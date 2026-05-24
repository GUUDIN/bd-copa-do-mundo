-- =============================================================================
-- SCC0640 – Copa do Mundo FIFA
-- 06.DML.sql – Dados de teste (gerado por IA com revisão humana)
-- Cobre 3 edições (1998, 2022, 2026), 24 países, 36 seleções e múltiplas
-- partidas/eventos suficientes para demonstrar todas as 10 consultas.
-- =============================================================================

-- =============================================================================
-- 1. CONFEDERAÇÕES (6)
-- =============================================================================
INSERT INTO confederacao (nome_confederacao) VALUES
    ('CONMEBOL'),  -- 1
    ('UEFA'),      -- 2
    ('CONCACAF'),  -- 3
    ('CAF'),       -- 4
    ('AFC'),       -- 5
    ('OFC');       -- 6

-- =============================================================================
-- 2. PAÍSES (24)
-- =============================================================================
INSERT INTO pais (sigla_pais, nome_pais, id_confederacao) VALUES
    ('BRA', 'Brasil',         1),
    ('ARG', 'Argentina',      1),
    ('URU', 'Uruguai',        1),
    ('GER', 'Alemanha',       2),
    ('FRA', 'França',         2),
    ('ENG', 'Inglaterra',     2),
    ('ITA', 'Itália',         2),
    ('ESP', 'Espanha',        2),
    ('POR', 'Portugal',       2),
    ('NED', 'Holanda',        2),
    ('BEL', 'Bélgica',        2),
    ('CRO', 'Croácia',        2),
    ('DEN', 'Dinamarca',      2),
    ('NOR', 'Noruega',        2),
    ('USA', 'Estados Unidos', 3),
    ('MEX', 'México',         3),
    ('CAN', 'Canadá',         3),
    ('QAT', 'Catar',          5),
    ('JPN', 'Japão',          5),
    ('AUS', 'Austrália',      5),
    ('MAR', 'Marrocos',       4),
    ('SEN', 'Senegal',        4),
    ('CMR', 'Camarões',       4),
    ('NZL', 'Nova Zelândia',  6);

-- =============================================================================
-- 3. TÉCNICOS (32)
-- =============================================================================
INSERT INTO tecnico (nome_tecnico) VALUES
    ('Aimé Jacquet'),         -- 1   FRA 1998
    ('Bo Johansson'),         -- 2   DEN 1998
    ('Mário Zagallo'),        -- 3   BRA 1998
    ('Egil Olsen'),           -- 4   NOR 1998
    ('Guus Hiddink'),         -- 5   NED 1998 (e reutilizado)
    ('Georges Leekens'),      -- 6   BEL 1998
    ('Daniel Passarella'),    -- 7   ARG 1998
    ('Takeshi Okada'),        -- 8   JPN 1998
    ('Cesare Maldini'),       -- 9   ITA 1998
    ('Steve Sampson'),        -- 10  USA 1998
    ('Miroslav Blažević'),    -- 11  CRO 1998
    ('Henri Michel'),         -- 12  MAR 1998
    ('Tite'),                 -- 13  (reservado)
    ('Lionel Scaloni'),       -- 14  ARG 2022 + ARG 2026
    ('Didier Deschamps'),     -- 15  FRA 2022 + FRA 2026
    ('Zlatko Dalić'),         -- 16  CRO 2022
    ('Walid Regragui'),       -- 17  MAR 2022
    ('Hansi Flick'),          -- 18  GER 2022 + GER 2026
    ('Luis Enrique'),         -- 19  ESP 2022
    ('Gareth Southgate'),     -- 20  ENG 2022
    ('Félix Sánchez'),        -- 21  QAT 2022
    ('Tata Martino'),         -- 22  MEX 2022
    ('Graham Arnold'),        -- 23  AUS 2022
    ('Gregg Berhalter'),      -- 24  USA 2022 + USA 2026
    ('Dorival Júnior'),       -- 25  BRA 2026
    ('Jesse Marsch'),         -- 26  CAN 2026
    ('Hajime Moriyasu'),      -- 27  JPN 2026
    ('Javier Aguirre'),       -- 28  MEX 2026
    ('Roberto Martínez'),     -- 29  POR 2026
    ('Ronald Koeman'),        -- 30  NED 2026
    ('Luis de la Fuente'),    -- 31  ESP 2026
    ('Thomas Tuchel');        -- 32  ENG 2026

-- =============================================================================
-- 4. EDIÇÕES DA COPA (3) — campeões serão definidos por UPDATE no final
-- =============================================================================
INSERT INTO edicao_da_copa (ano, pais_sede, data_inicio, data_fim) VALUES
    (1998, 'FRA', '1998-06-10', '1998-07-12'),
    (2022, 'QAT', '2022-11-20', '2022-12-18'),
    (2026, 'USA', '2026-06-11', '2026-07-19');

-- =============================================================================
-- 5. CIDADES SEDE (11)
-- =============================================================================
INSERT INTO cidade_sede (cidade, estado) VALUES
    ('Paris',       'FR'),
    ('Marseille',   'FR'),
    ('Lyon',        'FR'),
    ('Doha',        'QA'),
    ('Al Daayen',   'QA'),
    ('Al Khor',     'QA'),
    ('New York',    'NY'),
    ('Los Angeles', 'CA'),
    ('Mexico City', 'CD'),
    ('Toronto',     'ON'),
    ('Dallas',      'TX');

-- =============================================================================
-- 6. CIDADES SEDIANDO EDIÇÕES (11)
-- =============================================================================
INSERT INTO cidade_sedia_edicao (cidade, estado, ano_edicao) VALUES
    ('Paris',       'FR', 1998),
    ('Marseille',   'FR', 1998),
    ('Lyon',        'FR', 1998),
    ('Doha',        'QA', 2022),
    ('Al Daayen',   'QA', 2022),
    ('Al Khor',     'QA', 2022),
    ('New York',    'NY', 2026),
    ('Los Angeles', 'CA', 2026),
    ('Mexico City', 'CD', 2026),
    ('Toronto',     'ON', 2026),
    ('Dallas',      'TX', 2026);

-- =============================================================================
-- 7. ESTÁDIOS (11) — IDs SERIAL 1..11
-- =============================================================================
INSERT INTO estadio (cidade, estado) VALUES
    ('Paris',       'FR'),  -- 1  Stade de France
    ('Marseille',   'FR'),  -- 2  Vélodrome
    ('Lyon',        'FR'),  -- 3  Gerland
    ('Doha',        'QA'),  -- 4  Stadium 974
    ('Al Daayen',   'QA'),  -- 5  Lusail
    ('Al Khor',     'QA'),  -- 6  Al Bayt
    ('New York',    'NY'),  -- 7  MetLife
    ('Los Angeles', 'CA'),  -- 8  SoFi
    ('Mexico City', 'CD'),  -- 9  Azteca
    ('Toronto',     'ON'),  -- 10 BMO Field
    ('Dallas',      'TX');  -- 11 AT&T Stadium

-- =============================================================================
-- 8. FASES (6 × 3 = 18)
-- =============================================================================
INSERT INTO fase (tipo_de_fase, ano) VALUES
    ('Fase de Grupos',             1998),
    ('Oitavas de Final',           1998),
    ('Quartas de Final',           1998),
    ('Semifinais',                 1998),
    ('Disputa de Terceiro Lugar',  1998),
    ('Final',                      1998),
    ('Fase de Grupos',             2022),
    ('Oitavas de Final',           2022),
    ('Quartas de Final',           2022),
    ('Semifinais',                 2022),
    ('Disputa de Terceiro Lugar',  2022),
    ('Final',                      2022),
    ('Fase de Grupos',             2026),
    ('Oitavas de Final',           2026),
    ('Quartas de Final',           2026),
    ('Semifinais',                 2026),
    ('Disputa de Terceiro Lugar',  2026),
    ('Final',                      2026);

-- =============================================================================
-- 9. GRUPOS (6 × 3 = 18)
-- =============================================================================
INSERT INTO grupo (letra_grupo, ano) VALUES
    ('A', 1998), ('B', 1998), ('C', 1998), ('D', 1998), ('E', 1998), ('F', 1998),
    ('A', 2022), ('B', 2022), ('C', 2022), ('D', 2022), ('E', 2022), ('F', 2022),
    ('A', 2026), ('B', 2026), ('C', 2026), ('D', 2026), ('E', 2026), ('F', 2026);

-- =============================================================================
-- 10. SELEÇÕES (36) — IDs SERIAL: 1998=1..12, 2022=13..24, 2026=25..36
-- =============================================================================
INSERT INTO selecao (ano, letra_grupo, id_tecnico, sigla_pais) VALUES
    -- 1998
    (1998, 'A', 1,  'FRA'),   -- 1  FRA 1998
    (1998, 'A', 2,  'DEN'),   -- 2  DEN 1998
    (1998, 'B', 3,  'BRA'),   -- 3  BRA 1998
    (1998, 'B', 4,  'NOR'),   -- 4  NOR 1998
    (1998, 'C', 5,  'NED'),   -- 5  NED 1998
    (1998, 'C', 6,  'BEL'),   -- 6  BEL 1998
    (1998, 'D', 7,  'ARG'),   -- 7  ARG 1998
    (1998, 'D', 8,  'JPN'),   -- 8  JPN 1998
    (1998, 'E', 9,  'ITA'),   -- 9  ITA 1998
    (1998, 'E', 10, 'USA'),   -- 10 USA 1998
    (1998, 'F', 11, 'CRO'),   -- 11 CRO 1998
    (1998, 'F', 12, 'MAR'),   -- 12 MAR 1998
    -- 2022
    (2022, 'A', 21, 'QAT'),   -- 13 QAT 2022
    (2022, 'A', 5,  'NED'),   -- 14 NED 2022
    (2022, 'B', 20, 'ENG'),   -- 15 ENG 2022
    (2022, 'B', 24, 'USA'),   -- 16 USA 2022
    (2022, 'C', 14, 'ARG'),   -- 17 ARG 2022
    (2022, 'C', 22, 'MEX'),   -- 18 MEX 2022
    (2022, 'D', 15, 'FRA'),   -- 19 FRA 2022
    (2022, 'D', 23, 'AUS'),   -- 20 AUS 2022
    (2022, 'E', 19, 'ESP'),   -- 21 ESP 2022
    (2022, 'E', 18, 'GER'),   -- 22 GER 2022
    (2022, 'F', 16, 'CRO'),   -- 23 CRO 2022
    (2022, 'F', 17, 'MAR'),   -- 24 MAR 2022
    -- 2026
    (2026, 'A', 24, 'USA'),   -- 25 USA 2026
    (2026, 'A', 28, 'MEX'),   -- 26 MEX 2026
    (2026, 'B', 26, 'CAN'),   -- 27 CAN 2026
    (2026, 'B', 27, 'JPN'),   -- 28 JPN 2026
    (2026, 'C', 25, 'BRA'),   -- 29 BRA 2026
    (2026, 'C', 14, 'ARG'),   -- 30 ARG 2026
    (2026, 'D', 15, 'FRA'),   -- 31 FRA 2026
    (2026, 'D', 18, 'GER'),   -- 32 GER 2026
    (2026, 'E', 32, 'ENG'),   -- 33 ENG 2026
    (2026, 'E', 31, 'ESP'),   -- 34 ESP 2026
    (2026, 'F', 29, 'POR'),   -- 35 POR 2026
    (2026, 'F', 30, 'NED');   -- 36 NED 2026

-- =============================================================================
-- 11. CLASSIFICAÇÃO NA FASE DE GRUPOS
-- =============================================================================
INSERT INTO selecao_grupo (id_selecao, ano, letra_grupo, pontos, gols_pro, gols_contra) VALUES
    -- 1998
    (1,  1998, 'A', 3, 2, 0),  -- FRA
    (2,  1998, 'A', 0, 0, 2),  -- DEN
    (3,  1998, 'B', 3, 2, 1),  -- BRA
    (4,  1998, 'B', 0, 1, 2),  -- NOR
    (5,  1998, 'C', 3, 3, 0),  -- NED
    (6,  1998, 'C', 0, 0, 3),  -- BEL
    (7,  1998, 'D', 3, 1, 0),  -- ARG
    (8,  1998, 'D', 0, 0, 1),  -- JPN
    (9,  1998, 'E', 1, 2, 2),  -- ITA
    (10, 1998, 'E', 1, 2, 2),  -- USA
    (11, 1998, 'F', 3, 3, 0),  -- CRO
    (12, 1998, 'F', 0, 0, 3),  -- MAR
    -- 2022
    (13, 2022, 'A', 0, 1, 7),  -- QAT
    (14, 2022, 'A', 6, 5, 1),  -- NED
    (15, 2022, 'B', 3, 6, 2),  -- ENG
    (16, 2022, 'B', 0, 1, 3),  -- USA
    (17, 2022, 'C', 6, 5, 2),  -- ARG
    (18, 2022, 'C', 0, 2, 5),  -- MEX
    (19, 2022, 'D', 6, 6, 3),  -- FRA
    (20, 2022, 'D', 0, 3, 6),  -- AUS
    (21, 2022, 'E', 1, 7, 7),  -- ESP
    (22, 2022, 'E', 1, 7, 7),  -- GER
    (23, 2022, 'F', 4, 4, 1),  -- CRO
    (24, 2022, 'F', 4, 4, 1),  -- MAR
    -- 2026 (em andamento — apenas grupos A e C com dados)
    (25, 2026, 'A', 1, 1, 1),  -- USA
    (26, 2026, 'A', 1, 1, 1),  -- MEX
    (29, 2026, 'C', 3, 2, 1),  -- BRA
    (30, 2026, 'C', 0, 1, 2);  -- ARG

-- =============================================================================
-- 12. JOGADORES (25)
-- =============================================================================
INSERT INTO jogador (nome_jogador) VALUES
    ('Zinedine Zidane'),    -- 1   FRA 1998
    ('Emmanuel Petit'),     -- 2   FRA 1998
    ('Thierry Henry'),      -- 3   FRA 1998
    ('Ronaldo (Brasil)'),   -- 4   BRA 1998
    ('Rivaldo'),            -- 5   BRA 1998
    ('Roberto Carlos'),     -- 6   BRA 1998
    ('Davor Šuker'),        -- 7   CRO 1998
    ('Robert Prosinečki'),  -- 8   CRO 1998
    ('Dennis Bergkamp'),    -- 9   NED 1998
    ('Patrick Kluivert'),   -- 10  NED 1998
    ('Lionel Messi'),       -- 11  ARG 2022 + ARG 2026
    ('Ángel Di María'),     -- 12  ARG 2022
    ('Julián Álvarez'),     -- 13  ARG 2022
    ('Kylian Mbappé'),      -- 14  FRA 2022
    ('Antoine Griezmann'),  -- 15  FRA 2022
    ('Luka Modrić'),        -- 16  CRO 2022
    ('Mateo Kovačić'),      -- 17  CRO 2022
    ('Achraf Hakimi'),      -- 18  MAR 2022
    ('Hakim Ziyech'),       -- 19  MAR 2022
    ('Vinícius Júnior'),    -- 20  BRA 2026
    ('Rodrygo'),            -- 21  BRA 2026
    ('Christian Pulisic'),  -- 22  USA 2026
    ('Folarin Balogun'),    -- 23  USA 2026
    ('Emiliano Martínez'),  -- 24  ARG 2022
    ('Cristiano Ronaldo');  -- 25  POR 2026

-- =============================================================================
-- 13. CONVOCAÇÕES (gols_marcados será atualizado pelos triggers)
-- =============================================================================
INSERT INTO convocacao (ano, id_selecao, id_jogador, numero_camisa) VALUES
    -- 1998 FRA (sel 1)
    (1998, 1,  1,  10),
    (1998, 1,  2,  17),
    (1998, 1,  3,  12),
    -- 1998 BRA (sel 3)
    (1998, 3,  4,  9),
    (1998, 3,  5,  10),
    (1998, 3,  6,  6),
    -- 1998 NED (sel 5)
    (1998, 5,  9,  10),
    (1998, 5,  10, 9),
    -- 1998 CRO (sel 11)
    (1998, 11, 7,  9),
    (1998, 11, 8,  8),
    -- 2022 ARG (sel 17)
    (2022, 17, 11, 10),
    (2022, 17, 12, 11),
    (2022, 17, 13, 9),
    (2022, 17, 24, 23),
    -- 2022 FRA (sel 19)
    (2022, 19, 14, 10),
    (2022, 19, 15, 7),
    -- 2022 CRO (sel 23)
    (2022, 23, 16, 10),
    (2022, 23, 17, 8),
    -- 2022 MAR (sel 24)
    (2022, 24, 18, 2),
    (2022, 24, 19, 7),
    -- 2026 BRA (sel 29)
    (2026, 29, 20, 7),
    (2026, 29, 21, 11),
    -- 2026 ARG (sel 30) — Messi reaproveitado em outro ano
    (2026, 30, 11, 10),
    -- 2026 USA (sel 25)
    (2026, 25, 22, 10),
    (2026, 25, 23, 9),
    -- 2026 POR (sel 35)
    (2026, 35, 25, 7);

-- =============================================================================
-- 14. ÁRBITROS (8) — schema só guarda id (sem nome)
-- =============================================================================
INSERT INTO arbitro (id_arbitro) VALUES
    (DEFAULT), (DEFAULT), (DEFAULT), (DEFAULT),
    (DEFAULT), (DEFAULT), (DEFAULT), (DEFAULT);

-- =============================================================================
-- 15. PARTIDAS (12)
-- =============================================================================
INSERT INTO partida (
    tipo_de_fase, ano, id_estadio, data_hora,
    selecao1, selecao2,
    gols_regulamentares_selecao1, gols_regulamentares_selecao2,
    gols_prorrogacao_selecao1, gols_prorrogacao_selecao2,
    gols_penaltis_selecao1, gols_penaltis_selecao2,
    id_vencedor
) VALUES
    -- 1: Grupo FRA × DEN 1998
    ('Fase de Grupos', 1998, 1, '1998-06-12 16:00:00',
     1, 2, 2, 0, NULL, NULL, NULL, NULL, NULL),
    -- 2: Semi BRA × NED 1998 (1x1 reg, 0x0 prorr, BRA vence nos pênaltis)
    ('Semifinais', 1998, 1, '1998-07-07 21:00:00',
     3, 5, 1, 1, 0, 0, 4, 2, 3),
    -- 3: Semi FRA × CRO 1998 (2x1 reg)
    ('Semifinais', 1998, 1, '1998-07-08 21:00:00',
     1, 11, 2, 1, NULL, NULL, NULL, NULL, 1),
    -- 4: Disp 3º CRO × NED 1998 (2x1)
    ('Disputa de Terceiro Lugar', 1998, 2, '1998-07-11 21:00:00',
     11, 5, 2, 1, NULL, NULL, NULL, NULL, 11),
    -- 5: Final FRA × BRA 1998 (3x0)
    ('Final', 1998, 1, '1998-07-12 21:00:00',
     1, 3, 3, 0, NULL, NULL, NULL, NULL, 1),
    -- 6: Grupo ARG × MEX 2022 (2x0)
    ('Fase de Grupos', 2022, 4, '2022-11-26 22:00:00',
     17, 18, 2, 0, NULL, NULL, NULL, NULL, NULL),
    -- 7: Semi ARG × CRO 2022 (3x0)
    ('Semifinais', 2022, 5, '2022-12-13 22:00:00',
     17, 23, 3, 0, NULL, NULL, NULL, NULL, 17),
    -- 8: Disp 3º CRO × MAR 2022 (2x1)
    ('Disputa de Terceiro Lugar', 2022, 6, '2022-12-17 16:00:00',
     23, 24, 2, 1, NULL, NULL, NULL, NULL, 23),
    -- 9: Final ARG × FRA 2022 (2x2 reg + 1x1 prorr = 3x3, ARG vence 4x2 nos pênaltis)
    ('Final', 2022, 5, '2022-12-18 16:00:00',
     17, 19, 2, 2, 1, 1, 4, 2, 17),
    -- 10: Grupo USA × MEX 2026 (1x1)
    ('Fase de Grupos', 2026, 7, '2026-06-15 20:00:00',
     25, 26, 1, 1, NULL, NULL, NULL, NULL, NULL),
    -- 11: Grupo BRA × ARG 2026 (2x1)
    ('Fase de Grupos', 2026, 8, '2026-06-20 18:00:00',
     29, 30, 2, 1, NULL, NULL, NULL, NULL, NULL),
    -- 12: Grupo POR × NED 2026 (futura, sem placar)
    ('Fase de Grupos', 2026, 10, '2026-06-22 21:00:00',
     35, 36, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- =============================================================================
-- 16. EQUIPE DE ARBITRAGEM POR PARTIDA
-- =============================================================================
INSERT INTO arbitragem_partida (id_partida, id_arbitro, funcao) VALUES
    (1,  1, 'Principal'),
    (1,  2, 'Assistente'),
    (2,  3, 'Principal'),
    (3,  4, 'Principal'),
    (4,  5, 'Principal'),
    (5,  1, 'Principal'),
    (5,  2, 'Assistente'),
    (6,  6, 'Principal'),
    (7,  7, 'Principal'),
    (8,  8, 'Principal'),
    (9,  6, 'Principal'),
    (9,  7, 'Assistente'),
    (10, 3, 'Principal'),
    (11, 4, 'Principal');

-- =============================================================================
-- 17. EVENTOS DE JOGO
-- O tipo do campo "tempo" é TIME (HH:MM:SS). Usamos o formato HH:MM:SS para
-- representar o minuto da partida: minuto 87 → 01:27:00, minuto 108 → 01:48:00.
-- O trigger trg_gols_jogador atualiza convocacao.gols_marcados automaticamente.
-- =============================================================================
INSERT INTO evento_de_jogo (id_jogador, id_partida, tipo_evento, tempo) VALUES
    -- Partida 2 (Semi BRA × NED 1998)
    (4,  2, 'Gol',                '00:46:00'),  -- Ronaldo
    (9,  2, 'Gol',                '01:27:00'),  -- Bergkamp min 87
    (9,  2, 'Cartão Amarelo',     '00:50:00'),
    -- Partida 3 (Semi FRA × CRO 1998)
    (7,  3, 'Gol',                '00:46:00'),  -- Šuker
    (1,  3, 'Gol',                '00:47:00'),  -- Zidane
    (2,  3, 'Gol',                '01:10:00'),  -- Petit min 70
    -- Partida 4 (Disp 3º CRO × NED 1998)
    (8,  4, 'Gol',                '00:13:00'),  -- Prosinečki
    (10, 4, 'Gol',                '00:21:00'),  -- Kluivert
    (7,  4, 'Gol',                '00:35:00'),  -- Šuker
    -- Partida 5 (Final FRA × BRA 1998)
    (1,  5, 'Gol',                '00:27:00'),  -- Zidane
    (1,  5, 'Gol',                '00:45:00'),  -- Zidane 2x
    (6,  5, 'Cartão Amarelo',     '00:50:00'),  -- R. Carlos
    (2,  5, 'Gol',                '01:33:00'),  -- Petit min 93
    -- Partida 6 (Grupo ARG × MEX 2022)
    (11, 6, 'Gol',                '01:04:00'),  -- Messi min 64
    -- Partida 7 (Semi ARG × CRO 2022)
    (11, 7, 'Pênalti Convertido', '00:34:00'),  -- Messi
    (13, 7, 'Gol',                '00:39:00'),  -- Álvarez
    (13, 7, 'Gol',                '01:09:00'),  -- Álvarez min 69
    (16, 7, 'Cartão Amarelo',     '00:30:00'),  -- Modrić
    -- Partida 8 (Disp 3º CRO × MAR 2022)
    (19, 8, 'Gol',                '00:17:00'),  -- Ziyech
    (17, 8, 'Gol',                '01:30:00'),  -- Kovačić min 90
    (18, 8, 'Cartão Amarelo',     '01:05:00'),  -- Hakimi min 65
    -- Partida 9 (Final ARG × FRA 2022)
    (11, 9, 'Pênalti Convertido', '00:23:00'),  -- Messi
    (12, 9, 'Gol',                '00:36:00'),  -- Di María
    (14, 9, 'Pênalti Convertido', '01:20:00'),  -- Mbappé min 80
    (14, 9, 'Gol',                '01:21:00'),  -- Mbappé min 81
    (11, 9, 'Gol',                '01:48:00'),  -- Messi prorr (min 108)
    (14, 9, 'Pênalti Convertido', '01:58:00'),  -- Mbappé prorr (min 118)
    (14, 9, 'Cartão Amarelo',     '01:40:00'),  -- Mbappé
    -- Partida 10 (Grupo USA × MEX 2026)
    (22, 10, 'Gol',                '00:25:00'),  -- Pulisic
    (22, 10, 'Cartão Amarelo',     '01:00:00'),  -- Pulisic min 60
    -- Partida 11 (Grupo BRA × ARG 2026)
    (20, 11, 'Gol',                '00:30:00'),  -- Vinícius
    (21, 11, 'Gol',                '01:18:00'),  -- Rodrygo min 78
    (11, 11, 'Gol',                '01:28:00');  -- Messi min 88

-- =============================================================================
-- 18. CAMPEÕES / VICES / TERCEIROS — atualizado após inserir todas as seleções
-- =============================================================================
UPDATE edicao_da_copa
SET campea = 1, vice_campeao = 3, terceiro_colocado = 11
WHERE ano = 1998;

UPDATE edicao_da_copa
SET campea = 17, vice_campeao = 19, terceiro_colocado = 23
WHERE ano = 2022;

-- 2026: em andamento, sem campeão definido ainda.
