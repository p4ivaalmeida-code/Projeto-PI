-- Base de referência: grandes empresas já "cadastradas".
-- Pode rodar de novo: apaga a base antiga antes de inserir.
DELETE FROM empresas WHERE origem = 'base';

INSERT INTO empresas (nome, nome_normalizado, origem, pais, fonte) VALUES
('Amazon', 'amazon', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('Walmart', 'walmart', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('State Grid Corporation of China', 'state grid corporation of china', 'base', 'China', 'Fortune Global 500 2026'),
('UnitedHealth Group', 'unitedhealth group', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('Saudi Aramco', 'saudi aramco', 'base', 'Arábia Saudita', 'Fortune Global 500 2026'),
('Apple', 'apple', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('McKesson', 'mckesson', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('Alphabet', 'alphabet', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('CVS Health', 'cvs health', 'base', 'Estados Unidos', 'Fortune Global 500 2026'),
('China National Petroleum Corporation', 'china national petroleum corporation', 'base', 'China', 'Fortune Global 500 2026');