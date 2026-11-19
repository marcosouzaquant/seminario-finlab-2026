# Seminário FinLab 2026/2 — Análise Quantitativa e Análise Técnica

Base de dados e código do grupo para o I Seminário FinLab Contexto Econômico-Financeiro (2026/2): efeitos do resultado das eleições de 2026 sobre ações, índices, juros e câmbio, com comparação com as eleições de 2014, 2018 e 2022.

Conteúdo educativo. Não é recomendação de investimento e não expressa posição política.

## Gerar a base

Requer Python 3.10+ (testado em 3.13, Windows 11).

```bash
py -3.13 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python src/01_coletar.py                 # baixa brutos (≈ 10 min na 1ª vez)
.venv/Scripts/python src/02_tratar_validar.py          # gera tratados + relatório
.venv/Scripts/python src/04_sensibilidade_juros.py     # sensibilidade a juros 2022–2025 (usa futuros do MT5)
```

**MetaTrader 5 (opcional):** os scripts abaixo exigem um terminal MT5 aberto e conectado e só leem cotações.
- `src/01b_coletar_mt5.py` atualiza o DI futuro e o dólar futuro em `dados/brutos/mt5/`. Esses CSVs ficam no repositório, então quem não tem MT5 roda só os passos 1 e 2.
- `src/03_conferir_mt5.py` confere a base com o MT5.

Versão final (data de corte): `--fim 2026-11-27` no passo 1 e `--corte 2026-11-27` no passo 2.

O arquivo `dados/metadados/manifesto_arquivos.csv` registra o hash SHA-256 de cada arquivo tratado, para identificar a versão usada nos resultados.

**Certificados SSL:** nesta máquina o Python não reconhecia a cadeia de certificados. O código usa o repositório do Windows (`truststore`) e mantém a verificação ligada. Em outras máquinas isso não atrapalha.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `dados/brutos/` | Downloads originais, nunca editados |
| `dados/manuais/` | Insumos preenchidos à mão (calendário de eventos) |
| `dados/tratados/` | Séries prontas para análise (CSV UTF-8, datas ISO, ponto decimal) |
| `dados/metadados/` | Fontes, dicionário, relatório de validação, decisões, manifesto |
| `src/` | `comum.py` (universo e datas), `01_coletar.py`, `02_tratar_validar.py` |

## Convenções principais

- **Preços das ações: B3 (COTAHIST), fonte primária.** O Yahoo fornece apenas datas e valores de proventos e desdobramentos.
- **Preço ajustado** = preço bruto × `fator_ajuste`. O fator é o produto dos multiplicadores dos eventos posteriores: `(1 − provento / fechamento anterior) ÷ desdobramento`, a mesma convenção do Yahoo e do CRSP. No último pregão, ajustado = bruto.
- **Índices** (IBOV, IMOB, SMLL, IFNC): B3, em pontos. São índices de retorno total.
- **Calendário de pregões** = datas com fechamento do IBOV na B3.

## Fontes e termos de uso

Os dados pertencem às respectivas fontes e são reproduzidos apenas para fins educativos e de pesquisa, com a fonte e a data de coleta registradas em `dados/metadados/fontes.csv`. Para qualquer outro uso, consulte os termos de cada fonte:

- **B3:** cotações históricas (COTAHIST) e índices.
- **Banco Central do Brasil:** SGS, PTAX e Focus.
- **Tesouro Nacional:** Tesouro Transparente.
- **CVM:** dados abertos.
- **IBGE:** datas de divulgação do IPCA.
- **Yahoo Finance:** proventos, desdobramentos e controles externos.
- **MetaTrader 5 da corretora:** DI futuro e dólar futuro. São cotações de contratos da B3 obtidas pelo terminal da corretora.
