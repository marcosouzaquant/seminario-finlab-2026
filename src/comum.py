"""Configuração compartilhada: universo, datas, caminhos, rede e registro de fontes.

Toda alteração de universo ou de datas deve ser feita aqui e registrada em dados/metadados/decisoes_validacao.md.
"""
from __future__ import annotations

import csv
import datetime as dt
import ssl
from pathlib import Path
from zoneinfo import ZoneInfo

# --------------------------------------------------------------------------- universo
ACOES_NUCLEO = ["PETR4", "BBAS3", "ITUB4", "VALE3"]          # estatais, banco privado, exportadora
ACOES_JUROS = ["CYRE3", "MRVE3", "MGLU3", "LREN3", "TAEE11", "EGIE3"]  # canal de juros domésticos
ACOES = ACOES_NUCLEO + ACOES_JUROS
GRUPOS_JUROS = {"imobiliario": ["CYRE3", "MRVE3"], "varejo": ["MGLU3", "LREN3"], "utilities": ["TAEE11", "EGIE3"]}
# Códigos antigos da mesma companhia (concatenados na leitura do COTAHIST)
ALIAS_TICKER = {"TBLE3": "EGIE3"}  # Tractebel Energia -> Engie Brasil (troca de código em jul/2016)
INDICES_B3 = ["IBOV", "IMOB", "SMLL", "IFNC", "UTIL", "ICON"]  # IBOV = benchmark; demais = canais setoriais
CONTROLES_YAHOO = {"^GSPC": "sp500", "^VIX": "vix", "BZ=F": "brent"}
FOCUS_INDICADORES = ["IPCA", "Selic", "Câmbio", "Resultado primário"]
# Focus: para cada eleição, expectativas do ano seguinte coletadas durante o ano eleitoral
FOCUS_JANELAS = {"2015": ("2014-01-01", "2014-12-31"), "2019": ("2018-01-01", "2018-12-31"),
                 "2023": ("2022-01-01", "2022-12-31"), "2027": ("2026-01-01", None)}  # None = até a data de fim
# Empresas na CVM (dados abertos de ITR): nome usado para localizar a companhia
CVM_EMPRESAS = {"PETR4": "PETROLEO BRASILEIRO", "BBAS3": "BCO BRASIL S.A.", "ITUB4": "ITAU UNIBANCO HOLDING",
                "VALE3": "VALE S.A.", "CYRE3": "CYRELA BRAZIL REALTY", "MRVE3": "MRV ENGENHARIA",
                "MGLU3": "MAGAZINE LUIZA", "LREN3": "LOJAS RENNER", "TAEE11": "TRANSMISSORA ALIANÇA",
                "EGIE3": ("ENGIE BRASIL ENERGIA", "TRACTEBEL ENERGIA")}
ANOS_ELEICAO = [2014, 2018, 2022, 2026]
SGS_SERIES = {12: "cdi_diario", 432: "selic_meta"}

# --------------------------------------------------------------------------- datas
ANO_INICIO = 2013  # cobre as eleições de 2014, 2018 e 2022 com janela de estimação
DATA_INICIO = dt.date(ANO_INICIO, 1, 1)
DATA_CORTE_FINAL = dt.date(2026, 11, 27)
FUSO = ZoneInfo("America/Sao_Paulo")

# --------------------------------------------------------------------------- caminhos
RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
TRATADOS = RAIZ / "dados" / "tratados"
METADADOS = RAIZ / "dados" / "metadados"
MANUAIS = RAIZ / "dados" / "manuais"
for _p in (BRUTOS, TRATADOS, METADADOS, MANUAIS):
    _p.mkdir(parents=True, exist_ok=True)

CA_BUNDLE = RAIZ / ".venv" / "ca_windows.pem"


def agora_iso() -> str:
    return dt.datetime.now(FUSO).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- rede
def preparar_ssl() -> None:
    """Usa o repositório de certificados do Windows (necessário nesta máquina).

    Mantém a verificação de certificados ligada. Também gera um bundle PEM para o
    curl_cffi usado pelo yfinance, que não lê o repositório do Windows.
    """
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass
    if not CA_BUNDLE.exists() and hasattr(ssl, "enum_certificates"):
        import certifi

        pems = set()
        for loja in ("ROOT", "CA"):
            for cert, enc, _ in ssl.enum_certificates(loja):
                if enc == "x509_asn":
                    pems.add(ssl.DER_cert_to_PEM_cert(cert))
        CA_BUNDLE.parent.mkdir(exist_ok=True)
        CA_BUNDLE.write_text(Path(certifi.where()).read_text() + "".join(pems))


def sessao_yahoo():
    from curl_cffi import requests as cr

    verify = str(CA_BUNDLE) if CA_BUNDLE.exists() else True
    return cr.Session(impersonate="chrome", verify=verify)


# --------------------------------------------------------------------------- registro de fontes
CAMPOS_FONTES = [
    "fonte_id", "instituicao", "serie", "url", "arquivo_original", "coletado_em",
    "inicio", "fim", "unidade", "tratamento", "responsavel",
]


def registrar_fonte(**kw) -> None:
    """Acrescenta (ou substitui pelo fonte_id) uma linha em dados/metadados/fontes.csv."""
    caminho = METADADOS / "fontes.csv"
    linhas = []
    if caminho.exists():
        with caminho.open(encoding="utf-8", newline="") as f:
            linhas = [r for r in csv.DictReader(f) if r["fonte_id"] != kw["fonte_id"]]
    kw.setdefault("coletado_em", agora_iso())
    kw.setdefault("responsavel", "")
    linhas.append({c: kw.get(c, "") for c in CAMPOS_FONTES})
    linhas.sort(key=lambda r: r["fonte_id"])
    with caminho.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_FONTES)
        w.writeheader()
        w.writerows(linhas)
