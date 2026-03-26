import logging
from app.config import ATIVOS, LIMITE_POR_ATIVO
from app.pipeline import coletar_noticias
from app.output import salvar_md, salvar_json

logging.basicConfig(level=logging.INFO)

def main():
    for nome, keywords in ATIVOS.items():
        logging.info(f"Processando {nome}")

        noticias = coletar_noticias(nome, keywords, LIMITE_POR_ATIVO)

        salvar_md(nome, noticias)
        salvar_json(nome, noticias)

        logging.info(f"{nome}: {len(noticias)} notícias")


if __name__ == "__main__":
    main()