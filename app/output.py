import os
import json
from app.config import OUTPUT_DIR

def salvar_md(nome, noticias):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(f"{OUTPUT_DIR}/{nome}.md", "w", encoding="utf-8") as f:
        f.write(f"## {nome}\n\n")

        for n in noticias:
            data_str = n["data"].strftime("%Y-%m-%d") if n["data"] else "N/A"

            f.write(f"- [{n['titulo']}]({n['link']})\n")
            f.write(f"  Fonte: {n['fonte']}\n")
            f.write(f"  Data: {data_str}\n")
            f.write(f"  Resumo: {n['resumo']}\n\n")


def salvar_json(nome, noticias):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    serializavel = [
        {**n, "data": n["data"].isoformat() if n["data"] else None}
        for n in noticias
    ]

    with open(f"{OUTPUT_DIR}/{nome}.json", "w", encoding="utf-8") as f:
        json.dump(serializavel, f, indent=2, ensure_ascii=False)