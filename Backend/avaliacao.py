import random

from db import get_conn
from matching import normalizar, similaridade

random.seed(42)  # fixa o sorteio: toda vez que rodar, os casos de teste são os mesmos

# Nomes que NÃO são duplicatas de nenhuma empresa grande
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
    # Pega do banco os nomes das empresas grandes (origem = 'base')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nome FROM empresas WHERE origem = 'base' ORDER BY id")
            return [linha["nome"] for linha in cur.fetchall()]


def erro_de_digitacao(nome):
    # Apaga, troca ou duplica uma letra em uma posição sorteada
    pos = random.randint(1, len(nome) - 1)
    tipo = random.choice(["apagar", "trocar", "duplicar"])
    if tipo == "apagar":
        return nome[:pos] + nome[pos + 1:]
    if tipo == "trocar":
        return nome[:pos] + random.choice("abcdefghijklmnopqrstuvwxyz") + nome[pos + 1:]
    return nome[:pos] + nome[pos] + nome[pos:]


def gerar_positivos(nome):
    # 4 variações de uma empresa da base que DEVEM ser detectadas como duplicata
    return [
        (erro_de_digitacao(nome), "erro de digitacao"),
        (erro_de_digitacao(nome), "erro de digitacao"),
        (nome + random.choice([" Inc.", " Ltd", " S.A.", " Corp"]), "sufixo juridico"),
        (nome.upper(), "maiusculas"),
    ]


def montar_casos(base):
    # Lista de (texto, e_duplicata, tipo): 4 por empresa da base + os nomes diferentes
    casos = []
    for nome in base:
        for texto, tipo in gerar_positivos(nome):
            casos.append((texto, True, tipo))
    for nome in NOMES_DIFERENTES:
        casos.append((nome, False, "nome diferente"))
    return casos


def melhor_nota(texto, base):
    # Compara o texto com TODAS as empresas da base e devolve a maior nota
    notas = [similaridade(normalizar(texto), normalizar(empresa)) for empresa in base]
    return max(notas)


def contar(pontuados, corte):
    acertos = sum(1 for t, dup, nota in pontuados if dup and nota >= corte)
    perdidos = sum(1 for t, dup, nota in pontuados if dup and nota < corte)
    alarmes = sum(1 for t, dup, nota in pontuados if not dup and nota >= corte)
    precisao = acertos / (acertos + alarmes) if (acertos + alarmes) else 0
    recall = acertos / (acertos + perdidos) if (acertos + perdidos) else 0
    f1 = 2 * precisao * recall / (precisao + recall) if (precisao + recall) else 0
    return acertos, alarmes, perdidos, precisao, recall, f1


if __name__ == "__main__":
    base = carregar_base()
    casos = montar_casos(base)
    positivos = sum(1 for c in casos if c[1])
    print(f"Base: {len(base)} empresas")
    print(f"Casos de teste: {len(casos)} ({positivos} duplicatas, {len(casos) - positivos} diferentes)")

    pontuados = [(t, dup, melhor_nota(t, base)) for t, dup, tipo in casos]
    print()
    print("corte | acertos | alarmes falsos | perdidos | precisao | recall |   F1")
    for corte in range(50, 100, 5):
        a, al, p, prec, rec, f1 = contar(pontuados, corte)
        print(f"{corte:5} | {a:7} | {al:14} | {p:8} | {prec:8.2f} | {rec:6.2f} | {f1:.2f}")