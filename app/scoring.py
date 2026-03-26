from datetime import datetime, timezone

def score_noticia(noticia, keywords):
    score = 0
    texto = (noticia["titulo"] + " " + noticia["resumo"]).lower()

    for k in keywords:
        if k in texto:
            score += 1

    return score

def ordenar_noticias(noticias, keywords):
    return sorted(
        noticias,
        key=lambda x: (
            score_noticia(x, keywords),
            x["data"] or datetime.min.replace(tzinfo=timezone.utc)
        ),
        reverse=True
    )