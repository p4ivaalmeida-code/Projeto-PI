import os

import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    # O endereço do banco vem da variável DATABASE_URL (a senha não fica no código)
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def init_db():
    # No PostgreSQL a tabela já foi criada pelo script 01_criar_tabela.sql
    pass