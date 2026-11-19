"""Etapa 1b (opcional, requer MT5): baixa DI futuro e dólar futuro do terminal MetaTrader 5.

Uso:  .venv/Scripts/python src/01b_coletar_mt5.py
Os CSVs brutos ficam em dados/brutos/mt5/ e vão para o repositório. Quem não tem MT5
usa esses arquivos, sem precisar rodar este script. Apenas leitura de cotações.

Limites do MT5 (corretora): só contratos não vencidos, histórico D1 desde ~nov/2021.
Cobre as eleições de 2022 e 2026; para 2014 e 2018 não há dados.
"""
from __future__ import annotations

import datetime as dt

import MetaTrader5 as mt5
import pandas as pd

import comum as C

# DI1: taxa em % a.a. (último negócio do dia, não o ajuste da B3).
# Vértices em 2026: F27 ≈ curto (Copom), F28 ≈ 1 ano, F29 ≈ 2 anos, F31 ≈ 4 anos, F33 ≈ 6 anos.
SIMBOLOS = {
    "DI1F27": "DI jan/2027", "DI1F28": "DI jan/2028", "DI1F29": "DI jan/2029",
    "DI1F31": "DI jan/2031", "DI1F33": "DI jan/2033",
    "DOL$N": "Dólar futuro cheio, série contínua sem ajuste (R$ por US$ 1.000)",
}


def main() -> None:
    if not mt5.initialize():
        raise SystemExit(f"MT5 não inicializou: {mt5.last_error()}")
    empresa = mt5.terminal_info().company
    pasta = C.BRUTOS / "mt5"
    pasta.mkdir(parents=True, exist_ok=True)
    fim = min(dt.date.today(), C.DATA_CORTE_FINAL)
    for s, desc in SIMBOLOS.items():
        mt5.symbol_select(s, True)
        r = mt5.copy_rates_range(s, mt5.TIMEFRAME_D1, dt.datetime(C.ANO_INICIO, 1, 1), dt.datetime.combine(fim, dt.time(23, 59)))
        if r is None or len(r) == 0:
            raise RuntimeError(f"MT5 sem dados para {s}: {mt5.last_error()}")
        df = pd.DataFrame(r)
        df.insert(0, "data", pd.to_datetime(df.pop("time"), unit="s").dt.date)
        df = df[df["data"] < dt.date.today()]  # descarta a barra parcial do dia corrente
        nome = s.replace("$", "_cont")
        df.to_csv(pasta / f"{nome}.csv", index=False)
        print(f"{s}: {len(df)} pregões, {df.data.min()} a {df.data.max()}")
        C.registrar_fonte(
            fonte_id=f"MT5_{nome}", instituicao=f"{empresa} (MetaTrader 5); contrato negociado na B3", serie=f"{s}: {desc}",
            url="terminal local MT5 (pacote MetaTrader5)", arquivo_original=f"dados/brutos/mt5/{nome}.csv",
            inicio=str(df.data.min()), fim=str(df.data.max()),
            unidade="% ao ano" if s.startswith("DI1") else "R$ por US$ 1.000",
            tratamento="Barra diária da corretora; último negócio, não preço de ajuste da B3",
        )
    mt5.shutdown()


if __name__ == "__main__":
    main()
