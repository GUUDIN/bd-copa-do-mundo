-- =============================================================================
-- SCC0640 – Copa do Mundo FIFA
-- 06.DML.sql – Dados de teste (Gerado por IA)
-- =============================================================================

-- 1. Confederações
INSERT INTO confederacao (nome_confederacao) VALUES
    ('CONMEBOL'),
    ('UEFA'),
    ('CONCACAF'),
    ('CAF'),
    ('AFC'),
    ('OFC');

-- 2. Países
INSERT INTO pais (sigla_pais, nome_pais, id_confederacao) VALUES
    ('BRA', 'Brasil',          1),
    ('ARG', 'Argentina',       1),
    ('GER', 'Alemanha',        2),
    ('FRA', 'França',          2),
    ('USA', 'Estados Unidos',  3),
    ('MEX', 'México',          3),
    ('CAN', 'Canadá',          3),
    ('QAT', 'Catar',           5);

-- 3. Edições da Copa (Inseridas sem campeões por enquanto)
INSERT INTO edicao_da_copa (ano, pais_sede, data_inicio, data_fim) VALUES 
    (2022, 'QAT', '2022-11-20', '2022-12-18'),
    (2026, 'USA', '2026-06-11', '2026-07-19');

-- 4. Cidades Sede
INSERT INTO cidade_sede (cidade, estado) VALUES
    ('Doha', 'QA'),
    ('Al Daayen', 'QA'),
    ('New York', 'NY'),
    ('Los Angeles', 'CA'),
    ('Mexico City', 'CD'),
    ('Toronto', 'ON');

-- 5. Cidades Sediando Edições
INSERT INTO cidade_sedia_edicao (cidade, estado, ano_edicao) VALUES
    ('Doha', 'QA', 2022),
    ('Al Daayen', 'QA', 2022),
    ('New York', 'NY', 2026),
    ('Los Angeles', 'CA', 2026),
    ('Mexico City', 'CD', 2026),
    ('Toronto', 'ON', 2026);

-- 6. Estádios
INSERT INTO estadio (cidade, estado) VALUES
    ('Doha', 'QA'),        -- ID 1 (Ex: Stadium 974)
    ('Al Daayen', 'QA'),   -- ID 2 (Ex: Lusail)
    ('New York', 'NY'),    -- ID 3 (Ex: MetLife)
    ('Mexico City', 'CD'); -- ID 4 (Ex: Azteca)

-- 7. Fases
INSERT INTO fase (tipo_de_fase, ano) VALUES
    ('Fase de Grupos', 2022),
    ('Final', 2022),
    ('Fase de Grupos', 2026),
    ('Oitavas de Final', 2026);

-- 8. Grupos
INSERT INTO grupo (letra_grupo, ano) VALUES
    ('G', 2022),
    ('C', 2022),
    ('D', 2022),
    ('A', 2026),
    ('B', 2026);

-- 9. Técnicos
INSERT INTO tecnico (nome_tecnico) VALUES
    ('Tite'),              -- ID 1
    ('Lionel Scaloni'),    -- ID 2
    ('Didier Deschamps'),  -- ID 3
    ('Dorival Júnior'),    -- ID 4
    ('Gregg Berhalter');   -- ID 5

-- 10. Seleções
INSERT INTO selecao (ano, letra_grupo, id_tecnico, sigla_pais) VALUES
    (2022, 'G', 1, 'BRA'), -- ID 1 (Brasil 2022)
    (2022, 'C', 2, 'ARG'), -- ID 2 (Argentina 2022)
    (2022, 'D', 3, 'FRA'), -- ID 3 (França 2022)
    (2026, 'A', 4, 'BRA'), -- ID 4 (Brasil 2026)
    (2026, 'A', 2, 'ARG'), -- ID 5 (Argentina 2026)
    (2026, 'B', 5, 'USA'); -- ID 6 (EUA 2026)

-- 11. Classificação da Fase de Grupos
INSERT INTO selecao_grupo (id_selecao, ano, letra_grupo, pontos, gols_pro, gols_contra) VALUES
    (4, 2026, 'A', 6, 4, 1), -- Brasil 2026 (Saldo gerado automaticamente: 3)
    (5, 2026, 'A', 3, 2, 2), -- Argentina 2026 (Saldo gerado automaticamente: 0)
    (6, 2026, 'B', 0, 0, 0); -- EUA 2026

-- 12. Jogadores
INSERT INTO jogador (nome_jogador) VALUES
    ('Neymar Jr'),       -- ID 1
    ('Lionel Messi'),    -- ID 2
    ('Kylian Mbappé'),   -- ID 3
    ('Vinícius Júnior'), -- ID 4
    ('Emiliano Martínez');-- ID 5

-- 13. Convocações (O trigger trg_gols_jogador atualizará os gols_marcados automaticamente depois)
INSERT INTO convocacao (ano, id_selecao, id_jogador, numero_camisa) VALUES
    (2022, 1, 1, 10), -- Neymar no BR 2022
    (2022, 2, 2, 10), -- Messi na ARG 2022
    (2022, 2, 5, 23), -- Dibu na ARG 2022
    (2022, 3, 3, 10), -- Mbappé na FRA 2022
    (2026, 4, 4, 7),  -- Vini Jr no BR 2026
    (2026, 5, 2, 10); -- Messi na ARG 2026

-- 14. Atualização dos Campeões da Copa de 2022 (Feito após inserir as seleções)
UPDATE edicao_da_copa 
SET campea = 2, vice_campeao = 3 -- ID 2 = ARG 2022, ID 3 = FRA 2022
WHERE ano = 2022;

-- 15. Árbitros
INSERT INTO arbitro (nome_arbitro) VALUES
    ('Szymon Marciniak'), -- ID 1
    ('Wilton Pereira Sampaio'); -- ID 2

-- 16. Partidas
INSERT INTO partida (
    tipo_de_fase, ano, id_estadio, data_hora, selecao1, selecao2, 
    gols_regulamentares_selecao1, gols_regulamentares_selecao2, 
    gols_prorrogacao_selecao1, gols_prorrogacao_selecao2, 
    gols_penaltis_selecao1, gols_penaltis_selecao2, id_vencedor
) VALUES
    -- Partida 1: Final 2022 (ARG vs FRA) em Lusail (ID 2). ARG ganha nos pênaltis.
    ('Final', 2022, 2, '2022-12-18 18:00:00', 2, 3, 2, 2, 1, 1, 4, 2, 2),
    
    -- Partida 2: Fase de Grupos 2026 (BRA vs ARG) em NY (ID 3). BRA ganha 2x0.
    ('Fase de Grupos', 2026, 3, '2026-06-15 20:00:00', 4, 5, 2, 0, NULL, NULL, NULL, NULL, 4),
    
    -- Partida 3: Partida Futura 2026 (USA vs adversário indefinido simulado)
    ('Fase de Grupos', 2026, 4, '2026-06-20 15:00:00', 6, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- 17. Equipe de Arbitragem
INSERT INTO arbitragem_partida (id_partida, id_arbitro, funcao) VALUES
    (1, 1, 'Principal'),
    (2, 2, 'Principal');

-- 18. Eventos de Jogo (O tipo do campo 'tempo' no seu schema é TIME, por isso o formato 00:MM:SS)
INSERT INTO evento_de_jogo (id_jogador, id_partida, tipo_evento, tempo) VALUES
    -- Eventos da Final de 2022 (ARG vs FRA)
    (2, 1, 'Pênalti Convertido', '00:23:00'), -- Messi (ARG)
    (3, 1, 'Pênalti Convertido', '01:20:00'), -- Mbappé (FRA)
    (3, 1, 'Gol',                '01:21:00'), -- Mbappé (FRA)
    (2, 1, 'Gol',                '01:48:00'), -- Messi (ARG) prorrog. (simulado como 108 min)
    (3, 1, 'Pênalti Convertido', '01:58:00'), -- Mbappé (FRA) prorrog.
    
    -- Eventos da Fase de Grupos 2026 (BRA vs ARG)
    (4, 2, 'Gol',                '00:15:00'), -- Vini Jr (BRA)
    (2, 2, 'Cartão Amarelo',     '00:45:00'); -- Messi (ARG)