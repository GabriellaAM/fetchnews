import feedparser
from app.utils import (
    normalizar_noticia,
    garantir_timezone,
    dentro_do_periodo,
    contem_keyword,
)

def buscar(palavra):
    url = "https://thedefiant.io/rss.xml"
    noticias = []

    feed = feedparser.parse(url)

    for entry in feed.entries:
        titulo = entry.title
        resumo = entry.get("summary", "")
        data = garantir_timezone(entry.get("published"))

        texto = f"{titulo} {resumo}"

        if not contem_keyword(texto, [palavra]):
            continue

        if dentro_do_periodo(data):
            noticias.append(normalizar_noticia(
                titulo,
                entry.link,
                "The Defiant",
                data,
                resumo
            ))

    return noticias