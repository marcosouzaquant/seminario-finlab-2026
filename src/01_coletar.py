"""Etapa 1: baixa os dados brutos e registra cada fonte em dados/metadados/fontes.csv.

Uso:  .venv/Scripts/python src/01_coletar.py [--fim AAAA-MM-DD] [--sem-cotahist-antigo]

Os arquivos brutos não são editados depois de baixados. Rodar de novo em 27/11
(data de corte) para a versão final.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import time

import pandas as pd
import requests

import comum as C


def baixar(url: str, destino, tentativas: int = 3, **kw) -> requests.Response:
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=180, **kw)
            r.raise_for_status()
            if destino is not None:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(r.content)
            return r
        except requests.RequestException as e:
            if i == tentativas - 1:
                raise
            print(f"  nova tentativa ({e.__class__.__name__})")
            time.sleep(3 * (i + 1))


# --------------------------------------------------------------------------- B3: COTAHIST
def coletar_cotahist(fim: dt.date, refazer_antigos: bool) -> None:
    pasta = C.BRUTOS / "b3_cotahist"
    for ano in range(C.ANO_INICIO, fim.year + 1):
        destino = pasta / f"COTAHIST_A{ano}.ZIP"
        ano_corrente = ano == fim.year
        if destino.exists() and not ano_corrente and not refazer_antigos:
            print(f"COTAHIST {ano}: já existe")
            continue
        url = f"https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{ano}.ZIP"
        print(f"COTAHIST {ano}: baixando")
        baixar(url, destino)
    C.registrar_fonte(
        fonte_id="B3_COTAHIST", instituicao="B3", serie="Cotações históricas, mercado à vista (arquivos anuais)",
        url="https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{ano}.ZIP",
        arquivo_original="dados/brutos/b3_cotahist/", inicio=str(C.ANO_INICIO), fim=str(fim),
        unidade="R$ por ação (÷ FATCOT); volume em R$", tratamento="Sem ajuste por proventos; filtro TIPREG=01, CODBDI=02, TPMERC=010",
    )


# --------------------------------------------------------------------------- B3: índices
def coletar_indices_b3(fim: dt.date) -> None:
    pasta = C.BRUTOS / "b3_indices"
    for indice in C.INDICES_B3:
        for ano in range(C.ANO_INICIO, fim.year + 1):
            destino = pasta / f"{indice}_{ano}.json"
            if destino.exists() and ano != fim.year and json.loads(destino.read_text(encoding="utf-8")).get("results"):
                continue
            payload = base64.b64encode(json.dumps({"index": indice, "language": "pt-br", "year": str(ano)}).encode()).decode()
            url = f"https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetPortfolioDay/{payload}"
            for tentativa in range(4):  # a API às vezes devolve resultado vazio de forma transitória
                if baixar(url, destino).json().get("results"):
                    break
                time.sleep(3 * (tentativa + 1))
            else:
                raise RuntimeError(f"B3 devolveu resultado vazio para {indice} {ano}")
        print(f"Índice {indice}: ok")
        C.registrar_fonte(
            fonte_id=f"B3_INDICE_{indice}", instituicao="B3", serie=f"{indice}: fechamento diário (estatísticas do índice)",
            url="https://sistemaswebb3-listados.b3.com.br/indexStatisticsPage/day/" + indice,
            arquivo_original=f"dados/brutos/b3_indices/{indice}_AAAA.json", inicio=str(C.ANO_INICIO), fim=str(fim),
            unidade="pontos", tratamento="Tabela dia × mês convertida em série diária",
        )


# --------------------------------------------------------------------------- Yahoo: ações, IBOV e controles
def coletar_yahoo(fim: dt.date) -> None:
    import yfinance as yf

    sessao = C.sessao_yahoo()
    pasta = C.BRUTOS / "yahoo"
    pasta.mkdir(parents=True, exist_ok=True)
    tickers = {f"{a}.SA": a for a in C.ACOES} | {"^BVSP": "ibov_yahoo"} | C.CONTROLES_YAHOO
    for ticker, nome in tickers.items():
        df = yf.download(
            ticker, start=str(C.DATA_INICIO - dt.timedelta(days=40)), end=str(fim + dt.timedelta(days=1)),
            auto_adjust=False, actions=True, progress=False, session=sessao, multi_level_index=False,
        )
        if df.empty:
            raise RuntimeError(f"Yahoo não retornou dados para {ticker}")
        df.index.name = "data"
        df.to_csv(pasta / f"{nome}.csv")
        print(f"Yahoo {ticker}: {len(df)} linhas")
        papel = "fator de ajuste e eventos corporativos (fonte secundária)" if ticker.endswith(".SA") else "conferência/controle externo"
        C.registrar_fonte(
            fonte_id=f"YAHOO_{nome.upper()}", instituicao="Yahoo Finance (via yfinance)", serie=f"{ticker}: OHLCV, Adj Close, proventos",
            url=f"https://finance.yahoo.com/quote/{ticker}", arquivo_original=f"dados/brutos/yahoo/{nome}.csv",
            inicio=str(df.index.min().date()), fim=str(df.index.max().date()), unidade="moeda de negociação; pontos para índices",
            tratamento=f"Uso: {papel}",
        )


# --------------------------------------------------------------------------- BCB
def coletar_sgs(fim: dt.date) -> None:
    pasta = C.BRUTOS / "bcb_sgs"
    for codigo, nome in C.SGS_SERIES.items():
        partes = []
        for ano in range(C.ANO_INICIO, fim.year + 1):  # SGS limita consultas diárias a 10 anos
            ini, fim_ano = dt.date(ano, 1, 1), min(dt.date(ano, 12, 31), fim)
            url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
                   f"&dataInicial={ini:%d/%m/%Y}&dataFinal={fim_ano:%d/%m/%Y}")
            partes += baixar(url, None).json()
        (pasta / f"sgs_{codigo}_{nome}.json").parent.mkdir(parents=True, exist_ok=True)
        (pasta / f"sgs_{codigo}_{nome}.json").write_text(json.dumps(partes), encoding="utf-8")
        print(f"SGS {codigo} ({nome}): {len(partes)} obs.")
        unidade = "% ao dia" if codigo == 12 else "% ao ano"
        C.registrar_fonte(
            fonte_id=f"BCB_SGS_{codigo}", instituicao="Banco Central do Brasil (SGS)", serie=f"Série {codigo}: {nome}",
            url=f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados", arquivo_original=f"dados/brutos/bcb_sgs/sgs_{codigo}_{nome}.json",
            inicio=str(C.DATA_INICIO), fim=str(fim), unidade=unidade, tratamento="Consulta anual concatenada",
        )


def coletar_ptax(fim: dt.date) -> None:
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
           "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
           f"?@dataInicial='{C.DATA_INICIO:%m-%d-%Y}'&@dataFinalCotacao='{fim:%m-%d-%Y}'&$format=json")
    destino = C.BRUTOS / "bcb_ptax" / "ptax_dolar.json"
    r = baixar(url, destino)
    print(f"PTAX: {len(r.json()['value'])} obs.")
    C.registrar_fonte(
        fonte_id="BCB_PTAX", instituicao="Banco Central do Brasil (Olinda/PTAX)", serie="Dólar PTAX, compra e venda, boletim de fechamento",
        url="https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo", arquivo_original="dados/brutos/bcb_ptax/ptax_dolar.json",
        inicio=str(C.DATA_INICIO), fim=str(fim), unidade="R$/US$", tratamento="Último boletim do dia (fechamento)",
    )


def coletar_focus(fim: dt.date) -> None:
    from urllib.parse import quote
    pasta = C.BRUTOS / "bcb_focus"
    pasta.mkdir(parents=True, exist_ok=True)
    for horizonte, (ini, fim_j) in C.FOCUS_JANELAS.items():
        fim_j = fim_j or str(fim)
        total = []
        for ind in C.FOCUS_INDICADORES:
            filtro = (f"Indicador eq '{ind}' and DataReferencia eq '{horizonte}' "
                      f"and Data ge '{ini}' and Data le '{fim_j}'")
            url = ("https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais"
                   f"?$format=json&$top=20000&$filter={quote(filtro)}")  # Olinda rejeita '+' como espaço
            valores = baixar(url, None).json()["value"]
            if not valores:
                raise RuntimeError(f"Focus sem dados para '{ind}' {horizonte}")
            total += valores
        (pasta / f"focus_anuais_{horizonte}.json").write_text(json.dumps(total, ensure_ascii=False), encoding="utf-8")
        print(f"Focus horizonte {horizonte} ({ini} a {fim_j}): {len(total)} obs.")
    C.registrar_fonte(
        fonte_id="BCB_FOCUS", instituicao="Banco Central do Brasil (Sistema de Expectativas)",
        serie=f"ExpectativasMercadoAnuais: {', '.join(C.FOCUS_INDICADORES)}; horizonte = ano seguinte a cada eleição",
        url="https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais",
        arquivo_original="dados/brutos/bcb_focus/focus_anuais_AAAA.json", inicio="2014-01-01", fim=str(fim),
        unidade="conforme indicador (% , R$/US$, % do PIB)", tratamento="Todas as bases de cálculo mantidas; separar na análise",
    )


def coletar_tesouro(fim: dt.date) -> None:
    url = ("https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/"
           "resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv")
    destino = C.BRUTOS / "tesouro" / "PrecoTaxaTesouroDireto.csv"
    baixar(url, destino)
    print(f"Tesouro Direto: {destino.stat().st_size / 1e6:.1f} MB")
    C.registrar_fonte(
        fonte_id="TESOURO_TD", instituicao="Tesouro Nacional (Tesouro Transparente)",
        serie="Preços e taxas históricas dos títulos do Tesouro Direto", url=url,
        arquivo_original="dados/brutos/tesouro/PrecoTaxaTesouroDireto.csv", inicio="2004-12-31", fim=str(fim),
        unidade="% ao ano", tratamento="Taxa de venda da manhã; prefixados sem cupom e IPCA+ sem cupom; interpolação a prazo constante",
    )


def coletar_cvm_itr() -> None:
    import zipfile
    pasta = C.BRUTOS / "cvm_itr"
    for ano in C.ANOS_ELEICAO:
        destino = pasta / f"itr_cia_aberta_{ano}.zip"
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{ano}.zip"
        baixar(url, destino)
        with zipfile.ZipFile(destino) as z:
            nomes = [n for n in z.namelist() if n == f"itr_cia_aberta_{ano}.csv"]
        print(f"CVM ITR {ano}: ok ({nomes[0] if nomes else 'arquivo índice não encontrado'})")
    C.registrar_fonte(
        fonte_id="CVM_ITR", instituicao="Comissão de Valores Mobiliários (dados abertos)",
        serie="ITR de companhias abertas: data de recebimento de cada entrega",
        url="https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/", arquivo_original="dados/brutos/cvm_itr/",
        inicio=str(C.ANOS_ELEICAO[0]), fim=str(C.ANOS_ELEICAO[-1]), unidade="data",
        tratamento="DT_RECEB da 1ª versão do ITR do 3º trimestre (horário não informado pela CVM)",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fim", default=str(min(dt.date.today(), C.DATA_CORTE_FINAL)))
    ap.add_argument("--refazer-cotahist-antigo", action="store_true")
    a = ap.parse_args()
    fim = dt.date.fromisoformat(a.fim)
    print(f"Coleta até {fim} (início {C.DATA_INICIO}) — {C.agora_iso()}")
    C.preparar_ssl()
    coletar_sgs(fim)
    coletar_ptax(fim)
    coletar_focus(fim)
    coletar_tesouro(fim)
    coletar_cvm_itr()
    coletar_indices_b3(fim)
    coletar_yahoo(fim)
    coletar_cotahist(fim, a.refazer_cotahist_antigo)
    (C.METADADOS / "ultima_coleta.txt").write_text(f"fim_solicitado={fim}\ncoletado_em={C.agora_iso()}\n", encoding="utf-8")
    print("Coleta concluída.")


if __name__ == "__main__":
    main()
