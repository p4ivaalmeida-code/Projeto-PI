from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request

from db import get_conn, init_db

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR.parent / "Frontend").resolve()

app = Flask(__name__)

@app.get("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

@app.get("/<path:arquivo>")
def arquivos_front(arquivo):
    return send_from_directory(str(FRONTEND_DIR), arquivo)

@app.get("/api/empresas")
def listar_empresas():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, nome, nome_normalizado, criado_em FROM empresas ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/empresas")
def criar_empresa():
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    if not nome:
        return jsonify({"error": "Campo 'nome' é obrigatório"}), 400

    nome_norm = " ".join(nome.lower().split())

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO empresas (nome, nome_normalizado) VALUES (?, ?)",
            (nome, nome_norm),
        )
        conn.commit()

    return jsonify({"id": cur.lastrowid, "nome": nome, "nome_normalizado": nome_norm}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)