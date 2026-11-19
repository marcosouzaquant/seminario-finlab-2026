# Relatório de validação da base — corte 2026-11-19

Gerado automaticamente em 2026-11-19T17:04:34-03:00 por `src/02_tratar_validar.py`.
Última data comum às séries centrais: **2026-11-18**.

> A situação final (aprovada / aprovada com restrição / pendente) é decidida pelo grupo, depois de
> revisar as ATENÇÕES abaixo e conferir a amostra manual no site da B3.

## Verificações automáticas

| Verificação | Situação | Detalhe |
|---|---|---|
| Chaves únicas (data, ativo) | OK | 0 duplicatas |
| Preços positivos; mínima ≤ abertura/fechamento ≤ máxima; volume ≥ 0 | OK | 0 linhas inconsistentes |
| Cobertura das ações vs. calendário de pregões | OK | BBAS3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / CYRE3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / EGIE3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / ITUB4: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / LREN3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / MGLU3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / MRVE3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / PETR4: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / TAEE11: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes / VALE3: 3445 pregões, 2013-01-02 a 2026-11-18, 0 faltantes |
| Cobertura dos índices B3 | OK | IBOV: 3445 obs., 2013-01-02 a 2026-11-18 / ICON: 3445 obs., 2013-01-02 a 2026-11-18 / IFNC: 3445 obs., 2013-01-02 a 2026-11-18 / IMOB: 3445 obs., 2013-01-02 a 2026-11-18 / SMLL: 3445 obs., 2013-01-02 a 2026-11-18 / UTIL: 3445 obs., 2013-01-02 a 2026-11-18 |
| Ibovespa: B3 (usado) × Yahoo (só conferência), tolerância 0,1% | INFORMATIVO | 3444 datas comparadas; 95 acima da tolerância; mediana da diferença 0.0003%: 2013-12-19 (1.60%), 2014-11-28 (0.11%), 2018-02-28 (0.15%), 2019-11-04 (0.16%), 2019-11-05 (0.25%), 2019-11-11 (0.14%), 2019-11-13 (0.14%), 2019-11-19 (0.23%) |
| Ajuste por proventos: retorno anual da base × Adj Close do Yahoo (tolerância 1 p.p.) | OK | 140 ações×ano; 8 com correção documentada (BBAS3 2023, BBAS3 2024, CYRE3 2026, ITUB4 2013, ITUB4 2021, MGLU3 2024, MRVE3 2018, TAEE11 2015); demais: 0 acima da tolerância, maior diferença TAEE11 2022: +0.76 p.p. (dados/metadados/conferencia_ajuste_anual.csv) |
| Eventos corporativos a conferir (proventos > 15% do preço, saltos brutos sem desdobramento) | OK | 0 pendentes; 21 resolvidas ou informativas (dados/manuais/ocorrencias_resolvidas.csv) |
| Fechamento Yahoo diverge do oficial B3 (> 0,5%) — Yahoo NÃO é usado para preços | INFORMATIVO | 969 pregões isolados (dados/metadados/divergencias_b3_yahoo.csv) |
| Retornos extremos (|r| > 10%) sinalizados, não excluídos | INFORMATIVO | 233: BBAS3 2014-10-06 +11.9%; BBAS3 2014-10-13 +10.9%; BBAS3 2015-12-09 +10.1%; BBAS3 2016-03-03 +13.2%; BBAS3 2016-03-08 +10.9%; BBAS3 2016-03-15 -21.2%; BBAS3 2016-03-17 +14.4%; BBAS3 2016-04-08 +11.5%; BBAS3 2017-05-18 -19.9%; BBAS3 2018-10-02 +11.4%; BBAS3 2020-03-09 -11.0%; BBAS3 2020-03-12 -13.2%; BBAS3 2020-03-13 +16.8%; BBAS3 2020-03-16 -16.7%; BBAS3 2020-03-18 -16.5%; BBAS3 2020-03-23 -10.0%; BBAS3 2020-03-24 +17.1%; BBAS3 2020-03-25 +12.0%; BBAS3 2020-04-24 -13.4%; BBAS3 2020-04-28 +13.4%; BBAS3 2020-05-25 +10.5%; BBAS3 2021-02-22 -11.6%; BBAS3 2022-10-24 -10.0%; BBAS3 2025-05-16 -12.7%; BBAS3 2026-10-05 +11.0%; BBAS3 2026-10-26 -29.3%; CYRE3 2016-03-17 +10.1%; CYRE3 2017-05-18 -16.3%; CYRE3 2018-10-08 +11.7%; CYRE3 2020-03-09 -16.7%; CYRE3 2020-03-12 -24.7%; CYRE3 2020-03-13 +15.0%; CYRE3 2020-03-16 -19.0%; CYRE3 2020-03-18 -20.7%; CYRE3 2020-03-24 +18.1%; CYRE3 2020-03-26 +10.0%; CYRE3 2020-03-27 -11.8%; CYRE3 2020-04-24 -12.4%; CYRE3 2020-04-28 +12.7%; CYRE3 2020-05-21 +11.0%; CYRE3 2020-05-25 +12.4%; CYRE3 2020-06-03 +14.8%; CYRE3 2021-08-24 +12.3%; CYRE3 2022-08-04 +11.4%; CYRE3 2022-11-10 -11.7%; CYRE3 2026-10-05 +18.4%; CYRE3 2026-10-26 -44.8%; EGIE3 2026-10-26 -10.7%; ITUB4 2016-03-17 +10.9%; ITUB4 2017-05-18 -12.0%; ITUB4 2020-03-13 +11.1%; ITUB4 2026-10-05 +10.4%; ITUB4 2026-10-26 -13.7%; LREN3 2020-03-16 -21.1%; LREN3 2020-03-18 -17.0%; LREN3 2020-03-19 +15.0%; LREN3 2020-03-23 -12.8%; LREN3 2020-03-25 +11.5%; LREN3 2020-04-06 +12.2%; LREN3 2020-11-09 +14.5%; LREN3 2021-04-16 +11.9%; LREN3 2024-11-28 -10.2%; LREN3 2025-02-21 -14.0%; LREN3 2026-10-05 +15.4%; LREN3 2026-10-09 +11.6%; LREN3 2026-10-26 -33.6%; MGLU3 2013-08-07 +28.9%; MGLU3 2015-07-21 +14.1%; MGLU3 2015-07-23 +18.3%; MGLU3 2015-07-24 -12.7%; MGLU3 2015-07-31 +31.9%; MGLU3 2015-11-30 -11.7%; MGLU3 2015-12-15 +12.4%; MGLU3 2015-12-17 +15.5%; MGLU3 2015-12-28 +37.3%; MGLU3 2015-12-29 +10.8%; MGLU3 2016-01-07 -13.3%; MGLU3 2016-01-29 +10.1%; MGLU3 2016-02-12 +20.3%; MGLU3 2016-02-15 +13.9%; MGLU3 2016-02-17 -10.9%; MGLU3 2016-03-03 +13.8%; MGLU3 2016-04-27 +19.2%; MGLU3 2016-05-05 -11.1%; MGLU3 2016-05-06 +19.3%; MGLU3 2016-08-04 +12.6%; MGLU3 2016-10-25 -15.5%; MGLU3 2016-10-26 -16.3%; MGLU3 2016-10-27 +30.9%; MGLU3 2017-01-20 +11.6%; MGLU3 2017-03-16 +11.5%; MGLU3 2017-04-17 +10.3%; MGLU3 2017-05-05 +14.1%; MGLU3 2017-05-18 -16.2%; MGLU3 2017-05-22 -10.7%; MGLU3 2017-07-07 +10.1%; MGLU3 2017-08-31 +10.3%; MGLU3 2017-09-04 +10.2%; MGLU3 2017-09-12 -11.9%; MGLU3 2017-09-14 +13.4%; MGLU3 2017-10-18 +10.8%; MGLU3 2017-12-07 +10.5%; MGLU3 2018-05-08 +14.6%; MGLU3 2019-02-22 +10.4%; MGLU3 2020-03-09 -11.0%; MGLU3 2020-03-10 +16.4%; MGLU3 2020-03-12 -21.1%; MGLU3 2020-03-13 +23.5%; MGLU3 2020-03-16 -18.9%; MGLU3 2020-03-18 -19.0%; MGLU3 2020-03-24 +21.4%; MGLU3 2021-11-05 +12.3%; MGLU3 2021-11-09 +10.1%; MGLU3 2021-11-12 -18.3%; MGLU3 2021-11-16 -12.6%; MGLU3 2021-12-01 -11.8%; MGLU3 2021-12-08 -10.6%; MGLU3 2022-03-24 +10.0%; MGLU3 2022-05-05 -10.7%; MGLU3 2022-05-17 -11.5%; MGLU3 2022-07-05 +11.7%; MGLU3 2022-07-12 +11.4%; MGLU3 2022-07-20 +10.0%; MGLU3 2022-08-04 +14.0%; MGLU3 2022-08-12 +17.8%; MGLU3 2022-08-15 +12.8%; MGLU3 2022-09-30 +10.6%; MGLU3 2022-10-14 -11.2%; MGLU3 2022-11-10 -11.0%; MGLU3 2022-11-11 -13.1%; MGLU3 2022-12-19 +10.1%; MGLU3 2023-01-16 +12.2%; MGLU3 2023-03-01 -10.0%; MGLU3 2023-03-23 -13.4%; MGLU3 2023-04-11 +12.8%; MGLU3 2023-05-16 -22.8%; MGLU3 2023-11-03 +12.0%; MGLU3 2023-11-07 +23.8%; MGLU3 2023-11-16 +24.4%; MGLU3 2023-12-13 +11.0%; MGLU3 2024-06-24 +12.3%; MGLU3 2024-08-19 +10.7%; MGLU3 2024-11-04 +10.4%; MGLU3 2024-12-18 -10.0%; MGLU3 2025-01-27 +10.0%; MGLU3 2025-01-30 +12.6%; MGLU3 2025-03-07 +10.5%; MGLU3 2025-03-14 +13.5%; MGLU3 2025-04-08 -13.4%; MGLU3 2025-04-09 +11.3%; MGLU3 2025-04-24 +10.8%; MGLU3 2026-09-02 +16.9%; MGLU3 2026-09-30 +12.5%; MGLU3 2026-10-05 +24.2%; MGLU3 2026-10-09 +19.2%; MGLU3 2026-10-20 +14.8%; MGLU3 2026-10-26 -58.2%; MGLU3 2026-11-10 +11.6%; MGLU3 2026-11-11 +17.5%; MGLU3 2026-11-13 +10.5%; MRVE3 2013-06-13 +12.2%; MRVE3 2014-03-14 -12.5%; MRVE3 2020-03-09 -11.3%; MRVE3 2020-03-12 -20.2%; MRVE3 2020-03-13 +10.9%; MRVE3 2020-03-18 -20.1%; MRVE3 2020-03-23 -10.4%; MRVE3 2020-03-24 +16.1%; MRVE3 2020-04-01 -10.1%; MRVE3 2020-05-18 +13.8%; MRVE3 2020-05-25 +12.1%; MRVE3 2022-03-09 +10.9%; MRVE3 2022-03-11 -11.9%; MRVE3 2022-08-04 +12.7%; MRVE3 2022-08-11 -11.0%; MRVE3 2022-10-17 -11.4%; MRVE3 2023-05-25 +10.3%; MRVE3 2023-10-18 -10.1%; MRVE3 2024-01-11 -11.8%; MRVE3 2024-11-28 -14.1%; MRVE3 2025-05-09 -11.2%; MRVE3 2025-10-07 -12.1%; MRVE3 2026-08-13 +14.3%; MRVE3 2026-10-05 +11.4%; MRVE3 2026-10-09 +21.6%; MRVE3 2026-10-19 +10.9%; MRVE3 2026-10-26 -42.5%; MRVE3 2026-11-11 +10.3%; PETR4 2014-09-29 -11.2%; PETR4 2014-10-06 +11.1%; PETR4 2014-10-13 +10.5%; PETR4 2014-10-27 -12.3%; PETR4 2014-11-21 +11.9%; PETR4 2015-01-28 -11.2%; PETR4 2015-02-03 +15.5%; PETR4 2015-10-02 +10.7%; PETR4 2016-02-22 +13.0%; PETR4 2016-03-03 +16.3%; PETR4 2016-03-15 -10.7%; PETR4 2016-03-17 +12.0%; PETR4 2017-05-18 -15.8%; PETR4 2018-05-24 -13.7%; PETR4 2018-05-28 -14.6%; PETR4 2018-05-29 +14.1%; PETR4 2018-06-01 -14.9%; PETR4 2018-10-08 +11.0%; PETR4 2020-02-26 -10.1%; PETR4 2020-03-09 -29.7%; PETR4 2020-03-12 -20.5%; PETR4 2020-03-13 +22.2%; PETR4 2020-03-16 -15.0%; PETR4 2020-03-18 -13.2%; PETR4 2020-03-24 +15.2%; PETR4 2021-02-22 -21.5%; PETR4 2021-02-23 +12.2%; PETR4 2024-03-08 -10.6%; VALE3 2015-04-24 +10.0%; VALE3 2015-08-27 +11.3%; VALE3 2015-10-07 +10.0%; VALE3 2015-10-13 -10.6%; VALE3 2016-02-04 +14.8%; VALE3 2016-02-22 +11.1%; VALE3 2016-03-02 +11.0%; VALE3 2016-03-08 -14.5%; VALE3 2016-04-12 +10.4%; VALE3 2016-04-22 -11.2%; VALE3 2019-01-28 -24.5%; VALE3 2020-03-09 -15.2%; VALE3 2020-03-10 +18.5%; VALE3 2020-03-12 -13.2%; VALE3 2020-03-13 +21.4%; VALE3 2020-03-24 +10.4%; VALE3 2022-11-11 +10.4% |
| Séries BCB (CDI, Selic meta, PTAX, Focus) | OK | cdi_diario: 3486 obs., até 2026-11-18 / selic_meta: 5071 obs., até 2026-11-19 / ptax: 3487 obs., até 2026-11-19 / focus: 6259 obs., até 2026-11-13 / Focus por horizonte×indicador: 2015/Câmbio=253, 2015/IPCA=506, 2015/Resultado primário=253, 2015/Selic=253, 2019/Câmbio=250, 2019/IPCA=500, 2019/Resultado primário=250, 2019/Selic=250, 2023/Câmbio=502, 2023/IPCA=502, 2023/Resultado primário=502, 2023/Selic=502, 2027/Câmbio=434, 2027/IPCA=434, 2027/Resultado primário=434, 2027/Selic=434 |
| Nenhuma observação após a data de corte | OK | corte = 2026-11-19 |
| Janela de estimação (-160, -21) com ≥ 120 retornos e t0 presente, em todas as eleições | OK | 80 combinações evento×ação; 0 com problema |
| Balanços: data de entrega à CVM × calendário da imprensa (2026) | OK | PETR4 2026: CVM 2026-11-10 × imprensa 2026-11-10 (igual) / BBAS3 2026: CVM 2026-11-11 × imprensa 2026-11-11 (igual) / ITUB4 2026: CVM 2026-11-03 × imprensa 2026-11-03 (igual) / VALE3 2026: CVM 2026-10-29 × imprensa 2026-10-29 (igual) / CYRE3 2026: CVM 2026-11-12 × imprensa 2026-11-12 (igual) / MRVE3 2026: CVM 2026-11-11 × imprensa 2026-11-11 (igual) / MGLU3 2026: CVM 2026-11-09 × imprensa 2026-11-09 (igual) / LREN3 2026: CVM 2026-11-05 × imprensa 2026-11-05 (igual) / TAEE11 2026: CVM 2026-11-11 × imprensa 2026-11-11 (igual) / EGIE3 2026: CVM 2026-11-10 × imprensa 2026-11-10 (igual) |
| Tesouro: cobertura dos vértices em [t0−45d, t0+10d] por turno | INFORMATIVO | t0 presente em todos os turnos; Eleições 2014: 1: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2014: 2: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2018: 1: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2018: 2: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2022: 1: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2022: 2: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2026: 1: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% / Eleições 2026: 2: pre_2a=100%, pre_3a=100%, real_3a=100%, implicita_3a=100% |
| Futuros MT5 (DI1, DOL): cobertura e OHLC (dias sem negócio não são preenchidos) | INFORMATIVO | DI1F27: 1248 pregões desde 2021-11-19, 0 faltantes, 0 OHLC inconsistentes / DI1F28: 1248 pregões desde 2021-11-19, 0 faltantes, 0 OHLC inconsistentes / DI1F29: 1248 pregões desde 2021-11-19, 0 faltantes, 0 OHLC inconsistentes / DI1F31: 1248 pregões desde 2021-11-19, 0 faltantes, 0 OHLC inconsistentes / DI1F33: 1245 pregões desde 2021-11-19, 3 faltantes (2021-12-06, 2021-12-16, 2021-12-20), 0 OHLC inconsistentes / DOL$N: 1248 pregões desde 2021-11-19, 0 faltantes, 0 OHLC inconsistentes, 60 dias de rolagem |

## Eventos corporativos e ocorrências a investigar

Decisões já tomadas sobre estas ocorrências: `dados/metadados/decisoes_validacao.md`.

- PETR4: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- PETR4 2022-08-12: provento de 18.6% do preço — conferir valor e escala no RI/B3
- PETR4 2020-03-09: retorno bruto -29.7% sem desdobramento registrado — conferir evento corporativo
- BBAS3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- BBAS3 2026-10-26: retorno bruto -29.3% sem desdobramento registrado — conferir evento corporativo
- ITUB4: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- VALE3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- CYRE3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- CYRE3 2026-10-26: retorno bruto -44.8% sem desdobramento registrado — conferir evento corporativo
- MRVE3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- MRVE3 2026-10-26: retorno bruto -42.5% sem desdobramento registrado — conferir evento corporativo
- MGLU3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- MGLU3 2013-08-07: retorno bruto +28.9% sem desdobramento registrado — conferir evento corporativo
- MGLU3 2015-07-31: retorno bruto +31.9% sem desdobramento registrado — conferir evento corporativo
- MGLU3 2015-12-28: retorno bruto +37.3% sem desdobramento registrado — conferir evento corporativo
- MGLU3 2016-10-27: retorno bruto +30.9% sem desdobramento registrado — conferir evento corporativo
- MGLU3 2026-10-26: retorno bruto -58.2% sem desdobramento registrado — conferir evento corporativo
- LREN3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- LREN3 2026-10-26: retorno bruto -33.6% sem desdobramento registrado — conferir evento corporativo
- TAEE11: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20
- EGIE3: 1 pregões da B3 sem par no Yahoo (não afeta o ajuste, só a conferência): 2020-11-20

## Janelas de estimação por eleição

| evento                  | t0         | ticker   |   retornos_estimacao | pregao_t0_presente   |
|:------------------------|:-----------|:---------|---------------------:|:---------------------|
| Eleições 2014: 1º turno | 2014-10-06 | PETR4    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | BBAS3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | ITUB4    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | VALE3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | CYRE3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | MRVE3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | MGLU3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | LREN3    |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | TAEE11   |                  140 | True                 |
| Eleições 2014: 1º turno | 2014-10-06 | EGIE3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | PETR4    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | BBAS3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | ITUB4    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | VALE3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | CYRE3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | MRVE3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | MGLU3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | LREN3    |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | TAEE11   |                  140 | True                 |
| Eleições 2014: 2º turno | 2014-10-27 | EGIE3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | PETR4    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | BBAS3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | ITUB4    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | VALE3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | CYRE3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | MRVE3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | MGLU3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | LREN3    |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | TAEE11   |                  140 | True                 |
| Eleições 2018: 1º turno | 2018-10-08 | EGIE3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | PETR4    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | BBAS3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | ITUB4    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | VALE3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | CYRE3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | MRVE3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | MGLU3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | LREN3    |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | TAEE11   |                  140 | True                 |
| Eleições 2018: 2º turno | 2018-10-29 | EGIE3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | PETR4    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | BBAS3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | ITUB4    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | VALE3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | CYRE3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | MRVE3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | MGLU3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | LREN3    |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | TAEE11   |                  140 | True                 |
| Eleições 2022: 1º turno | 2022-10-03 | EGIE3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | PETR4    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | BBAS3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | ITUB4    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | VALE3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | CYRE3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | MRVE3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | MGLU3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | LREN3    |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | TAEE11   |                  140 | True                 |
| Eleições 2022: 2º turno | 2022-10-31 | EGIE3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | PETR4    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | BBAS3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | ITUB4    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | VALE3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | CYRE3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | MRVE3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | MGLU3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | LREN3    |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | TAEE11   |                  140 | True                 |
| Eleições 2026: 1º turno | 2026-10-05 | EGIE3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | PETR4    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | BBAS3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | ITUB4    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | VALE3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | CYRE3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | MRVE3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | MGLU3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | LREN3    |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | TAEE11   |                  140 | True                 |
| Eleições 2026: 2º turno | 2026-10-26 | EGIE3    |                  140 | True                 |

## Amostra para conferência manual no site da B3

| data       | ticker   |   abertura |   fechamento |   fechamento_ajustado |   volume_financeiro |
|:-----------|:---------|-----------:|-------------:|----------------------:|--------------------:|
| 2026-10-23 | BBAS3    |      23.95 |        24.72 |                 24.72 |       1121705683.00 |
| 2026-10-23 | CYRE3    |      34.41 |        35.57 |                 35.57 |        393052576.00 |
| 2026-10-23 | EGIE3    |      30.94 |        30.79 |                 30.79 |         56723405.00 |
| 2026-10-23 | IBOV     |     nan    |    205082.56 |                nan    |              nan    |
| 2026-10-23 | ITUB4    |      48.08 |        48.30 |                 48.28 |       1349617964.00 |
| 2026-10-23 | LREN3    |      14.47 |        14.58 |                 14.58 |        255393458.00 |
| 2026-10-23 | MGLU3    |      12.99 |        12.69 |                 12.69 |        874249780.00 |
| 2026-10-23 | MRVE3    |       8.27 |         8.23 |                  8.23 |        203319068.00 |
| 2026-10-23 | PETR4    |      58.10 |        58.68 |                 58.68 |       3437709460.00 |
| 2026-10-23 | TAEE11   |      44.90 |        44.75 |                 43.62 |        118264389.00 |
| 2026-10-23 | VALE3    |      61.65 |        61.90 |                 61.90 |       1671196874.00 |
| 2026-10-26 | BBAS3    |      16.48 |        17.47 |                 17.47 |       4978645162.00 |
| 2026-10-26 | CYRE3    |      17.79 |        19.63 |                 19.63 |       1228583968.00 |
| 2026-10-26 | EGIE3    |      27.43 |        27.50 |                 27.50 |        323083997.00 |
| 2026-10-26 | IBOV     |     nan    |    176608.23 |                nan    |              nan    |
| 2026-10-26 | ITUB4    |      42.00 |        41.70 |                 41.68 |       6034197682.00 |
| 2026-10-26 | LREN3    |       9.80 |         9.68 |                  9.68 |        873466336.00 |
| 2026-10-26 | MGLU3    |       6.35 |         5.30 |                  5.30 |        635506777.00 |
| 2026-10-26 | MRVE3    |       4.12 |         4.73 |                  4.73 |        200905184.00 |
| 2026-10-26 | PETR4    |      51.20 |        53.88 |                 53.88 |       7459734946.00 |
| 2026-10-26 | TAEE11   |      40.08 |        40.50 |                 39.48 |        354591282.00 |
| 2026-10-26 | VALE3    |      67.97 |        64.38 |                 64.38 |       6021159012.00 |
| 2026-10-27 | BBAS3    |      18.00 |        17.38 |                 17.38 |       2202328476.00 |
| 2026-10-27 | CYRE3    |      20.02 |        19.01 |                 19.01 |        730053072.00 |
| 2026-10-27 | EGIE3    |      27.69 |        28.00 |                 28.00 |        251095285.00 |
| 2026-10-27 | IBOV     |     nan    |    175710.05 |                nan    |              nan    |
| 2026-10-27 | ITUB4    |      42.05 |        41.19 |                 41.17 |       2153016349.00 |
| 2026-10-27 | LREN3    |       9.88 |         9.72 |                  9.72 |        551809722.00 |
| 2026-10-27 | MGLU3    |       5.55 |         5.75 |                  5.75 |        586388812.00 |
| 2026-10-27 | MRVE3    |       4.88 |         4.46 |                  4.46 |        213597734.00 |
| 2026-10-27 | PETR4    |      53.60 |        52.79 |                 52.79 |       4285385964.00 |
| 2026-10-27 | TAEE11   |      41.10 |        40.57 |                 39.55 |        283885404.00 |
| 2026-10-27 | VALE3    |      64.30 |        63.00 |                 63.00 |       2772825021.00 |
| 2026-11-18 | BBAS3    |      14.62 |        14.12 |                 14.12 |        978578423.00 |
| 2026-11-18 | CYRE3    |      19.50 |        19.10 |                 19.10 |        187398305.00 |
| 2026-11-18 | EGIE3    |      25.83 |        25.49 |                 25.49 |         68880704.00 |
| 2026-11-18 | IBOV     |     nan    |    167537.95 |                nan    |              nan    |
| 2026-11-18 | ITUB4    |      40.79 |        40.19 |                 40.19 |        938369415.00 |
| 2026-11-18 | LREN3    |       9.56 |         9.47 |                  9.47 |        191430251.00 |
| 2026-11-18 | MGLU3    |       7.93 |         8.32 |                  8.32 |        565266549.00 |
| 2026-11-18 | MRVE3    |       5.01 |         4.77 |                  4.77 |        118144485.00 |
| 2026-11-18 | PETR4    |      43.70 |        43.17 |                 43.17 |       1311622386.00 |
| 2026-11-18 | TAEE11   |      40.64 |        40.56 |                 40.56 |         66259051.00 |
| 2026-11-18 | VALE3    |      59.95 |        59.00 |                 59.00 |       1578494729.00 |

## Itens que dependem do grupo

- [ ] Conferir a amostra acima contra a B3 (cotações históricas / página do índice)
- [ ] Investigar cada ocorrência da seção de ajustes e registrar a decisão
- [ ] Conferir no site do Fed as datas do FOMC marcadas como "de memória" em dados/manuais/calendario_eventos.csv (2014-09, 2018-11, 2022-09)
- [ ] Conferir no RI os horários dos balanços marcados "a conferir" (relatório de produção da Petrobras, resultado do BB)
- [ ] Definir a situação da base e o responsável por cada pendência