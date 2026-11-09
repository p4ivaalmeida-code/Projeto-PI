import re
import unicodedata
from difflib import SequenceMatcher

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

# A partir de quantos % o nome é considerado parecido
LIMIAR_PADRAO = 70.0


def similaridade(a, b):
    # Compara dois nomes já normalizados e devolve um número de 0 a 100
    if not a or not b:
        return 0.0
    return round(SequenceMatcher(None, a, b).ratio() * 100, 2)


def buscar_similares(nome, registros, limiar=LIMIAR_PADRAO, ignorar_id=None):
    # Compara "nome" com cada empresa da lista e devolve as parecidas
    alvo = normalizar(nome)
    encontrados = []
    for reg in registros:
        if ignorar_id is not None and reg["id"] == ignorar_id:
            continue
        score = similaridade(alvo, normalizar(reg["nome"]))
        if score >= limiar:
            encontrados.append({
                "id": reg["id"],
                "nome": reg["nome"],
                "origem": reg["origem"],
                "pais": reg["pais"],
                "similaridade": score,
            })
    encontrados.sort(key=lambda r: r["similaridade"], reverse=True)
    return encontrados

