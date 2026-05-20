from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from db import get_conn, init_db

import difflib
import os

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR.parent / "Frontend").resolve()

app = Flask(__name__)
CORS(app)


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

        rows = conn.execute("""
            SELECT
                id,
                nome,
                nome_normalizado,
                criado_em
            FROM empresas
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(r) for r in rows])


# =========================
# CADASTRAR EMPRESA
# =========================

@app.post("/api/empresas")
def criar_empresa():

    data = request.get_json(silent=True) or {}

    nome = (data.get("nome") or "").strip()

    if not nome:
        return jsonify({
            "error": "Campo 'nome' é obrigatório"
        }), 400

    # normalização
    nome_norm = " ".join(nome.lower().split())

    with get_conn() as conn:

        empresas = conn.execute("""
            SELECT
                id,
                nome,
                nome_normalizado
            FROM empresas
        """).fetchall()

        duplicatas = []

        for emp in empresas:

            score = difflib.SequenceMatcher(
                None,
                nome_norm,
                emp["nome_normalizado"]
            ).ratio()

            similaridade = round(score * 100, 2)

            # empresas similares acima de 70%
            if similaridade >= 55:

                duplicatas.append({
                    "id": emp["id"],
                    "nome": emp["nome"],
                    "nome_normalizado": emp["nome_normalizado"],
                    "similaridade": similaridade
                })

        # cadastra normalmente
        cur = conn.execute("""
            INSERT INTO empresas (
                nome,
                nome_normalizado
            )
            VALUES (?, ?)
        """, (nome, nome_norm))

        conn.commit()

    return jsonify({

        "id": cur.lastrowid,
        "nome": nome,
        "nome_normalizado": nome_norm,

        "duplicada": len(duplicatas) > 0,

        "possiveis_duplicatas": duplicatas

    }), 201


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    init_db()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
