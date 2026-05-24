-- =============================================================================
-- SCC0640 – Copa do Mundo FIFA
-- consultas.sql – As 10 consultas requeridas
-- =============================================================================

-- 1. Listar todas as edições com ano, país-sede e campeão
-- -----------------------------------------------------------------------------
SELECT
    e.ano,
    ps.nome_pais              AS pais_sede,
    pc.nome_pais              AS selecao_campea
FROM edicao_da_copa e
JOIN pais ps ON e.pais_sede = ps.sigla_pais
LEFT JOIN selecao    s_c ON e.campea    = s_c.id_selecao AND e.ano = s_c.ano
LEFT JOIN pais    pc     ON s_c.sigla_pais = pc.sigla_pais
ORDER BY e.ano DESC;

-- 2. Seleções participantes de uma edição (substitua o ano)
-- -----------------------------------------------------------------------------
SELECT
    p.nome_pais,
    s.letra_grupo
FROM selecao s
JOIN pais p ON s.sigla_pais = p.sigla_pais
WHERE s.ano = 2026
ORDER BY s.letra_grupo, p.nome_pais;

-- 3. Grupos de uma edição e suas seleções
-- -----------------------------------------------------------------------------
SELECT
    s.letra_grupo AS grupo,
    p.nome_pais   AS selecao
FROM selecao s
JOIN pais p ON s.sigla_pais = p.sigla_pais
WHERE s.ano = 2026
ORDER BY s.letra_grupo, p.nome_pais;

-- 4. Classificação de um grupo (substitua ano e letra)
-- -----------------------------------------------------------------------------
SELECT
    p.nome_pais,
    sg.pontos,
    sg.gols_pro,
    sg.gols_contra,
    sg.saldo_gols
FROM selecao_grupo sg
JOIN selecao s ON sg.id_selecao = s.id_selecao AND sg.ano = s.ano
JOIN pais    p ON s.sigla_pais  = p.sigla_pais
WHERE sg.ano = 2026
  AND sg.letra_grupo = 'A'
ORDER BY sg.pontos DESC, sg.saldo_gols DESC, sg.gols_pro DESC;

-- 5. Partidas de uma edição com fase, data, estádio e placar
-- -----------------------------------------------------------------------------
SELECT
    pt.tipo_de_fase,
    pt.data_hora,
    est.cidade                             AS estadio_cidade,
    p1.nome_pais                           AS selecao1,
    pt.gols_regulamentares_selecao1        AS gols1,
    pt.gols_regulamentares_selecao2        AS gols2,
    p2.nome_pais                           AS selecao2
FROM partida pt
JOIN estadio est ON pt.id_estadio = est.id_estadio
JOIN selecao s1  ON pt.selecao1   = s1.id_selecao AND pt.ano = s1.ano
JOIN pais    p1  ON s1.sigla_pais = p1.sigla_pais
JOIN selecao s2  ON pt.selecao2   = s2.id_selecao AND pt.ano = s2.ano
JOIN pais    p2  ON s2.sigla_pais = p2.sigla_pais
WHERE pt.ano = 2026
ORDER BY pt.data_hora;

-- 6. Caminho do mata-mata (classificados por fase)
-- -----------------------------------------------------------------------------
SELECT
    pt.tipo_de_fase,
    pt.data_hora,
    pv.nome_pais AS classificado
FROM partida pt
JOIN selecao sv ON pt.id_vencedor = sv.id_selecao AND pt.ano = sv.ano
JOIN pais    pv ON sv.sigla_pais  = pv.sigla_pais
WHERE pt.ano = 2026
  AND pt.tipo_de_fase <> 'Fase de Grupos'
ORDER BY pt.data_hora;

-- 7. Elenco convocado de uma seleção numa edição (substitua ano e sigla)
-- -----------------------------------------------------------------------------
SELECT
    c.numero_camisa,
    j.nome_jogador,
    c.gols_marcados
FROM convocacao c
JOIN jogador  j ON c.id_jogador  = j.id_jogador
JOIN selecao  s ON c.id_selecao  = s.id_selecao AND c.ano = s.ano
WHERE c.ano        = 2026
  AND s.sigla_pais = 'BRA'
ORDER BY c.numero_camisa;

-- 8. Eventos de uma partida (gols, cartões, substituições)
-- -----------------------------------------------------------------------------
SELECT
    e.tempo,
    e.tipo_evento,
    j.nome_jogador
FROM evento_de_jogo e
LEFT JOIN jogador j ON e.id_jogador = j.id_jogador
WHERE e.id_partida = 1          -- substitua pelo id desejado
ORDER BY e.tempo;

-- 9. Artilheiros de uma edição
-- -----------------------------------------------------------------------------
SELECT
    j.nome_jogador,
    p.nome_pais,
    c.gols_marcados
FROM convocacao c
JOIN jogador j ON c.id_jogador  = j.id_jogador
JOIN selecao s ON c.id_selecao  = s.id_selecao AND c.ano = s.ano
JOIN pais    p ON s.sigla_pais  = p.sigla_pais
WHERE c.ano = 2026
  AND c.gols_marcados > 0
ORDER BY c.gols_marcados DESC
LIMIT 10;

-- 10. Histórico de uma seleção (participações, posições, J/V/E/D)
-- -----------------------------------------------------------------------------
WITH jogos AS (
    SELECT
        s.sigla_pais,
        COUNT(pt.id_partida)                                         AS total_jogos,
        SUM(CASE WHEN pt.id_vencedor = s.id_selecao               THEN 1 ELSE 0 END) AS vitorias,
        SUM(CASE
                WHEN pt.id_vencedor IS NULL
                 AND pt.gols_regulamentares_selecao1 = pt.gols_regulamentares_selecao2
                    THEN 1 ELSE 0 END)                               AS empates,
        SUM(CASE
                WHEN pt.id_vencedor IS NOT NULL
                 AND pt.id_vencedor <> s.id_selecao                 THEN 1 ELSE 0 END) AS derrotas
    FROM selecao s
    LEFT JOIN partida pt
           ON (s.id_selecao = pt.selecao1 OR s.id_selecao = pt.selecao2)
          AND s.ano = pt.ano
    WHERE s.sigla_pais = 'BRA'   -- substitua pelo país desejado
    GROUP BY s.sigla_pais
),
posicoes AS (
    SELECT
        s.sigla_pais,
        SUM(CASE WHEN e.campea             = s.id_selecao THEN 1 ELSE 0 END) AS titulos,
        SUM(CASE WHEN e.vice_campeao       = s.id_selecao THEN 1 ELSE 0 END) AS vices,
        SUM(CASE WHEN e.terceiro_colocado  = s.id_selecao THEN 1 ELSE 0 END) AS terceiros,
        COUNT(DISTINCT s.ano)                                                 AS participacoes
    FROM selecao s
    JOIN edicao_da_copa e ON s.ano = e.ano
    WHERE s.sigla_pais = 'BRA'
    GROUP BY s.sigla_pais
)
SELECT
    p.nome_pais,
    pos.participacoes,
    pos.titulos,
    pos.vices,
    pos.terceiros,
    j.total_jogos,
    j.vitorias,
    j.empates,
    j.derrotas
FROM jogos j
JOIN posicoes pos ON j.sigla_pais = pos.sigla_pais
JOIN pais    p   ON j.sigla_pais  = p.sigla_pais;
