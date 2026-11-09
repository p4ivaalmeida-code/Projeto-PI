from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from db import get_conn, init_db

from difflib import SequenceMatcher

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

    return send_from_directory(
        str(FRONTEND_DIR),
        "index.html"
    )


@app.get("/<path:arquivo>")
def arquivos_front(arquivo):

    return send_from_directory(
        str(FRONTEND_DIR),
        arquivo
    )


# =========================
# LISTAR EMPRESAS
# =========================

@app.get("/api/empresas")
def listar_empresas():

    with get_conn() as conn:

        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                id,
                nome,
                nome_normalizado,
                criado_em,
                origem,
                pais
            FROM empresas
            ORDER BY id DESC
            """
        )

        rows = cur.fetchall()

    empresas = [dict(r) for r in rows]

    # =========================
    # VERIFICA SIMILARIDADE
    # =========================

    for empresa in empresas:

        empresa["duplicada"] = False
        empresa["maior_similaridade"] = 0

        for outra in empresas:

            if empresa["id"] == outra["id"]:
                continue

            similaridade = SequenceMatcher(
                None,
                empresa["nome_normalizado"],
                outra["nome_normalizado"]
            ).ratio()

            similaridade_percentual = round(
                similaridade * 100,
                2
            )

            if similaridade_percentual >= 60:

                empresa["duplicada"] = True

                if (
                    similaridade_percentual >
                    empresa["maior_similaridade"]
                ):

                    empresa["maior_similaridade"] = (
                        similaridade_percentual
                    )

    return jsonify(empresas)


# =========================
# CADASTRAR EMPRESA
# =========================

@app.post("/api/empresas")
def criar_empresa():

    data = request.get_json(
        silent=True
    ) or {}

    nome = (
        data.get("nome") or ""
    ).strip()

    if not nome:

        return jsonify({
            "error":
            "Campo 'nome' é obrigatório"
        }), 400

    # NORMALIZAÇÃO

    nome_norm = " ".join(
        nome.lower().split()
    )

    with get_conn() as conn:

        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                id,
                nome,
                nome_normalizado
            FROM empresas
            """
        )

        empresas = cur.fetchall()

        duplicatas = []

        for emp in empresas:

            score = difflib.SequenceMatcher(
                None,
                nome_norm,
                emp["nome_normalizado"]
            ).ratio()

            similaridade = round(
                score * 100,
                2
            )

            # EMPRESAS SIMILARES

            if similaridade >= 55:

                duplicatas.append({

                    "id":
                    emp["id"],

                    "nome":
                    emp["nome"],

                    "nome_normalizado":
                    emp["nome_normalizado"],

                    "similaridade":
                    similaridade
                })

        # CADASTRA NORMALMENTE

        cur.execute(
            """
            INSERT INTO empresas (
                nome,
                nome_normalizado,
                origem
            )
            VALUES (%s, %s, 'cadastro')
            RETURNING id
            """,
            (
                nome,
                nome_norm
            )
        )

        novo_id = cur.fetchone()["id"]

        conn.commit()

    return jsonify({

        "id":
        novo_id,

        "nome":
        nome,

        "nome_normalizado":
        nome_norm,

        "duplicada":
        len(duplicatas) > 0,

        "possiveis_duplicatas":
        duplicatas

    }), 201


# =========================
# RESETAR CADASTROS
# =========================

@app.delete("/api/empresas/reset")
def resetar_empresas():

    # Apaga só os cadastros feitos pelo usuário.
    # A base de grandes empresas (origem = 'base') é mantida.

    with get_conn() as conn:

        cur = conn.cursor()

        cur.execute(
            "DELETE FROM empresas WHERE origem = 'cadastro'"
        )

        conn.commit()

    return jsonify({
        "message":
        "Cadastros apagados. A base de grandes empresas foi mantida."
    })


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    init_db()

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )