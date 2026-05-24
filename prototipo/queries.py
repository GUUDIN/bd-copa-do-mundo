"""As 10 consultas pedidas no enunciado."""


# 1. Edições da Copa do Mundo (ano, país-sede, campeão)
def q1_edicoes():
    sql = """
        SELECT
            e.ano,
            ps.nome_pais AS pais_sede,
            pc.nome_pais AS selecao_campea
        FROM edicao_da_copa e
        JOIN pais ps ON e.pais_sede = ps.sigla_pais
        LEFT JOIN selecao s_campea ON e.campea = s_campea.id_selecao
                                  AND e.ano = s_campea.ano
        LEFT JOIN pais pc ON s_campea.sigla_pais = pc.sigla_pais
        ORDER BY e.ano DESC;
    """
    return sql, ()


# 2. Seleções participantes de uma edição
def q2_selecoes_edicao(ano):
    sql = """
        SELECT
            p.nome_pais,
            s.letra_grupo
        FROM selecao s
        JOIN pais p ON s.sigla_pais = p.sigla_pais
        WHERE s.ano = %s
        ORDER BY p.nome_pais;
    """
    return sql, (ano,)


# 3. Grupos de uma edição e suas seleções
def q3_grupos_edicao(ano):
    sql = """
        SELECT
            s.letra_grupo AS grupo,
            p.nome_pais AS selecao
        FROM selecao s
        JOIN pais p ON s.sigla_pais = p.sigla_pais
        WHERE s.ano = %s
        ORDER BY s.letra_grupo, p.nome_pais;
    """
    return sql, (ano,)


# 4. Tabela de classificação de um grupo
def q4_classificacao_grupo(ano, letra):
    sql = """
        SELECT
            p.nome_pais,
            sg.pontos,
            sg.gols_pro,
            sg.gols_contra,
            sg.saldo_gols
        FROM selecao_grupo sg
        JOIN selecao s ON sg.id_selecao = s.id_selecao AND sg.ano = s.ano
        JOIN pais p ON s.sigla_pais = p.sigla_pais
        WHERE sg.ano = %s AND UPPER(sg.letra_grupo) = UPPER(%s)
        ORDER BY sg.pontos DESC, sg.saldo_gols DESC, sg.gols_pro DESC;
    """
    return sql, (ano, letra)


# 5. Partidas de uma edição
def q5_partidas_edicao(ano):
    sql = """
        SELECT
            pt.tipo_de_fase,
            pt.data_hora,
            est.cidade,
            p1.nome_pais AS mandante,
            pt.gols_regulamentares_selecao1 AS gols_mandante,
            pt.gols_regulamentares_selecao2 AS gols_visitante,
            p2.nome_pais AS visitante
        FROM partida pt
        JOIN estadio est ON pt.id_estadio = est.id_estadio
        JOIN selecao s1 ON pt.selecao1 = s1.id_selecao AND pt.ano = s1.ano
        JOIN pais p1 ON s1.sigla_pais = p1.sigla_pais
        JOIN selecao s2 ON pt.selecao2 = s2.id_selecao AND pt.ano = s2.ano
        JOIN pais p2 ON s2.sigla_pais = p2.sigla_pais
        WHERE pt.ano = %s
        ORDER BY pt.data_hora;
    """
    return sql, (ano,)


# 6. Caminho do mata-mata
def q6_mata_mata(ano):
    sql = """
        SELECT
            pt.tipo_de_fase,
            pt.data_hora,
            pv.nome_pais AS selecao_classificada
        FROM partida pt
        JOIN selecao sv ON pt.id_vencedor = sv.id_selecao AND pt.ano = sv.ano
        JOIN pais pv ON sv.sigla_pais = pv.sigla_pais
        WHERE pt.ano = %s AND pt.tipo_de_fase <> 'Fase de Grupos'
        ORDER BY pt.data_hora;
    """
    return sql, (ano,)


# 7. Elenco convocado de uma seleção em uma edição
def q7_elenco(sigla_pais, ano):
    sql = """
        SELECT
            c.numero_camisa,
            j.nome_jogador,
            c.gols_marcados
        FROM convocacao c
        JOIN jogador j ON c.id_jogador = j.id_jogador
        JOIN selecao s ON c.id_selecao = s.id_selecao AND c.ano = s.ano
        WHERE c.ano = %s AND UPPER(s.sigla_pais) = UPPER(%s)
        ORDER BY c.numero_camisa;
    """
    return sql, (ano, sigla_pais)


# 8. Eventos de uma partida
def q8_eventos_partida(id_partida):
    sql = """
        SELECT
            e.tempo,
            e.tipo_evento,
            j.nome_jogador
        FROM evento_de_jogo e
        LEFT JOIN jogador j ON e.id_jogador = j.id_jogador
        WHERE e.id_partida = %s
        ORDER BY e.tempo;
    """
    return sql, (id_partida,)


# 9. Artilheiros de uma edição
def q9_artilheiros(ano):
    sql = """
        SELECT
            j.nome_jogador,
            p.nome_pais,
            c.gols_marcados
        FROM convocacao c
        JOIN jogador j ON c.id_jogador = j.id_jogador
        JOIN selecao s ON c.id_selecao = s.id_selecao AND c.ano = s.ano
        JOIN pais p ON s.sigla_pais = p.sigla_pais
        WHERE c.ano = %s AND c.gols_marcados > 0
        ORDER BY c.gols_marcados DESC
        LIMIT 10;
    """
    return sql, (ano,)


# 10. Histórico de uma seleção (participações, títulos, jogos, V/E/D)
def q10_historico_selecao(sigla_pais):
    sql = """
        WITH historico_partidas AS (
            SELECT
                s.sigla_pais,
                COUNT(pt.id_partida) AS total_jogos,
                SUM(CASE
                    WHEN pt.id_vencedor = s.id_selecao THEN 1
                    WHEN pt.id_vencedor IS NULL
                         AND pt.selecao1 = s.id_selecao
                         AND pt.gols_regulamentares_selecao1 > pt.gols_regulamentares_selecao2 THEN 1
                    WHEN pt.id_vencedor IS NULL
                         AND pt.selecao2 = s.id_selecao
                         AND pt.gols_regulamentares_selecao2 > pt.gols_regulamentares_selecao1 THEN 1
                    ELSE 0 END) AS vitorias,
                SUM(CASE
                    WHEN pt.id_vencedor IS NULL
                         AND pt.gols_regulamentares_selecao1 = pt.gols_regulamentares_selecao2 THEN 1
                    ELSE 0 END) AS empates,
                SUM(CASE
                    WHEN pt.id_vencedor IS NOT NULL AND pt.id_vencedor <> s.id_selecao THEN 1
                    WHEN pt.id_vencedor IS NULL
                         AND pt.selecao1 = s.id_selecao
                         AND pt.gols_regulamentares_selecao1 < pt.gols_regulamentares_selecao2 THEN 1
                    WHEN pt.id_vencedor IS NULL
                         AND pt.selecao2 = s.id_selecao
                         AND pt.gols_regulamentares_selecao2 < pt.gols_regulamentares_selecao1 THEN 1
                    ELSE 0 END) AS derrotas
            FROM selecao s
            LEFT JOIN partida pt
                   ON (s.id_selecao = pt.selecao1 OR s.id_selecao = pt.selecao2)
                  AND s.ano = pt.ano
            WHERE UPPER(s.sigla_pais) = UPPER(%s)
            GROUP BY s.sigla_pais
        )
        SELECT
            p.nome_pais,
            (SELECT COUNT(*) FROM selecao
              WHERE UPPER(sigla_pais) = UPPER(%s))             AS participacoes_em_copas,
            (SELECT COUNT(*)
               FROM edicao_da_copa e
               JOIN selecao s ON e.campea = s.id_selecao AND e.ano = s.ano
              WHERE UPPER(s.sigla_pais) = UPPER(%s))           AS titulos_campeao,
            hp.total_jogos,
            hp.vitorias,
            hp.empates,
            hp.derrotas
        FROM historico_partidas hp
        JOIN pais p ON hp.sigla_pais = p.sigla_pais;
    """
    return sql, (sigla_pais, sigla_pais, sigla_pais)
