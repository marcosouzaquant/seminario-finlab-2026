# Decisões de validação (registro manual)

Cada decisão tem data, evidência e responsável. Atualizar sempre que o relatório apontar algo novo.
Correções aplicadas à base ficam em `dados/manuais/eventos_corporativos_manuais.csv`. Ocorrências conferidas que não exigem correção ficam em `dados/manuais/ocorrencias_resolvidas.csv`.

## Fontes de preço

| Data | Ocorrência | Evidência | Decisão |
|---|---|---|---|
| 19/11/2026 | Fechamentos diários do Yahoo divergem do oficial da B3 em pregões isolados (`divergencias_b3_yahoo.csv`) | Num dia o Yahoo difere e no seguinte volta a coincidir com a B3 | **Preços vêm só da B3 (COTAHIST).** Do Yahoo usam-se apenas proventos e desdobramentos, conferidos abaixo |
| 19/11/2026 | Ibovespa B3 × Yahoo acima de 0,1% em alguns dias | B3 é a fonte primária | Usar B3; Yahoo só conferência |
| 19/11/2026 | 2020-11-20 sem par no Yahoo (4 ações) | O pregão existe na B3 | Não afeta a base |
| 19/11/2026 | Conferência independente com MT5 (Clear), nov/2021 a nov/2026 (`conferencia_mt5_resumo.csv`) | IBOV: 99,9% dos fechamentos dentro de 0,1%. Ações (o MT5 entrega séries ajustadas): retornos diários iguais em 96–100% dos pregões; o resto difere ≤ 0,1 p.p. (arredondamento a centavos), exceto BBAS3 em 22/11/2023 e 22/02/2024 (ver abaixo) | Base confirmada por terceira fonte |

## Eventos corporativos

| Data | Ocorrência | Evidência | Decisão |
|---|---|---|---|
| 19/11/2026 | ITUB4 2013: retorno anual da base difere 2,4 p.p. do Yahoo | O Itaú registra a bonificação de 10% com evento em 21/05/2013 (página de eventos acionários do RI); aviso da OCC também fixa a data ex em 21/05/2013. O Yahoo aplica o efeito no preço em 20/05 (−8,0%) e 21/05 (+11,8%). Pela B3: 35,55 → 32,83 com bonificação 1,1 = +1,58% | **Resolvido:** a base está correta e o erro é do Yahoo |
| 19/11/2026 | ITUB4 2021-10-04: retorno de −18,0% | B3 (dados da companhia): "CIS RED CAP" com data com em 01/10/2021, a distribuição das ações da XP. O Yahoo não registra; IFNC −3,6% no dia | **Resolvido:** `retorno_valido = False` no dia. Sem preço ex-teórico, não se inventa fator |
| 19/11/2026 | PETR4 2022-08-12: provento de 18,6% do preço | Dividendo de R$ 6,73/ação, anunciado em 28/07/2022, data com 11/08 e ex 12/08/2022 (InfoMoney, CNN Brasil). Base: R$ 6,732 | **Resolvido:** valor e data corretos |
| 19/11/2026 | BBAS3 2023-11-22: provento ausente no Yahoo | BB, anúncio de 08/11/2023: dividendo R$ 0,10198860740 + JCP R$ 0,68622202551 por ação; data com 21/11, ex 22/11/2023 (Suno, InfoMoney). MT5 mostrava 1,3 p.p. de diferença, que corresponde ao valor com JCP líquido de IR | **Corrigido:** provento manual de R$ 0,78821062 (bruto, por ação anterior ao desdobramento de 2024) |
| 19/11/2026 | BBAS3 2024-02-22: provento ausente no Yahoo | BB, anúncio de 08/02/2024 com correção: JCP R$ 0,62114063186 + dividendo R$ 0,22081862607; data com 21/02, ex 22/02/2024 (Suno, Finance News). Valores depois atualizados pela Selic até o pagamento | **Corrigido:** provento manual de R$ 0,84195926 (valor conhecido na data ex) |
| 19/11/2026 | Completude dos proventos da BBAS3 no Yahoo | O Yahoo tem 8 proventos/ano em 2013–2022 e 7 em 2023 e 2024, que são os anos com as duas ausências acima | Sem outras ausências aparentes |
| 19/11/2026 | Proventos de 2025–2026: Yahoo × API de proventos da B3 | Coincidem nas 4 ações, exceto BBAS3 02/09/2026 (Yahoo R$ 0,105 × B3 R$ 0,140; ≈ 0,17 p.p. no dia) e PETR4 23/12/2025 (0,9% no valor) | Efeito desprezível; mantido |
| 19/11/2026 | EGIE3 só aparece no COTAHIST a partir de 21/07/2016 | A companhia negociava como TBLE3 (Tractebel Energia) antes da troca de nome | **Corrigido:** TBLE3 é lido como EGIE3 (`ALIAS_TICKER` em `src/comum.py`) |
| 19/11/2026 | MRVE3 2018-12-21: retorno de −5,4% contra cerca de +4,0% no Yahoo | B3 (dados da companhia): "CIS RED CAP", data com 20/12/2018, a distribuição das ações da LOG Commercial Properties | **Corrigido:** `retorno_valido = False` no dia |
| 19/11/2026 | CYRE3 2026-01-02: MT5 aponta 15,3 p.p. de diferença | B3: bonificação de 18,958333% com data com 30/12/2025; ausente no Yahoo | **Corrigido:** desdobramento manual com fator 1,18958333 |
| 19/11/2026 | MGLU3 2024-02-01: Yahoo +4,9% × base −1,9% | MT5 concorda com a base (diferença de 0,6 p.p., arredondamento de preço baixo) | Erro do Yahoo; base mantida |
| 19/11/2026 | MGLU3: altas de 29% a 37% em 2013–2016 | Mesmo retorno no Yahoo (fonte independente); os grupamentos e desdobramentos (2015, 2017, 2019, 2020, 2024 e 2025) são tratados pelos eventos | Movimento de mercado |
| 19/11/2026 | TAEE11 2015: diferença anual de 1,07 p.p. | Diferenças diárias alternadas de sinal (ruído do fechamento do Yahoo); MT5 concorda 100% em 2021–2026 | Ruído do Yahoo; base mantida |
| 19/11/2026 | CYRE3, MRVE3, MGLU3 e LREN3 em 2026-10-26: quedas de 34% a 58% | Retornos idênticos no MT5; sem evento na B3 | Movimento de mercado |
| 19/11/2026 | BBAS3 2026-10-26: retorno bruto de −29,3% | Preço da B3 (24,72 → 17,47); IFNC −22,5% no mesmo pregão; API da B3 sem provento ou desdobramento próximo | **Resolvido:** movimento de mercado |
| 19/11/2026 | PETR4 2020-03-09: retorno bruto de −29,7% | Preço da B3; sem evento corporativo | **Resolvido:** movimento de mercado |

## Futuros (MT5)

| Data | Ocorrência | Evidência | Decisão |
|---|---|---|---|
| 19/11/2026 | DOL$N (série contínua) troca de contrato | A diferença entre o retorno do DOL$N e o da PTAX é +0,53% em média no último pregão do mês, contra ≈ 0 nos demais | `retorno_valido = False` no último pregão de cada mês. As datas eleitorais não são afetadas |
| 19/11/2026 | DI1F33 sem barra em 06/12, 16/12 e 20/12/2021 | Vértice longo sem negócio nesses dias | Não preencher; fora das janelas eleitorais |
| 19/11/2026 | Cotações do MT5 são do último negócio, não do ajuste da B3 | Característica da fonte | Documentado; usar a variação em pontos-base no DI |

## Eleições passadas (2014, 2018, 2022)

| Data | Ocorrência | Evidência | Decisão |
|---|---|---|---|
| 19/11/2026 | DI do MT5 não cobre 2014 e 2018 | O MT5 só guarda contratos não vencidos (desde nov/2021) | Curva de juros pelo histórico do Tesouro Direto (Tesouro Nacional), com prazo constante interpolado. Os 4 vértices estão completos nas janelas dos 8 turnos |
| 19/11/2026 | Taxa do Tesouro é da manhã; o retorno das ações vai de fechamento a fechamento | Característica da fonte | Sensibilidade com Δ_t + Δ_t+1 (Dimson). Correlação de 0,98 com a medida pelo DI1F29 em 2022–2025 |
| 19/11/2026 | Focus: base de cálculo 1 só existe a partir de 2022 (e para IPCA em 2014 e 2018) | API do BCB | Usar base 0 nas comparações entre eleições |
| 19/11/2026 | Datas de balanço de 2014, 2018 e 2022 | Data de entrega do ITR do 3º trimestre à CVM. Em 2026 as 10 datas coincidem com as da imprensa | Usar a data da CVM e presumir divulgação após o fechamento |
| 19/11/2026 | Petrobras, ITR do 3º trimestre de 2014 entregue só em 22/04/2015 | CVM | Fora das janelas; registrar como limitação (a empresa adiou o balanço auditado) |
