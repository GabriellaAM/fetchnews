import requests
from app.utils import (
    normalizar_noticia,
    garantir_timezone,
    dentro_do_periodo,
    contem_keyword,
)

def buscar(palavra):
    noticias = []

    try:
        url = "https://cryptocurrency.cv/api/news"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()

        if not isinstance(data, list):
            return []

        for item in data:

            if not isinstance(item, dict):
                continue

            titulo = item.get("title", "")
            resumo = item.get("summary", "")

            texto = f"{titulo} {resumo}"

            # 🔥 filtro melhor
            if not contem_keyword(texto, [palavra]):
                continue

            data_pub = garantir_timezone(item.get("published_at"))

            if dentro_do_periodo(data_pub):
                noticias.append(normalizar_noticia(
                    titulo,
                    item.get("url"),
                    item.get("source", "FreeAPI"),
                    data_pub,
                    resumo
                ))

    except Exception as e:
        print(f"Erro Free API: {e}")

    return noticias