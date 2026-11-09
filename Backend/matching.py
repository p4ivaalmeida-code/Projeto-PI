import re
import unicodedata

# Palavras que não ajudam a identificar a empresa (formas jurídicas)
SUFIXOS = {
    "inc", "incorporated", "ltd", "ltda", "limited", "llc", "sa", "corp",
    "corporation", "co", "company", "group", "gruppe", "grupo", "holdings",
    "holding", "the", "nv", "bv", "ag", "plc", "gmbh", "spa", "com",
}


def normalizar_simples(nome):
    # Versão antiga: só minúsculas e espaços únicos
    return " ".join(nome.lower().split())


def normalizar(nome):
    # 1) tira acentos e deixa em minúsculas
    texto = unicodedata.normalize("NFKD", nome)
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()

    # 2) "S.A." vira "sa"
    texto = re.sub(r"\bs\.\s?a\.?", " sa ", texto)

    # 3) pontuação vira espaço (ex.: "mercedes-benz" -> "mercedes benz")
    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    # 4) remove as palavras da lista SUFIXOS
    palavras = [p for p in texto.split() if p not in SUFIXOS]
    resultado = " ".join(palavras)

    # se sobrou nada (o nome era só "Inc"), usa a versão simples
    return resultado or normalizar_simples(nome)