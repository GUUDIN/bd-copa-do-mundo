"""As 10 consultas SQL parametrizadas do sistema de Copas do Mundo.

Todas as queries usam placeholders %s do psycopg2 para parâmetros.
Cada função retorna uma tupla (sql, params).
"""

# 1. Listar edições da Copa do Mundo (ano, país-sede, campeão)
def q1_edicoes():
    sql = """
        SELECT e.ano,
               p.nome AS pais_sede,
               s_pais.nome AS campea
        FROM copa_mundo.edicaocopa e
        JOIN copa_mundo.pais p ON p.id_pais = e.id_pais_sede
        LEFT JOIN copa_mundo.selecao sel ON sel.id_selecao = e.id_selecao_campea
        LEFT JOIN copa_mundo.pais s_pais ON s_pais.id_pais = sel.id_pais
        ORDER BY e.ano;
    """
    return sql, ()


# 2. Listar seleções de uma edição
def q2_selecoes_edicao(ano):
    sql = """
        SELECT p.nome AS pais,
               c.nome AS confederacao
        FROM copa_mundo.participacaoedicao pe
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pe.id_edicao
        JOIN copa_mundo.selecao s ON s.id_selecao = pe.id_selecao
        JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        LEFT JOIN copa_mundo.confederacao c ON c.id_confederacao = s.id_confederacao
        WHERE e.ano = %s
        ORDER BY p.nome;
    """
    return sql, (ano,)


# 3. Grupos e seleções de uma edição
def q3_grupos_edicao(ano):
    sql = """
        SELECT g.letra AS grupo,
               p.nome AS pais
        FROM copa_mundo.grupo g
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = g.id_edicao
        JOIN copa_mundo.selecaogrupo sg ON sg.id_grupo = g.id_grupo
        JOIN copa_mundo.selecao s ON s.id_selecao = sg.id_selecao
        JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        WHERE e.ano = %s
        ORDER BY g.letra, p.nome;
    """
    return sql, (ano,)


# 4. Tabela de classificação de um grupo
def q4_classificacao_grupo(ano, letra):
    sql = """
        SELECT p.nome AS pais,
               cg.pontos,
               cg.vitorias,
               cg.empates,
               cg.derrotas,
               cg.gols_pro,
               cg.gols_contra,
               (cg.gols_pro - cg.gols_contra) AS saldo
        FROM copa_mundo.classificacaogrupo cg
        JOIN copa_mundo.grupo g ON g.id_grupo = cg.id_grupo
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = g.id_edicao
        JOIN copa_mundo.selecao s ON s.id_selecao = cg.id_selecao
        JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        WHERE e.ano = %s AND UPPER(g.letra) = UPPER(%s)
        ORDER BY cg.pontos DESC,
                 (cg.gols_pro - cg.gols_contra) DESC,
                 cg.gols_pro DESC;
    """
    return sql, (ano, letra)


# 5. Partidas de uma edição
def q5_partidas_edicao(ano):
    sql = """
        SELECT pa.id_partida,
               pa.data_hora,
               f.nome AS fase,
               p1.nome AS mandante,
               pa.gols_mandante,
               pa.gols_visitante,
               p2.nome AS visitante,
               est.nome AS estadio
        FROM copa_mundo.partida pa
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pa.id_edicao
        JOIN copa_mundo.fase f ON f.id_fase = pa.id_fase
        JOIN copa_mundo.selecao s1 ON s1.id_selecao = pa.id_selecao_mandante
        JOIN copa_mundo.pais p1 ON p1.id_pais = s1.id_pais
        JOIN copa_mundo.selecao s2 ON s2.id_selecao = pa.id_selecao_visitante
        JOIN copa_mundo.pais p2 ON p2.id_pais = s2.id_pais
        LEFT JOIN copa_mundo.estadio est ON est.id_estadio = pa.id_estadio
        WHERE e.ano = %s
        ORDER BY pa.data_hora;
    """
    return sql, (ano,)


# 6. Caminho do mata-mata
def q6_mata_mata(ano):
    sql = """
        SELECT f.nome AS fase,
               pa.data_hora,
               p1.nome AS mandante,
               pa.gols_mandante,
               pa.gols_visitante,
               p2.nome AS visitante
        FROM copa_mundo.partida pa
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pa.id_edicao
        JOIN copa_mundo.fase f ON f.id_fase = pa.id_fase
        JOIN copa_mundo.selecao s1 ON s1.id_selecao = pa.id_selecao_mandante
        JOIN copa_mundo.pais p1 ON p1.id_pais = s1.id_pais
        JOIN copa_mundo.selecao s2 ON s2.id_selecao = pa.id_selecao_visitante
        JOIN copa_mundo.pais p2 ON p2.id_pais = s2.id_pais
        WHERE e.ano = %s
          AND LOWER(f.nome) NOT LIKE '%%grupo%%'
          AND LOWER(f.nome) NOT LIKE '%%fase de grupo%%'
        ORDER BY pa.data_hora;
    """
    return sql, (ano,)


# 7. Elenco de uma seleção em uma edição
def q7_elenco(pais, ano):
    sql = """
        SELECT j.nome AS jogador,
               c.numero_camisa,
               c.posicao
        FROM copa_mundo.convocacao c
        JOIN copa_mundo.participacaoedicao pe ON pe.id_participacao = c.id_participacao
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pe.id_edicao
        JOIN copa_mundo.selecao s ON s.id_selecao = pe.id_selecao
        JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        JOIN copa_mundo.jogador j ON j.id_jogador = c.id_jogador
        WHERE LOWER(p.nome) = LOWER(%s) AND e.ano = %s
        ORDER BY c.numero_camisa;
    """
    return sql, (pais, ano)


# 8. Eventos de uma partida
def q8_eventos_partida(id_partida):
    sql = """
        SELECT ev.minuto,
               ev.tipo,
               j.nome AS jogador,
               p.nome AS selecao,
               ev.descricao
        FROM copa_mundo.eventojogo ev
        LEFT JOIN copa_mundo.jogador j ON j.id_jogador = ev.id_jogador
        LEFT JOIN copa_mundo.selecao s ON s.id_selecao = ev.id_selecao
        LEFT JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        WHERE ev.id_partida = %s
        ORDER BY ev.minuto;
    """
    return sql, (id_partida,)


# 9. Artilheiros de uma edição
def q9_artilheiros(ano):
    sql = """
        SELECT j.nome AS jogador,
               p.nome AS selecao,
               COUNT(*) AS gols
        FROM copa_mundo.eventojogo ev
        JOIN copa_mundo.partida pa ON pa.id_partida = ev.id_partida
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pa.id_edicao
        JOIN copa_mundo.jogador j ON j.id_jogador = ev.id_jogador
        LEFT JOIN copa_mundo.selecao s ON s.id_selecao = ev.id_selecao
        LEFT JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        WHERE e.ano = %s
          AND LOWER(ev.tipo) IN ('gol', 'goal', 'gol_contra', 'penalti')
          AND LOWER(ev.tipo) NOT LIKE '%%contra%%'
        GROUP BY j.nome, p.nome
        ORDER BY gols DESC, j.nome
        LIMIT 50;
    """
    return sql, (ano,)


# 10. Histórico de uma seleção
def q10_historico_selecao(pais):
    sql = """
        SELECT e.ano,
               ps.nome AS pais_sede,
               f.nome AS melhor_fase
        FROM copa_mundo.participacaoedicao pe
        JOIN copa_mundo.selecao s ON s.id_selecao = pe.id_selecao
        JOIN copa_mundo.pais p ON p.id_pais = s.id_pais
        JOIN copa_mundo.edicaocopa e ON e.id_edicao = pe.id_edicao
        JOIN copa_mundo.pais ps ON ps.id_pais = e.id_pais_sede
        LEFT JOIN copa_mundo.fase f ON f.id_fase = pe.id_fase_final
        WHERE LOWER(p.nome) = LOWER(%s)
        ORDER BY e.ano;
    """
    return sql, (pais,)
