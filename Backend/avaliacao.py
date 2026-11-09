import random

from db import get_conn
from matching import normalizar, similaridade

random.seed(42)  # mesma semente = sempre os mesmos casos de teste

# Nomes que NÃO são duplicata de nenhuma empresa da base
NOMES_DIFERENTES = [
    "Padaria do Joao", "Mercadinho Boa Vista", "Oficina Silva e Filhos",
    "Farmacia Sao Jose", "Pizzaria Bella Napoli", "Auto Pecas Central",
    "Studio Bela Forma", "Livraria Pagina Um", "Lanchonete do Zeca",
    "Construtora Horizonte", "Tech Solutions Brasil", "Distribuidora Santa Clara",
    "Clinica Vida Plena", "Papelaria Ponto Certo", "Transportes Rapido Sul",
    "Barbearia do Marcos", "Escola Aprender Mais", "Floricultura Jardim",
    "Academia Corpo em Forma", "Hortifruti Sabor da Terra",
]


def carregar_base():
    # Lê do banco as empresas grandes (origem = 'base')
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT nome FROM empresas WHERE origem = 'base' ORDER BY id")
        return [r["nome"] for r in cur.fetchall()]


def erro_de_digitacao(nome):
    # Apaga, troca ou duplica uma letra do nome
    posicoes = [i for i, c in enumerate(nome) if c.isalpha() and i > 0]
    i = random.choice(posicoes)
    tipo = random.choice(["apagar", "trocar", "duplicar"])
    if tipo == "apagar":
        return nome[:i] + nome[i + 1:]
    if tipo == "trocar":
        return nome[:i] + random.choice("abcdefghijklmnopqrstuvwxyz") + nome[i + 1:]
    return nome[:i] + nome[i] + nome[i:]


def gerar_positivos(nome):
    # Versões "erradas" da mesma empresa (devem ser achadas como duplicata)
    return [
        ("erro de digitacao", erro_de_digitacao(nome)),
        ("erro de digitacao", erro_de_digitacao(nome)),
        ("sufixo juridico", nome + random.choice([" Inc.", " Ltd", " S.A.", " Corp"])),
        ("maiusculas", nome.upper()),
    ]


def montar_casos(base):
    casos = []  # cada caso: (texto, e_duplicata, tipo)
    for nome in base:
        for tipo, texto in gerar_positivos(nome):
            casos.append((texto, True, tipo))
    for texto in NOMES_DIFERENTES:
        casos.append((texto, False, "empresa diferente"))
    return casos


if __name__ == "__main__":
    base = carregar_base()
    casos = montar_casos(base)
    positivos = sum(1 for c in casos if c[1])
    print(f"Base: {len(base)} empresas")
    print(f"Casos de teste: {len(casos)} ({positivos} duplicatas, {len(casos) - positivos} diferentes)")
    for texto, duplicata, tipo in casos[:8]:
        print(f"  {texto!r:45} {tipo}")

def melhor_nota(texto, base):
    notas = [similaridade(normalizar(texto), normalizar(empresa)) for empresa in base]
    return max(notas)

if __name__ == "__main__":
    print()
    print("Notas de alguns casos:")
    for texto, duplicata, tipo in montar_casos(carregar_base())[:8]:
        print(f"  {texto!r:25} nota = {melhor_nota(texto, carregar_base())}")
    print(f"  {'Padaria do Joao'!r:25} nota = {melhor_nota('Padaria do Joao', carregar_base())}")