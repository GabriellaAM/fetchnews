from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
from bs4 import BeautifulSoup
import hashlib
import json
import os
from app.config import DIAS, CACHE_FILE

def agora():
    return datetime.now(timezone.utc)

def dentro_do_periodo(data):
    return data and data >= agora() - timedelta(days=DIAS)

def garantir_timezone(data):
    if not data:
        return None

    if isinstance(data, str):
        try:
            data = dateparser.parse(data)
        except:
            return None

    if data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc)

    return data

def limpar_html(texto):
    if not texto:
        return ""
    return BeautifulSoup(texto, "html.parser").get_text(" ", strip=True)

def hash_noticia(titulo, resumo):
    base = (titulo + resumo).lower()
    return hashlib.md5(base.encode()).hexdigest()

def carregar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def normalizar_noticia(titulo, link, fonte, data, resumo=""):
    return {
        "titulo": titulo.strip() if titulo else "",
        "link": link,
        "fonte": fonte,
        "data": garantir_timezone(data),
        "resumo": limpar_html(resumo)
    }

def contem_keyword(texto, keywords):
    if not texto:
        return False

    texto = texto.lower()
    return any(k in texto for k in keywords)