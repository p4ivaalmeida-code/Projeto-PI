import os
from pathlib import Path

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from db import get_conn, init_db
from matching import LIMIAR_PADRAO, buscar_similares, normalizar

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR.parent / "Frontend").resolve()

# A partir de quantos % um nome é considerado possível duplicata
LIMIAR = float(os.environ.get("LIMIAR", LIMIAR_PADRAO))

app = Flask(__name__)
CORS(app)


def _registros(conn):
    # Lê todas as empresas do banco (base + cadastros)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, nome_normalizado, criado_em, origem, pais FROM empresas"
    )
    return [dict(r) for r in cur.fetchall()]


# =========================
# FRONTEND
# =========================

@app.get("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.get("/<path:arquivo>")
def arquivos_front(arquivo):
    return send_from_directory(str(FRONTEND_DIR), arquivo)


# =========================
# LISTAR EMPRESAS
# =========================

@app.get("/api/empresas")
def listar_empresas():
    with get_conn() as conn:
        empresas = _registros(conn)

    # Só os cadastros feitos pelo usuário são conferidos contra todos os
    # outros registros (inclusive a base de grandes empresas).
    for emp in empresas:
        emp["duplicada"] = False
        emp["maior_similaridade"] = 0
        emp["parecida_com"] = None
        if emp["origem"] != "cadastro":
            continue
        similares = buscar_similares(
            emp["nome"], empresas, LIMIAR, ignorar_id=emp["id"]
        )
        if similares:
            emp["duplicada"] = True
            emp["maior_similaridade"] = similares[0]["similaridade"]
            emp["parecida_com"] = similares[0]["nome"]

    empresas.sort(key=lambda e: e["id"], reverse=True)
    return jsonify(empresas)


# =========================
# CADASTRAR EMPRESA
# =========================

@app.post("/api/empresas")
def criar_empresa():
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()

    if not nome:
        return jsonify({"error": "Campo 'nome' é obrigatório"}), 400

    nome_norm = normalizar(nome)

    with get_conn() as conn:
        # Confere ANTES de cadastrar: base de grandes empresas + cadastros
        duplicatas = buscar_similares(nome, _registros(conn), LIMIAR)

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO empresas (nome, nome_normalizado, origem) "
            "VALUES (%s, %s, 'cadastro') RETURNING id",
            (nome, nome_norm),
        )
        novo_id = cur.fetchone()["id"]
        conn.commit()

    return jsonify({
        "id": novo_id,
        "nome": nome,
        "nome_normalizado": nome_norm,
        "limiar": LIMIAR,
        "duplicada": len(duplicatas) > 0,
        "possiveis_duplicatas": duplicatas,
    }), 201


# =========================
# RESETAR CADASTROS
# =========================

@app.delete("/api/empresas/reset")
def resetar_empresas():
    # Apaga só os cadastros do usuário; a base de grandes empresas é mantida
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM empresas WHERE origem = 'cadastro'")
        conn.commit()

    return jsonify({
        "message": "Cadastros apagados. A base de grandes empresas foi mantida."
    })


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)