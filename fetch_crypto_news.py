import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
import hashlib
import json
import os
import logging
from time import sleep

# =========================
# CONFIG
# =========================

ATIVOS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth"],
}

DIAS = 7
LIMITE_POR_ATIVO = 20
OUTPUT_DIR = "output"
CACHE_FILE = "cache.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# =========================
# UTILS
# =========================

def agora():
    return datetime.now(timezone.utc)  # ✅ timezone-aware

def dentro_do_periodo(data):
    if not data:
        return False
    return data >= agora() - timedelta(days=DIAS)

def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def carregar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

# =========================
# NORMALIZAÇÃO
# =========================

def garantir_timezone(data):
    """Garante que a data tenha timezone UTC"""
    if not data:
        return None

    if isinstance(data, str):
        try:
            data = dateparser.parse(data)
        except:
            return None

    if data and data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc)

    return data

def normalizar_noticia(titulo, link, fonte, data, resumo=""):
    data = garantir_timezone(data)

    return {
        "titulo": titulo.strip() if titulo else "",
        "link": link,
        "fonte": fonte,
        "data": data,
        "resumo": resumo.strip() if resumo else ""
    }

# =========================
# FONTES
# =========================

def buscar_coindesk(palavra):
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml"
    noticias = []

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            titulo = entry.title
            link = entry.link
            data = garantir_timezone(entry.get("published"))

            if palavra.lower() in titulo.lower() and dentro_do_periodo(data):
                noticias.append(normalizar_noticia(
                    titulo, link, "CoinDesk", data, entry.get("summary", "")
                ))

    except Exception as e:
        logging.error(f"CoinDesk erro: {e}")

    return noticias


def buscar_google_news(palavra):
    url = f"https://news.google.com/rss/search?q={palavra}+crypto&hl=en-US&gl=US&ceid=US:en"
    noticias = []

    try:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            data = garantir_timezone(entry.get("published"))

            if dentro_do_periodo(data):
                noticias.append(normalizar_noticia(
                    entry.title,
                    entry.link,
                    "Google News",
                    data,
                    entry.get("summary", "")
                ))

    except Exception as e:
        logging.error(f"Google News erro: {e}")

    return noticias


def buscar_theblock(palavra):
    url = f"https://www.theblock.co/search?q={palavra}"
    noticias = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        artigos = soup.select("article")

        for art in artigos:
            try:
                titulo = art.get_text(strip=True)
                link_tag = art.find("a")
                link = "https://www.theblock.co" + link_tag["href"]

                noticias.append(normalizar_noticia(
                    titulo, link, "The Block", agora()
                ))
            except:
                continue

    except Exception as e:
        logging.error(f"The Block erro: {e}")

    return noticias


def buscar_thedefiant(palavra):
    url = f"https://thedefiant.io/search?q={palavra}"
    noticias = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        artigos = soup.select("a")

        for a in artigos:
            titulo = a.get_text(strip=True)
            link = a.get("href")

            if titulo and link and palavra.lower() in titulo.lower():
                noticias.append(normalizar_noticia(
                    titulo, link, "The Defiant", agora()
                ))

    except Exception as e:
        logging.error(f"The Defiant erro: {e}")

    return noticias


def buscar_tradingview(palavra):
    url = f"https://www.tradingview.com/news/?query={palavra}"
    noticias = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        artigos = soup.select("a")

        for a in artigos:
            titulo = a.get_text(strip=True)
            link = a.get("href")

            if titulo and link and palavra.lower() in titulo.lower():
                noticias.append(normalizar_noticia(
                    titulo,
                    "https://www.tradingview.com" + link,
                    "TradingView",
                    agora()
                ))

    except Exception as e:
        logging.error(f"TradingView erro: {e}")

    return noticias

# =========================
# PIPELINE
# =========================

def coletar_noticias_por_ativo(nome, keywords):
    logging.info(f"Coletando notícias para {nome}")
    todas = []
    cache = carregar_cache()

    for palavra in keywords:
        logging.info(f"Buscando: {palavra}")

        fontes = [
            buscar_coindesk,
            buscar_google_news,
            buscar_theblock,
            buscar_thedefiant,
            buscar_tradingview,
        ]

        for fonte in fontes:
            try:
                noticias = fonte(palavra)

                for n in noticias:
                    if not n["link"]:
                        continue

                    h = hash_url(n["link"])

                    if h not in cache:
                        cache[h] = True
                        todas.append(n)

            except Exception as e:
                logging.error(f"Erro na fonte {fonte.__name__}: {e}")

            sleep(1)

    salvar_cache(cache)

    # filtro final + ordenação
    todas = [n for n in todas if dentro_do_periodo(n["data"])]
    todas.sort(key=lambda x: x["data"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    return todas[:LIMITE_POR_ATIVO]

# =========================
# OUTPUT
# =========================

def salvar_md(nome, noticias):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{nome}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"## {nome}\n\n")

        for n in noticias:
            data_str = n["data"].strftime("%Y-%m-%d") if n["data"] else "N/A"

            f.write(f"- [{n['titulo']}]({n['link']})\n")
            f.write(f"  Fonte: {n['fonte']}\n")
            f.write(f"  Data: {data_str}\n")
            f.write(f"  Resumo: {n['resumo']}\n\n")


def salvar_json(nome, noticias):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{nome}.json")

    serializavel = []
    for n in noticias:
        serializavel.append({
            **n,
            "data": n["data"].isoformat() if n["data"] else None
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializavel, f, indent=2, ensure_ascii=False)

# =========================
# MAIN
# =========================

def main():
    for nome, keywords in ATIVOS.items():
        noticias = coletar_noticias_por_ativo(nome, keywords)

        salvar_md(nome, noticias)
        salvar_json(nome, noticias)

        logging.info(f"{nome}: {len(noticias)} notícias salvas")

if __name__ == "__main__":
    main()