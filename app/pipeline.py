from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils import carregar_cache, salvar_cache, hash_noticia, dentro_do_periodo
from app.scoring import ordenar_noticias

from app.sources import (
    buscar_coindesk,
    buscar_google_news,
    buscar_free_api,
    buscar_theblock,
    buscar_thedefiant,
)

FONTES = [
    buscar_free_api,
    buscar_coindesk,
    buscar_theblock,
    buscar_thedefiant,
    buscar_google_news,
]

def coletar_fontes_paralelo(palavra):
    resultados = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(f, palavra) for f in FONTES]

        for future in as_completed(futures):
            try:
                resultados.extend(future.result())
            except:
                pass

    return resultados


def coletar_noticias(nome, keywords, limite):
    cache = carregar_cache()
    todas = []

    for palavra in keywords:
        noticias = coletar_fontes_paralelo(palavra)

        for n in noticias:
            if not n["link"]:
                continue

            h = hash_noticia(n["titulo"], n["resumo"])

            if h not in cache:
                cache[h] = True
                todas.append(n)

    salvar_cache(cache)

    print(f"{nome} total bruto: {len(todas)}")

    todas = [n for n in todas if dentro_do_periodo(n["data"])]

    return ordenar_noticias(todas, keywords)[:limite]