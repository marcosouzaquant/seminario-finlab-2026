"""Conferência independente: barras diárias do MT5 (corretora) × base tratada (B3).

Uso:  .venv/Scripts/python src/03_conferir_mt5.py
Requer o terminal MT5 aberto e conectado. Apenas leitura de dados de mercado.
O MT5 é fonte de conferência, não substitui a B3. Saída: dados/metadados/conferencia_mt5*.csv
"""
from __future__ import annotations

import datetime as dt

import MetaTrader5 as mt5
import pandas as pd

import comum as C

TOL = 0.001  # 0,1%


def barras(simbolo: str) -> pd.DataFrame:
    mt5.symbol_select(simbolo, True)
    r = mt5.copy_rates_range(simbolo, mt5.TIMEFRAME_D1, dt.datetime(C.ANO_INICIO, 1, 1), dt.datetime.now() + dt.timedelta(days=1))
    if r is None or len(r) == 0:
        raise RuntimeError(f"MT5 sem dados para {simbolo}: {mt5.last_error()}")
    df = pd.DataFrame(r)
    df["data"] = pd.to_datetime(df["time"], unit="s").dt.normalize()
    return df.rename(columns={"open": "abertura_mt5", "high": "maxima_mt5", "low": "minima_mt5",
                              "close": "fechamento_mt5", "real_volume": "quantidade_mt5"})


def main() -> None:
    if not mt5.initialize():
        raise SystemExit(f"MT5 não inicializou: {mt5.last_error()}")
    ti = mt5.terminal_info()
    acoes = pd.read_csv(C.TRATADOS / "acoes_diarias.csv", parse_dates=["data"])
    ibov = pd.read_csv(C.TRATADOS / "indices_diarios.csv", parse_dates=["data"]).query("indice == 'IBOV'")
    resumo, detalhes = [], []
    for s in C.ACOES + ["IBOV"]:
        m = barras(s)
        base = (ibov.rename(columns={"fechamento_pontos": "fechamento"}).assign(ticker="IBOV") if s == "IBOV"
                else acoes[acoes["ticker"] == s])
        j = base.merge(m, on="data", how="inner")
        if j.empty:
            continue
        for campo in (["fechamento"] if s == "IBOV" else ["abertura", "maxima", "minima", "fechamento"]):
            j[f"dif_{campo}"] = j[f"{campo}_mt5"] / j[campo] - 1
        j["dif_abs"] = j["dif_fechamento"].abs()
        # MT5 pode trazer série ajustada: razão constante por trechos indica ajuste, não erro
        j["razao"] = j["fechamento_mt5"] / j["fechamento"]
        # Retornos diários: comparáveis mesmo que o MT5 use outra convenção de ajuste.
        # Só pregões consecutivos nas duas fontes; exclui o pregão de hoje (barra parcial).
        j = j[j["data"] < pd.Timestamp(dt.date.today())].reset_index(drop=True)
        col_base = "fechamento" if s == "IBOV" else "fechamento_ajustado"
        j["ret_base"] = j[col_base].pct_change()
        j["ret_mt5"] = j["fechamento_mt5"].pct_change()
        j["dif_ret_pp"] = 100 * (j["ret_mt5"] - j["ret_base"])
        eventos = set(pd.read_csv(C.TRATADOS / "eventos_corporativos.csv", parse_dates=["data_ex"])
                      .query("ticker == @s")["data_ex"]) if s != "IBOV" else set()
        jr = j[~j["data"].isin(eventos)].dropna(subset=["dif_ret_pp"])
        ruins = j[j["dif_abs"] > TOL] if s == "IBOV" else jr[jr["dif_ret_pp"].abs() > 0.05]
        resumo.append({
            "ativo": s, "mt5_inicio": m["data"].min().date(), "mt5_fim": m["data"].max().date(), "pregoes_comparados": len(j),
            "fechamento_ate_0_1pct": f"{(j['dif_abs'] <= TOL).mean():.2%}", "fechamento_igual_centavo": f"{(j['dif_abs'] < 1e-6).mean():.2%}" if s == "IBOV"
            else f"{((j['fechamento_mt5'] - j['fechamento']).abs() < 0.005).mean():.2%}",
            "acima_tolerancia": len(ruins), "maior_dif": f"{j['dif_fechamento'].iloc[j['dif_abs'].values.argmax()]:+.3%}",
            "data_maior_dif": j["data"].iloc[j["dif_abs"].values.argmax()].date(),
            "razao_mediana": round(j["razao"].median(), 6),
            "ret_dif_ate_0_05pp_sem_evento": f"{(jr['dif_ret_pp'].abs() <= 0.05).mean():.2%}",
            "ret_maior_dif_pp_sem_evento": f"{jr['dif_ret_pp'].iloc[jr['dif_ret_pp'].abs().values.argmax()]:+.2f}",
            "ret_data_maior_dif": jr["data"].iloc[jr["dif_ret_pp"].abs().values.argmax()].date(),
        })
        detalhes.append(ruins.assign(ativo=s)[["data", "ativo", "fechamento", "fechamento_mt5", "dif_fechamento", "ret_base", "ret_mt5", "dif_ret_pp"]])
    mt5.shutdown()
    res = pd.DataFrame(resumo)
    res.to_csv(C.METADADOS / "conferencia_mt5_resumo.csv", index=False, encoding="utf-8")
    pd.concat(detalhes).to_csv(C.METADADOS / "conferencia_mt5_divergencias.csv", index=False, encoding="utf-8", date_format="%Y-%m-%d")
    C.registrar_fonte(fonte_id="MT5_CLEAR", instituicao=f"{ti.company} (terminal MetaTrader 5)", serie="Barras diárias D1: ações e IBOV",
                      url="terminal local MT5 (pacote MetaTrader5)", arquivo_original="não arquivado; resultado em dados/metadados/conferencia_mt5_*.csv",
                      inicio=str(C.ANO_INICIO), fim=str(dt.date.today()), unidade="R$ / pontos",
                      tratamento="Somente conferência da base B3; não usado como dado")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
