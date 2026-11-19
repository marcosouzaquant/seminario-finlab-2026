"""Etapa 2: trata os brutos, gera dados/tratados/*.csv e o relatório de validação.

Uso:  .venv/Scripts/python src/02_tratar_validar.py [--corte AAAA-MM-DD]

Regras: nada é preenchido artificialmente; observações posteriores ao corte são
descartadas; toda divergência é listada no relatório, não apagada.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import zipfile

import numpy as np
import pandas as pd

import comum as C

LIMIAR_RETORNO_EXTREMO = 0.10
LIMIAR_FATOR = 0.0005      # variação do fator de ajuste considerada evento
LIMIAR_RAZAO_SPLIT = 0.005  # divergência B3 × Yahoo (fechamento) tolerada
JANELA_ESTIMACAO = (-160, -21)
MIN_RETORNOS_ESTIMACAO = 120


# =========================================================================== leitura
def ler_cotahist(corte: dt.date) -> pd.DataFrame:
    alvo = set(C.ACOES) | set(C.ALIAS_TICKER)
    linhas = []
    for arq in sorted((C.BRUTOS / "b3_cotahist").glob("COTAHIST_A*.ZIP")):
        with zipfile.ZipFile(arq) as z:
            with z.open(z.namelist()[0]) as f:
                for b in f:
                    s = b.decode("latin-1")
                    if s[:2] != "01" or s[10:12] != "02" or s[24:27] != "010":
                        continue
                    cod = s[12:24].strip()
                    if cod not in alvo:
                        continue
                    cod = C.ALIAS_TICKER.get(cod, cod)
                    fat = int(s[210:217])
                    p = lambda a, b_: int(s[a:b_]) / 100 / fat
                    linhas.append({
                        "data": dt.date(int(s[2:6]), int(s[6:8]), int(s[8:10])), "ticker": cod,
                        "abertura": p(56, 69), "maxima": p(69, 82), "minima": p(82, 95), "fechamento": p(108, 121),
                        "negocios": int(s[147:152]), "quantidade": int(s[152:170]), "volume_financeiro": int(s[170:188]) / 100,
                        "fatcot": fat, "arquivo": arq.name,
                    })
    df = pd.DataFrame(linhas)
    df["data"] = pd.to_datetime(df["data"])
    return df[df["data"] <= pd.Timestamp(corte)]


def ler_yahoo(nome: str) -> pd.DataFrame:
    df = pd.read_csv(C.BRUTOS / "yahoo" / f"{nome}.csv", parse_dates=["data"])
    df["data"] = df["data"].dt.tz_localize(None).dt.normalize() if df["data"].dt.tz is not None else df["data"]
    return df


def ler_indice_b3(indice: str) -> pd.DataFrame:
    regs = []
    for arq in sorted((C.BRUTOS / "b3_indices").glob(f"{indice}_*.json")):
        ano = int(arq.stem.split("_")[1])
        for linha in json.loads(arq.read_text(encoding="utf-8"))["results"]:
            for mes in range(1, 13):
                v = linha.get(f"rateValue{mes}")
                if v:
                    regs.append({"data": pd.Timestamp(ano, mes, linha["day"]), "indice": indice,
                                 "fechamento_pontos": float(v.replace(".", "").replace(",", "."))})
    return pd.DataFrame(regs).sort_values("data")


# =========================================================================== tratamento
def tratar_acoes(b3: pd.DataFrame):
    saida, eventos, achados, divergencias, conferencia_anual = [], [], [], [], []
    manuais = pd.read_csv(C.MANUAIS / "eventos_corporativos_manuais.csv", dtype={"valor_rs": float})
    for t in C.ACOES:
        y = ler_yahoo(t)
        x = b3[b3["ticker"] == t].merge(
            y[["data", "Close", "Adj Close", "Dividends", "Stock Splits"]], on="data", how="left")
        x = x.sort_values("data").reset_index(drop=True)
        sem_yahoo = x["Adj Close"].isna().sum()
        if sem_yahoo:
            achados.append(f"{t}: {sem_yahoo} pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): "
                           + ", ".join(x.loc[x['Adj Close'].isna(), 'data'].dt.strftime('%Y-%m-%d').head(10)))
        # ----- Ajuste a partir dos EVENTOS (preços sempre da B3; do Yahoo só vêm proventos e desdobramentos).
        # Eventos em datas sem pregão na B3 (raro) são deslocados para o pregão seguinte.
        ev = y.loc[(y["Dividends"].fillna(0) > 0) | (y["Stock Splits"].fillna(0) != 0), ["data", "Dividends", "Stock Splits"]]
        ev = ev[ev["data"] > x["data"].min()]
        pos = x["data"].searchsorted(ev["data"])
        ev = ev.assign(pos=pos)[pos < len(x)]
        k = pd.Series(1.0, index=x.index)          # desdobramento: novas ações por ação antiga
        d_y = pd.Series(0.0, index=x.index)        # provento na escala do Yahoo (ajustada a desdobramentos posteriores)
        for e in ev.itertuples():
            if e._3 and e._3 != 0:
                k.iloc[e.pos] *= e._3
            d_y.iloc[e.pos] += e.Dividends
        # s_depois usa só os desdobramentos que o Yahoo conhece: é a escala em que ele publica os proventos
        s_depois = k[::-1].cumprod()[::-1].shift(-1, fill_value=1.0)  # desdobramentos estritamente posteriores
        man = manuais[manuais["ticker"] == t]
        for m_ in man[man["acao"] == "desdobramento_manual"].itertuples():
            idx = x.index[x["data"] == pd.Timestamp(m_.data_ex)]
            k.loc[idx] *= float(m_.valor_rs)  # valor_rs = fator (novas ações por ação antiga); ausente no Yahoo
        d_bruto = d_y * s_depois                                       # provento em R$ por ação da época
        # Eventos manuais (dados/manuais/eventos_corporativos_manuais.csv)
        x["retorno_valido"] = True
        for m_ in man.itertuples():
            idx = x.index[x["data"] == pd.Timestamp(m_.data_ex)]
            if idx.empty:
                achados.append(f"{t} {m_.data_ex}: evento manual em data sem pregão na base")
                continue
            if m_.acao == "excluir_retorno":
                x.loc[idx, "retorno_valido"] = False
            elif m_.acao == "provento_manual":
                d_bruto.loc[idx] += float(m_.valor_rs)
            elif m_.acao == "desdobramento_manual":
                pass  # já aplicado acima
            elif m_.acao == "a_confirmar":
                achados.append(f"{t} {m_.data_ex}: {m_.tipo_evento} — PENDENTE ({m_.observacao})")
        p_ant = x["fechamento"].shift()
        mult = (1 - d_bruto / p_ant).fillna(1.0) / k                   # multiplicador do evento (convenção CRSP/Yahoo)
        x["fator_ajuste"] = mult[::-1].cumprod()[::-1].shift(-1, fill_value=1.0)
        for c in ("abertura", "maxima", "minima", "fechamento"):
            x[f"{c}_ajustado"] = x[c] * x["fator_ajuste"]
        provento_pct = (d_bruto / p_ant)[d_bruto > 0]
        for i_, v in provento_pct[provento_pct > 0.15].items():
            achados.append(f"{t} {x.data[i_]:%Y-%m-%d}: provento de {v:.1%} do preço — conferir valor e escala no RI/B3")

        # ----- Conferências (vão para dados/metadados/divergencias_b3_yahoo.csv)
        split = k != 1
        dr = (x["fechamento"] / x["Close"]).pct_change().abs()
        div = x[(dr > LIMIAR_RAZAO_SPLIT) & ~split & ~split.shift(-1, fill_value=False)]
        divergencias.append(div.assign(ticker=t)[["data", "ticker", "fechamento", "Close"]].rename(
            columns={"fechamento": "fechamento_b3", "Close": "fechamento_yahoo"}))
        # Salto bruto sem evento: possível desdobramento/bonificação ausente no Yahoo
        r_bruto = x["fechamento"] / p_ant - 1
        for i_ in x.index[(r_bruto.abs() > 0.25) & ~split]:
            achados.append(f"{t} {x.data[i_]:%Y-%m-%d}: retorno bruto {r_bruto[i_]:+.1%} sem desdobramento registrado — conferir evento corporativo")
        # Retorno acumulado por ano: nosso ajuste × Adj Close do Yahoo
        comp = x.set_index("data")[["fechamento_ajustado", "Adj Close"]].dropna()
        anual = comp.groupby(comp.index.year).agg(["first", "last"])
        for ano, r in anual.iterrows():
            ra = r[("fechamento_ajustado", "last")] / r[("fechamento_ajustado", "first")] - 1
            ry = r[("Adj Close", "last")] / r[("Adj Close", "first")] - 1
            conferencia_anual.append({"ticker": t, "ano": ano, "retorno_base": ra, "retorno_yahoo": ry, "diferenca_pp": 100 * (ra - ry)})
        for e in ev.itertuples():
            data_b3 = x.data.iloc[e.pos].date()
            if e.Dividends > 0:
                eventos.append({"ticker": t, "tipo_evento": "provento (dividendo/JCP)", "data_ex": data_b3,
                                "valor_ou_fator": e.Dividends, "valor_bruto_rs": d_bruto.iloc[e.pos],
                                "pct_preco_anterior": d_bruto.iloc[e.pos] / p_ant.iloc[e.pos],
                                "convencao": "valor_ou_fator na escala do Yahoo; valor_bruto_rs em R$ por ação da época", "fonte_id": f"YAHOO_{t}"})
            if e._3 and e._3 != 0:
                eventos.append({"ticker": t, "tipo_evento": "desdobramento/grupamento/bonificação", "data_ex": data_b3,
                                "valor_ou_fator": e._3, "convencao": "novas ações por ação antiga", "fonte_id": f"YAHOO_{t}"})
        x["fonte_id"] = "B3_COTAHIST"
        x["ajuste_id"] = f"YAHOO_{t}"
        saida.append(x)
    cols = ["data", "ticker", "abertura", "maxima", "minima", "fechamento", "abertura_ajustado", "maxima_ajustado",
            "minima_ajustado", "fechamento_ajustado", "fator_ajuste", "retorno_valido", "negocios", "quantidade", "volume_financeiro",
            "fonte_id", "ajuste_id"]
    return (pd.concat(saida)[cols], pd.DataFrame(eventos), achados,
            pd.concat(divergencias), pd.DataFrame(conferencia_anual))


def tratar_bcb(corte: dt.date) -> dict[str, pd.DataFrame]:
    out = {}
    for cod, nome in C.SGS_SERIES.items():
        d = pd.DataFrame(json.loads((C.BRUTOS / "bcb_sgs" / f"sgs_{cod}_{nome}.json").read_text(encoding="utf-8")))
        d["data"] = pd.to_datetime(d["data"], format="%d/%m/%Y")
        d["valor"] = d["valor"].astype(float)
        out[nome] = d.drop_duplicates("data")[lambda z: z["data"] <= pd.Timestamp(corte)]
    p = pd.DataFrame(json.loads((C.BRUTOS / "bcb_ptax" / "ptax_dolar.json").read_text(encoding="utf-8"))["value"])
    p["data"] = pd.to_datetime(p["dataHoraCotacao"]).dt.normalize()
    p = p.sort_values("dataHoraCotacao").groupby("data", as_index=False).last()
    out["ptax"] = p.rename(columns={"cotacaoCompra": "ptax_compra", "cotacaoVenda": "ptax_venda"})[
        ["data", "ptax_compra", "ptax_venda"]][lambda z: z["data"] <= pd.Timestamp(corte)]
    f = pd.concat([pd.DataFrame(json.loads((C.BRUTOS / "bcb_focus" / f"focus_anuais_{h}.json").read_text(encoding="utf-8")))
                   for h in C.FOCUS_JANELAS])
    f = f.rename(columns={"Data": "data", "Indicador": "indicador", "DataReferencia": "horizonte", "Media": "media", "Mediana": "mediana",
                          "DesvioPadrao": "desvio_padrao", "Minimo": "minimo", "Maximo": "maximo",
                          "numeroRespondentes": "n_respondentes", "baseCalculo": "base_calculo"})
    f["data"] = pd.to_datetime(f["data"])
    out["focus"] = f.drop(columns=["IndicadorDetalhe"])[lambda z: z["data"] <= pd.Timestamp(corte)]
    return out


def tratar_tesouro(corte: dt.date) -> pd.DataFrame:
    """Taxas a prazo constante (interpolação linear na taxa, prazo em anos corridos/365,25), sem extrapolar.

    Prefixado = 'Tesouro Prefixado' (LTN, sem cupom); real = 'Tesouro IPCA+' (NTN-B Principal, sem cupom).
    Taxa de venda da manhã. Inflação implícita = (1 + pre) / (1 + real) - 1 no mesmo prazo.
    """
    d = pd.read_csv(C.BRUTOS / "tesouro" / "PrecoTaxaTesouroDireto.csv", sep=";", decimal=",")
    d["data"] = pd.to_datetime(d["Data Base"], dayfirst=True)
    d["venc"] = pd.to_datetime(d["Data Vencimento"], dayfirst=True)
    d = d[(d["data"] >= pd.Timestamp(C.DATA_INICIO)) & (d["data"] <= pd.Timestamp(corte))]
    d["tau"] = (d["venc"] - d["data"]).dt.days / 365.25
    vertices = {"Tesouro Prefixado": ("pre", [1, 2, 3]), "Tesouro IPCA+": ("real", [3, 5])}
    linhas = {}
    for tipo, (pref, taus) in vertices.items():
        g = d[(d["Tipo Titulo"] == tipo) & d["Taxa Venda Manha"].gt(0)]
        for data_, x in g.groupby("data"):
            x = x.sort_values("tau")
            reg = linhas.setdefault(data_, {})
            for t in taus:
                ok_ = x["tau"].min() <= t <= x["tau"].max()
                reg[f"{pref}_{t}a"] = float(np.interp(t, x["tau"], x["Taxa Venda Manha"])) if ok_ else np.nan
    out = pd.DataFrame.from_dict(linhas, orient="index").sort_index()
    out.index.name = "data"
    out["implicita_3a"] = ((1 + out["pre_3a"] / 100) / (1 + out["real_3a"] / 100) - 1) * 100
    out["fonte_id"] = "TESOURO_TD"
    return out.reset_index()


def tratar_mt5(corte: dt.date, pregoes: pd.DatetimeIndex) -> pd.DataFrame | None:
    """DI futuro (taxa % a.a.) e dólar futuro contínuo, a partir de dados/brutos/mt5 (se existir)."""
    pasta = C.BRUTOS / "mt5"
    if not pasta.exists():
        return None
    partes = []
    for arq in sorted(pasta.glob("*.csv")):
        d = pd.read_csv(arq, parse_dates=["data"])
        d = d[d["data"] <= pd.Timestamp(corte)].sort_values("data")
        ativo = arq.stem.replace("_cont", "$")
        dol = ativo.startswith("DOL")
        d["retorno_valido"] = True
        if dol:
            # Série contínua troca de contrato no último pregão do mês (vencimento no 1º dia útil seguinte):
            # a variação desse dia mistura câmbio e pontos a termo, logo é marcada como inválida.
            ultimo_mes = d.groupby(d["data"].dt.to_period("M"))["data"].transform("max")
            d.loc[d["data"] == ultimo_mes, "retorno_valido"] = False
            d.loc[d["data"] == d["data"].max(), "retorno_valido"] = True  # último dado da base não é, por si, rolagem
        partes.append(pd.DataFrame({
            "data": d["data"], "ativo": ativo, "abertura": d["open"], "maxima": d["high"], "minima": d["low"],
            "fechamento": d["close"], "contratos": d["real_volume"], "unidade": "R$ por US$ 1.000" if dol else "% ao ano",
            "retorno_valido": d["retorno_valido"], "fonte_id": f"MT5_{arq.stem}",
        }))
    return pd.concat(partes)


def calendario_cvm(cal_manual: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Datas de entrega do ITR do 3º trimestre (1ª versão) na CVM, para os anos eleitorais.

    Anos já cobertos no calendário manual (2026) servem só de conferência. A CVM não informa o horário;
    presume-se divulgação após o fechamento (padrão das 10 empresas em 2026).
    """
    import zipfile
    linhas, conferencia = [], []
    for ano in C.ANOS_ELEICAO:
        with zipfile.ZipFile(C.BRUTOS / "cvm_itr" / f"itr_cia_aberta_{ano}.zip") as z:
            d = pd.read_csv(z.open(f"itr_cia_aberta_{ano}.csv"), sep=";", encoding="latin-1")
        q3 = d[d["DT_REFER"].str.endswith("09-30") & (d["VERSAO"] == 1)]
        for t, nome in C.CVM_EMPRESAS.items():
            nomes = nome if isinstance(nome, tuple) else (nome,)
            m = q3[q3["DENOM_CIA"].str.upper().str.contains("|".join(nomes), regex=True)]
            if m.empty:
                conferencia.append(f"{t} {ano}: ITR 3T não encontrado na CVM")
                continue
            data_ = m["DT_RECEB"].min()
            if ano == 2026:
                man = cal_manual[(cal_manual["categoria"] == "balanco") & cal_manual["observacao"].str.contains(f"afeta {t}", na=False)
                                 & cal_manual["evento"].str.contains("resultado", case=False)]
                datas_man = set(man["data"])
                conferencia.append(f"{t} 2026: CVM {data_} × imprensa {', '.join(sorted(datas_man)) or '—'}"
                                   + (" (igual)" if data_ in datas_man else " (DIFERENTE)"))
                continue
            obs = f"Data de entrega do ITR à CVM; horário não informado (presumido após o fechamento); afeta {t}"
            if data_ > f"{ano + 1}-01-01":
                obs += ". ATENÇÃO: entrega muito depois do trimestre; resultados podem ter sido comunicados antes por outro meio"
            linhas.append({"data": data_, "horario": "após o fechamento", "evento": f"{m['DENOM_CIA'].iloc[0].title()}: ITR 3T{str(ano)[2:]}",
                           "categoria": "balanco", "fonte_id": "CVM_ITR", "fonte_url": m["LINK_DOC"].iloc[0], "observacao": obs})
    return pd.DataFrame(linhas), conferencia


def adicionar_pregao_afetado(cal: pd.DataFrame, pregoes: pd.DatetimeIndex) -> pd.DataFrame:
    """Primeiro pregão em que a informação pôde ser negociada.

    Divulgação até 16:59 em dia de pregão -> o próprio dia; após o fechamento, à noite, ou em dia sem
    pregão (fim de semana, feriado) -> pregão seguinte.
    """
    afetados = []
    for r in cal.itertuples():
        d = pd.Timestamp(r.data)
        h = str(r.horario) if pd.notna(r.horario) else ""
        depois = h.startswith("após") or (h[:2].isdigit() and int(h[:2]) >= 17)
        mesmo_dia = d in pregoes and not depois and h != ""
        i = pregoes.searchsorted(d, side="left" if mesmo_dia else "right")
        afetados.append(pregoes[i].date() if i < len(pregoes) else pd.NaT)
    return cal.assign(pregao_afetado=afetados)


# =========================================================================== validação
def validar(acoes, indices, ibov_y, bcb, eventos_cal, achados_ajuste, diverg, anual, corte) -> tuple[list[tuple[str, str, str]], pd.DataFrame]:
    """Retorna lista (verificação, situação, detalhe) e tabela de janelas de estimação."""
    res = []
    ok = lambda cond: "OK" if cond else "ATENÇÃO"
    pregoes = pd.DatetimeIndex(sorted(indices.loc[indices["indice"] == "IBOV", "data"]))

    # 1. chaves únicas e datas ordenadas
    dup = acoes.duplicated(["data", "ticker"]).sum() + indices.duplicated(["data", "indice"]).sum()
    res.append(("Chaves únicas (data, ativo)", ok(dup == 0), f"{dup} duplicatas"))

    # 2. consistência OHLC e não negatividade
    inc = acoes[(acoes[["abertura", "maxima", "minima", "fechamento"]] <= 0).any(axis=1)
                | (acoes["minima"] > acoes[["abertura", "fechamento"]].min(axis=1) + 1e-9)
                | (acoes["maxima"] < acoes[["abertura", "fechamento"]].max(axis=1) - 1e-9)
                | (acoes["quantidade"] < 0) | (acoes["volume_financeiro"] < 0)]
    res.append(("Preços positivos; mínima ≤ abertura/fechamento ≤ máxima; volume ≥ 0", ok(inc.empty),
                f"{len(inc)} linhas inconsistentes" + ("" if inc.empty else ": " + inc[["data", "ticker"]].astype(str).agg(" ".join, axis=1).head(5).str.cat(sep="; "))))

    # 3. cobertura frente ao calendário de pregões (IBOV como calendário)
    det = []
    for t, g in acoes.groupby("ticker"):
        falt = pregoes[(pregoes >= g["data"].min()) & (pregoes <= g["data"].max())].difference(g["data"])
        extra = pd.DatetimeIndex(g["data"]).difference(pregoes)
        det.append(f"{t}: {len(g)} pregões, {g.data.min():%Y-%m-%d} a {g.data.max():%Y-%m-%d}, {len(falt)} faltantes"
                   + (f" ({', '.join(falt.strftime('%Y-%m-%d')[:5])})" if len(falt) else "")
                   + (f", {len(extra)} datas fora do calendário IBOV" if len(extra) else ""))
    total_falt = sum(int(s.split(", ")[2].split()[0]) for s in det)
    res.append(("Cobertura das ações vs. calendário de pregões", ok(total_falt == 0), " | ".join(det)))

    # 4. índices
    det = [f"{i}: {len(g)} obs., {g.data.min():%Y-%m-%d} a {g.data.max():%Y-%m-%d}" for i, g in indices.groupby("indice")]
    res.append(("Cobertura dos índices B3", "OK", " | ".join(det)))

    # 5. IBOV B3 × Yahoo
    m = indices[indices["indice"] == "IBOV"].merge(ibov_y[["data", "Close"]], on="data", how="inner")
    m["dif"] = (m["fechamento_pontos"] / m["Close"] - 1).abs()
    ruins = m[m["dif"] > 0.001]
    res.append(("Ibovespa: B3 (usado) × Yahoo (só conferência), tolerância 0,1%", "INFORMATIVO",
                f"{len(m)} datas comparadas; {len(ruins)} acima da tolerância; mediana da diferença {m['dif'].median():.4%}"
                + ("" if ruins.empty else ": " + ", ".join(f"{r.data:%Y-%m-%d} ({r.dif:.2%})" for r in ruins.head(8).itertuples()))))

    # 6. ajustes
    # Anos com evento manual (corrigido de propósito em relação ao Yahoo) ou com erro do Yahoo documentado
    man = pd.read_csv(C.MANUAIS / "eventos_corporativos_manuais.csv", parse_dates=["data_ex"])
    corrigidos = {(r.ticker, r.data_ex.year) for r in man.itertuples() if r.acao in ("provento_manual", "excluir_retorno", "desdobramento_manual")}
    # Erros do Yahoo documentados em decisoes_validacao.md (base conferida com B3/MT5)
    corrigidos |= {("ITUB4", 2013), ("MGLU3", 2024), ("TAEE11", 2015)}
    anual = anual.assign(explicado=[(t, a_) in corrigidos for t, a_ in zip(anual["ticker"], anual["ano"])])
    resto = anual[~anual["explicado"]]
    pior = resto.loc[resto["diferenca_pp"].abs().idxmax()]
    n_ruim = (resto["diferenca_pp"].abs() > 1.0).sum()
    res.append(("Ajuste por proventos: retorno anual da base × Adj Close do Yahoo (tolerância 1 p.p.)", ok(n_ruim == 0),
                f"{len(anual)} ações×ano; {anual['explicado'].sum()} com correção documentada "
                f"({', '.join(f'{t} {a_}' for t, a_ in sorted(corrigidos))}); demais: {n_ruim} acima da tolerância, "
                f"maior diferença {pior.ticker} {pior.ano}: {pior.diferenca_pp:+.2f} p.p. (dados/metadados/conferencia_ajuste_anual.csv)"))
    resolv = pd.read_csv(C.MANUAIS / "ocorrencias_resolvidas.csv")
    chaves = [f"{r.ticker} {r.data}" for r in resolv.itertuples()]
    pendentes = [x for x in achados_ajuste if "sem par no Yahoo" not in x and not any(c in x for c in chaves)]
    res.append(("Eventos corporativos a conferir (proventos > 15% do preço, saltos brutos sem desdobramento)",
                ok(not pendentes), f"{len(pendentes)} pendentes; {len(achados_ajuste) - len(pendentes)} resolvidas ou informativas "
                "(dados/manuais/ocorrencias_resolvidas.csv)"))
    res.append(("Fechamento Yahoo diverge do oficial B3 (> 0,5%) — Yahoo NÃO é usado para preços", "INFORMATIVO",
                f"{len(diverg)} pregões isolados (dados/metadados/divergencias_b3_yahoo.csv)"))

    # 7. retornos extremos
    a = acoes.sort_values(["ticker", "data"]).copy()
    a["ret"] = a.groupby("ticker")["fechamento_ajustado"].pct_change()
    a.loc[~a["retorno_valido"].astype(bool), "ret"] = np.nan  # eventos sem ajuste possível
    ext = a[a["ret"].abs() > LIMIAR_RETORNO_EXTREMO]
    res.append((f"Retornos extremos (|r| > {LIMIAR_RETORNO_EXTREMO:.0%}) sinalizados, não excluídos", "INFORMATIVO",
                f"{len(ext)}: " + "; ".join(f"{r.ticker} {r.data:%Y-%m-%d} {r.ret:+.1%}" for r in ext.itertuples())))

    # 8. BCB
    det = [f"{k}: {len(v)} obs., até {v.data.max():%Y-%m-%d}" for k, v in bcb.items()]
    fz = bcb["focus"].groupby(["horizonte", "indicador"]).size()
    res.append(("Séries BCB (CDI, Selic meta, PTAX, Focus)", ok(all(len(v) for v in bcb.values()) and len(fz) == len(C.FOCUS_INDICADORES) * len(C.FOCUS_JANELAS)),
                " | ".join(det) + " | Focus por horizonte×indicador: " + ", ".join(f"{h}/{i}={v}" for (h, i), v in fz.items())))

    # 9. sem dados após o corte
    pos = (acoes["data"] > pd.Timestamp(corte)).sum() + (indices["data"] > pd.Timestamp(corte)).sum()
    res.append(("Nenhuma observação após a data de corte", ok(pos == 0), f"corte = {corte}"))

    # 10. janelas de estimação por evento eleitoral
    linhas = []
    for e in eventos_cal[eventos_cal["categoria"] == "eleicao"].itertuples():
        d = pd.Timestamp(e.data)
        pos0 = pregoes.searchsorted(d, side="right")  # primeiro pregão após o domingo
        if pos0 >= len(pregoes):
            continue
        t0 = pregoes[pos0]
        ini, fim = pos0 + JANELA_ESTIMACAO[0], pos0 + JANELA_ESTIMACAO[1]
        for t in C.ACOES:
            g = a[(a["ticker"] == t) & a["data"].between(pregoes[max(ini, 0)], pregoes[fim])]
            n = g["ret"].notna().sum()
            no_evento = a[(a["ticker"] == t) & (a["data"] == t0)]
            linhas.append({"evento": e.evento, "t0": t0.date(), "ticker": t, "retornos_estimacao": int(n),
                           "pregao_t0_presente": not no_evento.empty})
    jan = pd.DataFrame(linhas)
    falha = jan[(jan["retornos_estimacao"] < MIN_RETORNOS_ESTIMACAO) | ~jan["pregao_t0_presente"]]
    res.append((f"Janela de estimação {JANELA_ESTIMACAO} com ≥ {MIN_RETORNOS_ESTIMACAO} retornos e t0 presente, em todas as eleições",
                ok(falha.empty), f"{len(jan)} combinações evento×ação; {len(falha)} com problema"))
    return res, jan


def amostra_manual(acoes, indices, corte) -> pd.DataFrame:
    datas = [pd.Timestamp("2026-10-23"), pd.Timestamp("2026-10-26"), pd.Timestamp("2026-10-27"),
             acoes["data"].max()]
    a = acoes[acoes["data"].isin(datas)][["data", "ticker", "abertura", "fechamento", "fechamento_ajustado", "volume_financeiro"]]
    i = indices[(indices["indice"] == "IBOV") & indices["data"].isin(datas)].rename(
        columns={"indice": "ticker", "fechamento_pontos": "fechamento"})
    out = pd.concat([a, i.drop(columns=["fonte_id"], errors="ignore")]).sort_values(["data", "ticker"])
    out["data"] = out["data"].dt.strftime("%Y-%m-%d")
    return out


# =========================================================================== saída
def sha256(p) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dicionario() -> pd.DataFrame:
    linhas = [
        ("acoes_diarias.csv", "data", "data", "", "Data do pregão (AAAA-MM-DD)"),
        ("acoes_diarias.csv", "ticker", "texto", "", "Código de negociação B3"),
        ("acoes_diarias.csv", "abertura/maxima/minima/fechamento", "decimal", "R$ por ação", "Preços brutos B3 (sem ajuste), divididos por FATCOT"),
        ("acoes_diarias.csv", "*_ajustado", "decimal", "R$ por ação", "Preço bruto × fator_ajuste; usar para retornos"),
        ("acoes_diarias.csv", "fator_ajuste", "decimal", "adimensional", "Adj Close (Yahoo) ÷ fechamento B3; muda só em datas ex"),
        ("acoes_diarias.csv", "retorno_valido", "booleano", "", "False = retorno do pregão contaminado por evento corporativo sem ajuste possível (ver eventos_corporativos_manuais.csv); excluir das análises"),
        ("acoes_diarias.csv", "negocios", "inteiro", "nº de negócios", "TOTNEG do COTAHIST"),
        ("acoes_diarias.csv", "quantidade", "inteiro", "nº de ações", "QUATOT do COTAHIST"),
        ("acoes_diarias.csv", "volume_financeiro", "decimal", "R$", "VOLTOT do COTAHIST"),
        ("indices_diarios.csv", "fechamento_pontos", "decimal", "pontos", "Fechamento diário do índice (B3); IBOV, IMOB, SMLL, IFNC são de retorno total"),
        ("eventos_corporativos.csv", "valor_ou_fator", "decimal", "R$/ação ou razão", "Proventos e desdobramentos segundo o Yahoo"),
        ("cdi_diario.csv", "valor", "decimal", "% ao dia", "SGS 12; dividir por 100 para decimal"),
        ("selic_meta.csv", "valor", "decimal", "% ao ano", "SGS 432"),
        ("ptax.csv", "ptax_compra/ptax_venda", "decimal", "R$/US$", "PTAX de fechamento (último boletim do dia)"),
        ("focus.csv", "media/mediana/desvio_padrao/minimo/maximo", "decimal", "unidade do indicador", "Estatísticas diárias do Focus; horizonte = ano seguinte a cada eleição (2015, 2019, 2023, 2027), coletado no ano eleitoral"),
        ("juros_tesouro.csv", "pre_1a/pre_2a/pre_3a", "decimal", "% ao ano", "Tesouro Prefixado (LTN) interpolado a prazo constante; taxa de venda da manhã; NaN fora do intervalo de vencimentos"),
        ("juros_tesouro.csv", "real_3a/real_5a", "decimal", "% ao ano", "Tesouro IPCA+ (NTN-B Principal) interpolado; juro real"),
        ("juros_tesouro.csv", "implicita_3a", "decimal", "% ao ano", "Inflação implícita de 3 anos = (1+pre)/(1+real)-1"),
        ("focus.csv", "base_calculo", "inteiro", "", "Base de cálculo do BCB (conferir definição na documentação oficial). Só a base 0 existe nas 4 eleições: usar base 0 nas comparações"),
        ("controles_externos.csv", "sp500/vix/brent", "decimal", "pontos / US$", "Fechamento Yahoo; fusos e feriados diferentes da B3"),
        ("calendario_pregoes.csv", "data", "data", "", "Datas com fechamento do IBOV na B3"),
        ("calendario_eventos.csv", "pregao_afetado", "data", "", "Primeiro pregão em que a informação pôde ser negociada (divulgação após 17h ou em dia sem pregão -> pregão seguinte)"),
        ("calendario_eventos.csv", "categoria", "texto", "", "eleicao, copom, fomc, ipca, ipca15, balanco"),
        ("futuros_diarios.csv", "ativo", "texto", "", "DI1F27, DI1F28, DI1F29, DI1F31, DI1F33 (DI futuro) e DOL$N (dólar futuro contínuo); desde nov/2021"),
        ("futuros_diarios.csv", "abertura/maxima/minima/fechamento", "decimal", "% ao ano (DI1) / R$ por US$ 1.000 (DOL)", "Barra diária MT5 (último negócio, não ajuste da B3). Para DI usar variação em pontos-base, não retorno"),
        ("futuros_diarios.csv", "contratos", "inteiro", "nº de contratos", "Volume em contratos"),
        ("futuros_diarios.csv", "retorno_valido", "booleano", "", "DOL$N: False no último pregão do mês (troca de contrato na série contínua)"),
    ]
    return pd.DataFrame(linhas, columns=["arquivo", "campo", "tipo", "unidade", "descricao"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", default=str(min(dt.date.today(), C.DATA_CORTE_FINAL)))
    corte = dt.date.fromisoformat(ap.parse_args().corte)

    b3 = ler_cotahist(corte)
    acoes, eventos_corp, achados, diverg, anual = tratar_acoes(b3)
    diverg.to_csv(C.METADADOS / "divergencias_b3_yahoo.csv", index=False, encoding="utf-8", date_format="%Y-%m-%d")
    anual.to_csv(C.METADADOS / "conferencia_ajuste_anual.csv", index=False, encoding="utf-8", float_format="%.6f")
    indices = pd.concat([ler_indice_b3(i) for i in C.INDICES_B3])
    indices = indices[indices["data"] <= pd.Timestamp(corte)]
    indices["fonte_id"] = "B3_INDICE_" + indices["indice"]
    ibov_y = ler_yahoo("ibov_yahoo")
    bcb = tratar_bcb(corte)
    controles = None
    for tk, nome in C.CONTROLES_YAHOO.items():
        y = ler_yahoo(nome)[["data", "Close"]].rename(columns={"Close": nome})
        controles = y if controles is None else controles.merge(y, on="data", how="outer")
    controles = controles[controles["data"].between(pd.Timestamp(C.DATA_INICIO), pd.Timestamp(corte))].sort_values("data")
    cal = pd.read_csv(C.MANUAIS / "calendario_eventos.csv")
    cal_cvm, conf_cvm = calendario_cvm(cal)
    cal = pd.concat([cal, cal_cvm], ignore_index=True).sort_values(["data", "categoria"]).reset_index(drop=True)
    cal = adicionar_pregao_afetado(cal, pd.DatetimeIndex(sorted(indices.loc[indices["indice"] == "IBOV", "data"])))

    # Última data comum a todas as séries centrais
    ultima_comum = min(acoes.groupby("ticker")["data"].max().min(), indices.groupby("indice")["data"].max().min())

    validacoes_cvm = ("Balanços: data de entrega à CVM × calendário da imprensa (2026)",
                      "OK" if not any("DIFERENTE" in c or "não encontrado" in c for c in conf_cvm) else "ATENÇÃO", " / ".join(conf_cvm))
    validacoes, janelas = validar(acoes, indices, ibov_y, bcb, cal, achados, diverg, anual, corte)

    validacoes.append(validacoes_cvm)
    pregoes = pd.DatetimeIndex(sorted(indices.loc[indices["indice"] == "IBOV", "data"]))
    tesouro = tratar_tesouro(corte)
    tesouro.to_csv(C.TRATADOS / "juros_tesouro.csv", index=False, encoding="utf-8", date_format="%Y-%m-%d", float_format="%.4f")
    det = []
    for e in cal[cal["categoria"] == "eleicao"].itertuples():
        t0 = pd.Timestamp(e.pregao_afetado)
        jan = tesouro[tesouro["data"].between(t0 - pd.Timedelta(days=45), t0 + pd.Timedelta(days=10))]
        det.append(f"{e.evento[:16]}: " + ", ".join(f"{c}={jan[c].notna().mean():.0%}" for c in ("pre_2a", "pre_3a", "real_3a", "implicita_3a")))
    falta_t0 = [e.evento for e in cal[cal["categoria"] == "eleicao"].itertuples()
                if not (tesouro["data"] == pd.Timestamp(e.pregao_afetado)).any()]
    validacoes.append(("Tesouro: cobertura dos vértices em [t0−45d, t0+10d] por turno", "INFORMATIVO" if not falta_t0 else "ATENÇÃO",
                       (f"sem dado no t0: {falta_t0}; " if falta_t0 else "t0 presente em todos os turnos; ") + " / ".join(det)))
    futuros = tratar_mt5(corte, pregoes)
    if futuros is not None:
        det, problemas = [], 0
        for at, g in futuros.groupby("ativo"):
            falt = pregoes[(pregoes >= g["data"].min()) & (pregoes <= g["data"].max())].difference(g["data"])
            inc = ((g["minima"] > g[["abertura", "fechamento"]].min(axis=1) + 1e-9) |
                   (g["maxima"] < g[["abertura", "fechamento"]].max(axis=1) - 1e-9)).sum()
            problemas += len(falt) + inc
            det.append(f"{at}: {len(g)} pregões desde {g.data.min():%Y-%m-%d}, {len(falt)} faltantes"
                       + (f" ({', '.join(falt.strftime('%Y-%m-%d')[:4])})" if len(falt) else "") + f", {inc} OHLC inconsistentes"
                       + (f", {(~g.retorno_valido).sum()} dias de rolagem" if at.startswith("DOL") else ""))
        situacao = "OK" if problemas == 0 else ("INFORMATIVO" if problemas <= 5 else "ATENÇÃO")  # vértices longos podem não ter negócio no dia
        validacoes.append(("Futuros MT5 (DI1, DOL): cobertura e OHLC (dias sem negócio não são preenchidos)", situacao, " / ".join(det)))
        futuros.to_csv(C.TRATADOS / "futuros_diarios.csv", index=False, encoding="utf-8", date_format="%Y-%m-%d")

    # ----- grava tratados
    fmt = dict(index=False, encoding="utf-8", date_format="%Y-%m-%d")
    acoes.sort_values(["ticker", "data"]).to_csv(C.TRATADOS / "acoes_diarias.csv", float_format="%.6f", **fmt)
    indices.sort_values(["indice", "data"]).to_csv(C.TRATADOS / "indices_diarios.csv", **fmt)
    eventos_corp.to_csv(C.TRATADOS / "eventos_corporativos.csv", **fmt)
    for nome in ("cdi_diario", "selic_meta", "ptax", "focus"):
        bcb[nome].to_csv(C.TRATADOS / f"{nome}.csv", **fmt)
    controles.to_csv(C.TRATADOS / "controles_externos.csv", **fmt)
    pd.DataFrame({"data": sorted(indices.loc[indices.indice == "IBOV", "data"])}).to_csv(C.TRATADOS / "calendario_pregoes.csv", **fmt)
    cal.to_csv(C.TRATADOS / "calendario_eventos.csv", index=False, encoding="utf-8")
    janelas.to_csv(C.METADADOS / "janelas_estimacao.csv", index=False, encoding="utf-8")
    dicionario().to_csv(C.METADADOS / "dicionario_dados.csv", index=False, encoding="utf-8")

    gerado = C.agora_iso()
    man = [{"arquivo": f"dados/tratados/{p.name}", "versao": f"corte_{corte}", "sha256": sha256(p), "gerado_em": gerado}
           for p in sorted(C.TRATADOS.glob("*.csv"))]
    pd.DataFrame(man).to_csv(C.METADADOS / "manifesto_arquivos.csv", index=False, encoding="utf-8")

    # ----- relatório
    amostra = amostra_manual(acoes, indices, corte)
    L = [f"# Relatório de validação da base — corte {corte}", "",
         f"Gerado automaticamente em {gerado} por `src/02_tratar_validar.py`.",
         f"Última data comum às séries centrais: **{ultima_comum:%Y-%m-%d}**.", "",
         "> A situação final (aprovada / aprovada com restrição / pendente) é decidida pelo grupo, depois de",
         "> revisar as ATENÇÕES abaixo e conferir a amostra manual no site da B3.", "",
         "## Verificações automáticas", "", "| Verificação | Situação | Detalhe |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c.replace('|', '/')} |" for a, b, c in validacoes]
    L += ["", "## Eventos corporativos e ocorrências a investigar",
          "", "Decisões já tomadas sobre estas ocorrências: `dados/metadados/decisoes_validacao.md`.", ""]
    L += [f"- {x}" for x in achados] or ["- Nenhuma."]
    L += ["", "## Janelas de estimação por eleição", "", janelas.to_markdown(index=False), "",
          "## Amostra para conferência manual no site da B3", "",
          amostra.to_markdown(index=False, floatfmt=".2f"), "",
          "## Itens que dependem do grupo", "",
          "- [ ] Conferir a amostra acima contra a B3 (cotações históricas / página do índice)",
          "- [ ] Investigar cada ocorrência da seção de ajustes e registrar a decisão",
          "- [ ] Conferir no site do Fed as datas do FOMC marcadas como \"de memória\" em dados/manuais/calendario_eventos.csv (2014-09, 2018-11, 2022-09)",
          "- [ ] Conferir no RI os horários dos balanços marcados \"a conferir\" (relatório de produção da Petrobras, resultado do BB)",
          "- [ ] Definir a situação da base e o responsável por cada pendência"]
    (C.METADADOS / "relatorio_validacao.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(f"{b:11s} {a}" for a, b, _ in validacoes))
    print(f"Última data comum: {ultima_comum:%Y-%m-%d}. Relatório: dados/metadados/relatorio_validacao.md")


if __name__ == "__main__":
    main()
