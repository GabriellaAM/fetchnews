import feedparser
from app.utils import (
    normalizar_noticia,
    garantir_timezone,
    dentro_do_periodo,
    contem_keyword,
)

def buscar(palavra):
    url = f"https://news.google.com/rss/search?q={palavra}+crypto"
    noticias = []

    feed = feedparser.parse(url)

    for entry in feed.entries:
        data = garantir_timezone(entry.get("published"))

        titulo = entry.title
        resumo = entry.get("summary", "")

        texto = f"{titulo} {resumo}"

        if not contem_keyword(texto, [palavra]):
            continue

        if dentro_do_periodo(data):
            noticias.append(normalizar_noticia(
                titulo,
                entry.link,
                "Google News",
                data,
                resumo
            ))

    return noticias