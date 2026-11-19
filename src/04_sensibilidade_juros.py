"""Sensibilidade de ações e índices aos juros, medida ANTES de cada eleição.

Uso:  .venv/Scripts/python src/04_sensibilidade_juros.py

A) Validação 2022–2025 (fora do ano eleitoral de 2026), duas medidas de juros:
   - DI1F29 (MT5, fechamento):          r_i = a + b_m r_IBOV + b_j ΔDI_t + e
   - Tesouro prefixado 2 anos (manhã):  r_i = a + b_m r_IBOV + c0 Δpre_t + c1 Δpre_t+1 + e,  b_j = c0 + c1
     A taxa do Tesouro é da manhã e o retorno da ação vai de fechamento a fechamento; somar Δ_t e Δ_t+1
     cobre o descasamento de horário (ajuste de Dimson, 1979).
B) Por eleição (2º turno de 2014, 2018, 2022 e 2026): mesmo modelo com o Tesouro na janela [t0-500, t0-21]
   pregões (em 2014 a base começa em jan/2013, então a janela fica mais curta).

ΔJuros em pontos-base; efeito = retorno (%) para +100 bp, além do mercado. Erros de Newey-West (5 defasagens).
Saídas: dados/metadados/sensibilidade_juros.csv e sensibilidade_juros_por_eleicao.csv
"""
from __future__ import annotations

import pandas as pd
import statsmodels.api as sm

import comum as C

VALID_INICIO, VALID_FIM = "2022-01-01", "2025-12-31"
JANELA = (-500, -21)


def carregar() -> pd.DataFrame:
    a = pd.read_csv(C.TRATADOS / "acoes_diarias.csv", parse_dates=["data"]).sort_values(["ticker", "data"])
    a["ret"] = a.groupby("ticker")["fechamento_ajustado"].pct_change()
    a.loc[~a["retorno_valido"].astype(bool), "ret"] = float("nan")
    r = a.pivot(index="data", columns="ticker", values="ret")
    ind = (pd.read_csv(C.TRATADOS / "indices_diarios.csv", parse_dates=["data"])
           .pivot(index="data", columns="indice", values="fechamento_pontos").pct_change())
    pregoes = ind.index
    tes = pd.read_csv(C.TRATADOS / "juros_tesouro.csv", parse_dates=["data"]).set_index("data")["pre_2a"]
    tes = tes.reindex(pregoes)  # só pregões da B3; Δ entre pregões consecutivos
    dpre = tes.diff() * 100
    base = pd.concat([r, ind, dpre.rename("dPRE"), dpre.shift(-1).rename("dPRE_seg")], axis=1)
    fut = pd.read_csv(C.TRATADOS / "futuros_diarios.csv", parse_dates=["data"])
    ddi = fut[fut["ativo"] == "DI1F29"].set_index("data")["fechamento"].diff() * 100
    return base.join(ddi.rename("dDI"))


def estimar(d: pd.DataFrame, ativo: str, juros: list[str]) -> dict:
    x = d[[ativo, "IBOV", *juros]].dropna()
    m = sm.OLS(x[ativo], sm.add_constant(x[["IBOV", *juros]])).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    b = sum(m.params[j] for j in juros)
    cov = m.cov_params().loc[juros, juros].values.sum()
    return {"n": int(m.nobs), "beta_mercado": m.params["IBOV"], "efeito_100bp_pct": 100 * 100 * b,
            "t_juros": b / cov ** 0.5, "r2": m.rsquared}


def grupo(ativo: str) -> str:
    return next((g for g, l in C.GRUPOS_JUROS.items() if ativo in l), "nucleo" if ativo in C.ACOES_NUCLEO else "indice")


def main() -> None:
    base = carregar()
    ativos = C.ACOES + [i for i in C.INDICES_B3 if i != "IBOV"]

    # A) validação 2022–2025
    v = base.loc[VALID_INICIO:VALID_FIM]
    linhas = []
    for at in ativos:
        di = estimar(v, at, ["dDI"])
        te = estimar(v, at, ["dPRE", "dPRE_seg"])
        linhas.append({"ativo": at, "grupo": grupo(at), "n": di["n"], "beta_mercado": di["beta_mercado"],
                       "efeito_100bp_DI1F29": di["efeito_100bp_pct"], "t_DI": di["t_juros"],
                       "efeito_100bp_tesouro2a": te["efeito_100bp_pct"], "t_tesouro": te["t_juros"], "r2_DI": di["r2"]})
    a = pd.DataFrame(linhas).sort_values("efeito_100bp_DI1F29")
    a.to_csv(C.METADADOS / "sensibilidade_juros.csv", index=False, encoding="utf-8", float_format="%.4f")
    corr = a[["efeito_100bp_DI1F29", "efeito_100bp_tesouro2a"]].corr().iloc[0, 1]
    print(f"A) {VALID_INICIO} a {VALID_FIM}: efeito de +100 bp (%), além do mercado")
    print(a.round(2).to_string(index=False))
    print(f"Correlação entre as duas medidas (entre ativos): {corr:.3f}\n")

    # B) por eleição (2º turno), com o Tesouro
    cal = pd.read_csv(C.TRATADOS / "calendario_eventos.csv", parse_dates=["pregao_afetado"])
    pregoes = base.index
    linhas = []
    for e in cal[(cal["categoria"] == "eleicao") & cal["evento"].str.contains("2º turno")].itertuples():
        i0 = pregoes.get_loc(e.pregao_afetado)
        jan = base.iloc[max(i0 + JANELA[0], 0): i0 + JANELA[1] + 1]
        for at in ativos:
            te = estimar(jan, at, ["dPRE", "dPRE_seg"])
            linhas.append({"eleicao": e.evento[9:13], "t0": e.pregao_afetado.date(), "inicio": jan.index[0].date(),
                           "fim": jan.index[-1].date(), "ativo": at, "grupo": grupo(at), **te})
    b = pd.DataFrame(linhas)
    b.to_csv(C.METADADOS / "sensibilidade_juros_por_eleicao.csv", index=False, encoding="utf-8", float_format="%.4f")
    print("B) Efeito de +100 bp no Tesouro prefixado 2 anos, janela [t0-500, t0-21] antes de cada 2º turno")
    print(b.pivot(index="ativo", columns="eleicao", values="efeito_100bp_pct").reindex(ativos).round(2).to_string())


if __name__ == "__main__":
    main()
