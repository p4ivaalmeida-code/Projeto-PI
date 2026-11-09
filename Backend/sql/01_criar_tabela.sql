CREATE TABLE IF NOT EXISTS empresas (
  id SERIAL PRIMARY KEY,
  nome TEXT NOT NULL,
  nome_normalizado TEXT NOT NULL,
  criado_em TIMESTAMP NOT NULL DEFAULT now(),
  origem TEXT NOT NULL DEFAULT 'cadastro' CHECK (origem IN ('base', 'cadastro')),
  pais TEXT,
  fonte TEXT
);

CREATE INDEX IF NOT EXISTS idx_empresas_nome_normalizado
  ON empresas (nome_normalizado);