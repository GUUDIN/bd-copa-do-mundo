-- =============================================================================
-- SCC0640 – Copa do Mundo FIFA
-- 06.DML.sql – Dados de teste (gerado com IA)
-- =============================================================================
-- TODO: inserir dados para a Copa 2026 (EUA/Canadá/México) e copas históricas.
-- Este arquivo deve ser preenchido pelo grupo usando IA (ex.: ChatGPT/Claude)
-- conforme indicado no item 6 do enunciado.
-- =============================================================================

-- Exemplo mínimo de estrutura:

-- Confederações
INSERT INTO confederacao (nome_confederacao) VALUES
    ('CONMEBOL'),
    ('UEFA'),
    ('CONCACAF'),
    ('CAF'),
    ('AFC'),
    ('OFC');

-- Países (amostra)
INSERT INTO pais (sigla_pais, nome_pais, id_confederacao) VALUES
    ('BRA', 'Brasil',          1),
    ('ARG', 'Argentina',       1),
    ('GER', 'Alemanha',        2),
    ('FRA', 'França',          2),
    ('USA', 'Estados Unidos',  3),
    ('MEX', 'México',          3);

-- Edição 2026
INSERT INTO edicao_da_copa (ano, pais_sede, data_inicio, data_fim)
VALUES (2026, 'USA', '2026-06-11', '2026-07-19');

-- ... completar com dados reais
