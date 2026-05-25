# Treinamento NL → SQL — Copa do Mundo

Material que orienta o modelo a gerar SQL para o schema do projeto. Não contém
respostas prontas. Cada padrão descreve a intenção, os termos esperados, as
tabelas/colunas envolvidas e um template-esqueleto com placeholders.

## ESCOPO DOS DADOS (sempre verdadeiro)

- A base cobre as Copas de **1998, 2002, 2006, 2010, 2014, 2018 e 2022** (7 edições).
- Todas as edições carregadas usam formato com **32 seleções**, fase de grupos e
  mata-mata. Campeã faz **7 jogos** (3 grupos + oitavas + quartas + semi + final).
- Não há dados de Copas anteriores a 1998 nem da Copa de 2026.
- "Todas as copas" / "todas as edições" / "no geral" → as 7 edições acima.

## REGRAS CRÍTICAS (aplicar sempre, sem exceção)

1. **Escopo temporal:** se a pergunta cita um ano fora de {1998, 2002, 2006, 2010, 2014, 2018, 2022},
   responda `-- NAO_SEI`. Se a pergunta não cita ano, não filtre por ano.

2. **Perspectiva de UMA seleção** (pergunta cita uma seleção específica, ex.: "Brasil", "Argentina"):
   normalize partida com `UNION ALL` em duas linhas (uma com a seleção como
   `selecao1`, outra como `selecao2`) e filtre por `sigla_pais` em ambos os lados.

3. **Estatística sobre TODAS as seleções** (pergunta não cita seleção específica,
   ex.: "qual seleção fez mais gols", "qual time venceu mais"): mesma normalização
   `UNION ALL`, mas **sem filtro de sigla**. Agrupe por `ano` + `sigla_pais`.

4. **Gols marcados** de uma seleção (do lado X): `gols_regulamentares_selecaoX + gols_prorrogacao_selecaoX`.

5. **Gols sofridos** de uma seleção (do lado X): `gols_regulamentares_selecaoY + gols_prorrogacao_selecaoY`, onde Y é o lado oposto.

6. **Pênaltis de disputa** (`gols_penaltis_*`) NUNCA entram como gols de jogo,
   salvo se a pergunta falar explicitamente em "disputa de pênaltis".

7. **"Em uma única edição"** → `GROUP BY ano, sigla_pais` (ou nome equivalente).

8. **"Máximo / maior / mais X"** → calcule o `MAX(...)` em CTE auxiliar e
   retorne TODAS as linhas empatadas no valor máximo via `JOIN`. **NUNCA use
   `LIMIT 1`** quando empate é possível (gols totais, jogos, vitórias, etc.).

9. **Adversário** só entra no `GROUP BY` se a pergunta falar "adversário", "contra
   quem", "contra qual seleção". Nunca atribua gols de uma seleção ao adversário.

10. **Gols de jogadores** → `convocacao.gols_marcados`.
    **Gols de seleções** / **placar de partidas** → tabela `partida`.
    Nunca use `convocacao.gols_marcados` para placar.

## VOCABULÁRIO DO SCHEMA

- edição, copa, mundial, torneio → `edicao_da_copa`
- país sede, sede, anfitrião → `edicao_da_copa.pais_sede` + `pais`
- campeão, vencedor da copa → `edicao_da_copa.campea`
- vice, finalista derrotado → `edicao_da_copa.vice_campeao`
- terceiro colocado → `edicao_da_copa.terceiro_colocado`
- seleção, time, equipe, país participante → `selecao` + `pais`
- grupo, chave → `grupo`, `selecao.letra_grupo`, `selecao_grupo`
- classificação, tabela, pontos, saldo → `selecao_grupo`
- partida, jogo, confronto → `partida`
- fase, etapa → `partida.tipo_de_fase`
- mata-mata, eliminatórias → fases diferentes de `'Fase de Grupos'`
- oitavas → `'Oitavas de Final'`
- quartas → `'Quartas de Final'`
- semi → `'Semifinais'`
- terceiro lugar → `'Disputa de Terceiro Lugar'`
- final → `'Final'`
- elenco, convocados → `convocacao` + `jogador`
- artilheiro, goleador → `convocacao.gols_marcados`
- evento, lance → `evento_de_jogo`
- cartão, substituição, gol → `evento_de_jogo.tipo_evento`
- estádio, cidade → `estadio`, `cidade_sede`, `cidade_sedia_edicao`

## SIGLAS

Alemanha=`GER`, Argentina=`ARG`, Austrália=`AUS`, Bélgica=`BEL`, Brasil=`BRA`,
Camarões=`CMR`, Canadá=`CAN`, Chile=`CHI`, Coreia do Sul=`KOR`, Croácia=`CRO`,
Dinamarca=`DEN`, Equador=`ECU`, Espanha=`ESP`, Estados Unidos=`USA`,
França=`FRA`, Gana=`GHA`, Holanda=`NED`, Inglaterra=`ENG`, Irã=`IRN`,
Itália=`ITA`, Japão=`JPN`, México=`MEX`, Marrocos=`MAR`, Nigéria=`NGA`,
Paraguai=`PAR`, Polônia=`POL`, Portugal=`POR`, Rússia=`RUS`, Senegal=`SEN`,
Sérvia=`SRB`, Suécia=`SWE`, Suíça=`SUI`, Tunísia=`TUN`, Uruguai=`URU`.
Para nomes em português digitados pelo usuário, prefira `pais.nome_pais ILIKE '%nome%'`.

---

## PADRÕES CANÔNICOS

Use o padrão cujo "USAR QUANDO" mais combina com a pergunta. Adapte filtros e
aliases. Não copie placeholders `<...>` literalmente.

### gols_por_selecao_em_edicao

USAR QUANDO:
- "qual seleção marcou mais gols em uma única edição"
- "país fez mais gols em uma copa"
- "equipe com mais gols em uma edição"
- "maior número de gols em uma única copa"
- "seleção mais ofensiva em uma edição"

OBRIGATÓRIO:
- usar tabela `partida` (NUNCA `convocacao` para isso);
- CTE com UNION ALL trazendo os dois lados como linhas separadas;
- somar `gols_regulamentares_selecaoX + gols_prorrogacao_selecaoX` do PRÓPRIO lado;
- agrupar por `ano + sigla_pais`;
- calcular o máximo em CTE auxiliar e retornar empatados via JOIN;
- NÃO usar `LIMIT 1`.

SQL_TEMPLATE:
```sql
WITH gols_por_selecao AS (
    SELECT pt.ano, s.sigla_pais, p.nome_pais AS selecao,
           COALESCE(pt.gols_regulamentares_selecao1, 0)
         + COALESCE(pt.gols_prorrogacao_selecao1, 0) AS gols_marcados
    FROM partida pt
    JOIN selecao s ON pt.selecao1 = s.id_selecao AND pt.ano = s.ano
    JOIN pais p ON s.sigla_pais = p.sigla_pais
    UNION ALL
    SELECT pt.ano, s.sigla_pais, p.nome_pais AS selecao,
           COALESCE(pt.gols_regulamentares_selecao2, 0)
         + COALESCE(pt.gols_prorrogacao_selecao2, 0) AS gols_marcados
    FROM partida pt
    JOIN selecao s ON pt.selecao2 = s.id_selecao AND pt.ano = s.ano
    JOIN pais p ON s.sigla_pais = p.sigla_pais
),
total_por_edicao AS (
    SELECT ano, sigla_pais, selecao, SUM(gols_marcados) AS total_gols
    FROM gols_por_selecao
    GROUP BY ano, sigla_pais, selecao
),
maximo AS (SELECT MAX(total_gols) AS m FROM total_por_edicao)
SELECT t.ano, t.sigla_pais, t.selecao, t.total_gols
FROM total_por_edicao t JOIN maximo ON t.total_gols = maximo.m
ORDER BY t.ano, t.selecao;
```

### gols_contra_adversario

USAR QUANDO:
- "qual adversário mais sofreu gols do <SELEÇÃO>"
- "contra quem o <SELEÇÃO> mais fez gols"
- "qual seleção mais marcou contra o <SELEÇÃO>"

OBRIGATÓRIO:
- CTE UNION ALL com filtro `WHERE sel.sigla_pais = '<SIGLA>'` em AMBOS os lados;
- carregar adversário pelo lado oposto;
- somar gols pró ou contra dependendo da pergunta;
- agrupar por adversário (nome ou sigla).

SQL_TEMPLATE:
```sql
WITH jogos_da_selecao AS (
    SELECT pt.ano, adv.sigla_pais AS sigla_adv, adv_p.nome_pais AS adversario,
           COALESCE(pt.gols_regulamentares_selecao1, 0)
         + COALESCE(pt.gols_prorrogacao_selecao1, 0) AS gols_pro,
           COALESCE(pt.gols_regulamentares_selecao2, 0)
         + COALESCE(pt.gols_prorrogacao_selecao2, 0) AS gols_contra
    FROM partida pt
    JOIN selecao sel ON pt.selecao1 = sel.id_selecao AND pt.ano = sel.ano
    JOIN selecao adv ON pt.selecao2 = adv.id_selecao AND pt.ano = adv.ano
    JOIN pais adv_p ON adv.sigla_pais = adv_p.sigla_pais
    WHERE sel.sigla_pais = '<SIGLA>'
    UNION ALL
    SELECT pt.ano, adv.sigla_pais AS sigla_adv, adv_p.nome_pais AS adversario,
           COALESCE(pt.gols_regulamentares_selecao2, 0)
         + COALESCE(pt.gols_prorrogacao_selecao2, 0) AS gols_pro,
           COALESCE(pt.gols_regulamentares_selecao1, 0)
         + COALESCE(pt.gols_prorrogacao_selecao1, 0) AS gols_contra
    FROM partida pt
    JOIN selecao sel ON pt.selecao2 = sel.id_selecao AND pt.ano = sel.ano
    JOIN selecao adv ON pt.selecao1 = adv.id_selecao AND pt.ano = adv.ano
    JOIN pais adv_p ON adv.sigla_pais = adv_p.sigla_pais
    WHERE sel.sigla_pais = '<SIGLA>'
)
SELECT sigla_adv, adversario, SUM(gols_pro) AS gols_marcados_contra
FROM jogos_da_selecao
GROUP BY sigla_adv, adversario
ORDER BY gols_marcados_contra DESC, adversario;
```

### jogos_por_selecao

USAR QUANDO:
- "quantos jogos a <SELEÇÃO> fez"
- "quantas partidas o <SELEÇÃO> disputou"
- "qual seleção fez mais jogos em uma edição"
- "máximo de jogos de uma seleção"

OBRIGATÓRIO:
- CTE UNION ALL trazendo os dois lados como linhas separadas;
- contar `id_partida` por seleção/ano;
- se pergunta cita seleção específica → filtre por sigla; senão, agrupe por todas;
- para "máximo/maior", use a regra de empate (CTE de MAX + JOIN).

SQL_TEMPLATE (todas as seleções, com tratamento de empate):
```sql
WITH jogos AS (
    SELECT pt.ano, s.sigla_pais, p.nome_pais AS selecao, pt.id_partida
    FROM partida pt
    JOIN selecao s ON pt.selecao1 = s.id_selecao AND pt.ano = s.ano
    JOIN pais p ON s.sigla_pais = p.sigla_pais
    UNION ALL
    SELECT pt.ano, s.sigla_pais, p.nome_pais AS selecao, pt.id_partida
    FROM partida pt
    JOIN selecao s ON pt.selecao2 = s.id_selecao AND pt.ano = s.ano
    JOIN pais p ON s.sigla_pais = p.sigla_pais
),
total AS (
    SELECT ano, sigla_pais, selecao, COUNT(id_partida) AS total_jogos
    FROM jogos GROUP BY ano, sigla_pais, selecao
),
maximo AS (SELECT MAX(total_jogos) AS m FROM total)
SELECT t.ano, t.sigla_pais, t.selecao, t.total_jogos
FROM total t JOIN maximo ON t.total_jogos = maximo.m
ORDER BY t.ano, t.selecao;
```

### artilharia_jogador

USAR QUANDO:
- "quem foi o artilheiro da copa de <ANO>"
- "top 10 artilheiros"
- "maior goleador"
- "quantos gols <JOGADOR> fez"

OBRIGATÓRIO:
- usar `convocacao.gols_marcados` (mantido por trigger);
- joins com `jogador`, `selecao` (id_selecao + ano), `pais`;
- para "máximo" sem ranking, usar CTE de MAX + JOIN (não LIMIT 1);
- para "top N" listado, usar `ORDER BY ... DESC LIMIT N` (N>1).

SQL_TEMPLATE:
```sql
SELECT j.nome_jogador, p.nome_pais, c.gols_marcados
FROM convocacao c
JOIN jogador j ON c.id_jogador = j.id_jogador
JOIN selecao s ON c.id_selecao = s.id_selecao AND c.ano = s.ano
JOIN pais p ON s.sigla_pais = p.sigla_pais
WHERE c.ano = <ANO> AND c.gols_marcados > 0
ORDER BY c.gols_marcados DESC
LIMIT 10;
```

### mata_mata

USAR QUANDO:
- "caminho do mata-mata"
- "quem foi eliminado por <SELEÇÃO>"
- "quem eliminou <SELEÇÃO>"
- "finais", "semifinais", "quartas", "oitavas"

OBRIGATÓRIO:
- filtrar `partida.tipo_de_fase <> 'Fase de Grupos'`;
- para vencedor, usar `partida.id_vencedor` (não recomputar do placar);
- para fase específica, usar `tipo_de_fase = 'Final'` etc.

SQL_TEMPLATE:
```sql
SELECT pt.tipo_de_fase, pt.data_hora,
       p1.nome_pais AS selecao1, p2.nome_pais AS selecao2,
       pv.nome_pais AS vencedor
FROM partida pt
JOIN selecao s1 ON pt.selecao1 = s1.id_selecao AND pt.ano = s1.ano
JOIN pais p1 ON s1.sigla_pais = p1.sigla_pais
JOIN selecao s2 ON pt.selecao2 = s2.id_selecao AND pt.ano = s2.ano
JOIN pais p2 ON s2.sigla_pais = p2.sigla_pais
LEFT JOIN selecao sv ON pt.id_vencedor = sv.id_selecao AND pt.ano = sv.ano
LEFT JOIN pais pv ON sv.sigla_pais = pv.sigla_pais
WHERE pt.ano = <ANO> AND pt.tipo_de_fase <> 'Fase de Grupos'
ORDER BY pt.data_hora;
```

### classificacao_grupo

USAR QUANDO:
- "tabela do grupo <LETRA>"
- "classificação do grupo"
- "quem liderou o grupo"

OBRIGATÓRIO:
- usar `selecao_grupo` (NÃO recalcular de `partida`);
- ordenar `pontos DESC, saldo_gols DESC, gols_pro DESC`.

SQL_TEMPLATE:
```sql
SELECT p.nome_pais, sg.pontos, sg.gols_pro, sg.gols_contra, sg.saldo_gols
FROM selecao_grupo sg
JOIN selecao s ON sg.id_selecao = s.id_selecao AND sg.ano = s.ano
JOIN pais p ON s.sigla_pais = p.sigla_pais
WHERE sg.ano = <ANO> AND UPPER(sg.letra_grupo) = UPPER('<LETRA>')
ORDER BY sg.pontos DESC, sg.saldo_gols DESC, sg.gols_pro DESC;
```

### historico_selecao

USAR QUANDO:
- "campanha de <SELEÇÃO>"
- "histórico de <SELEÇÃO>"
- "vitórias, empates e derrotas de <SELEÇÃO>"

OBRIGATÓRIO:
- CTE UNION ALL com perspectiva da seleção, filtrando por sigla;
- agregar V/E/D a partir do placar regulamentar + prorrogação.

SQL_TEMPLATE: (esqueleto longo — adapte conforme a pergunta, ver q10 em queries.py)

---

## ARMADILHAS COMUNS

- Não traduzir Alemanha para `ALE`; use `GER`.
- Não usar `HOL` para Holanda; use `NED`.
- Não contar gols com `COUNT(*)`; gols exigem `SUM(...)`.
- Não contar só `selecao1`; a seleção pode estar em qualquer lado.
- Não usar `convocacao.gols_marcados` para gols de seleções ou placares de
  partidas. Essa coluna é para gols de jogadores.
- Não somar pênaltis da disputa ao placar normal quando a pergunta for "gols".
- Não usar `id_vencedor` em fase de grupos (lá ele é NULL).
- Não usar `pais_sede` diretamente como nome; é uma sigla, junte com `pais`.
- Não usar `campea` diretamente como país; é `id_selecao`, junte com `selecao`
  usando também `ano`.
- Não usar `LIMIT 1` em perguntas de "máximo / maior / mais X" sem antes calcular
  o máximo em CTE — empates ficam invisíveis.
- Não filtrar por ano fora do conjunto {1998, 2002, 2006, 2010, 2014, 2018, 2022};
  retorne `-- NAO_SEI`.

---

## PERGUNTAS DE TREINO (recuperadas por similaridade lexical)

Cobertura dos padrões canônicos e variantes; cada entrada indica a tabela/coluna chave.

1. Quantas edições da Copa estão cadastradas? → contar `edicao_da_copa`.
2. Quem sediou a Copa de 2014? → `edicao_da_copa.pais_sede` + `pais`.
3. Em que anos o Brasil sediou a Copa? → sede com `pais.nome_pais ILIKE '%Brasil%'`.
4. Quem foi campeão em cada edição? → `edicao_da_copa.campea` + `selecao` + `pais`.
5. Quem foi campeão em 2022? → `campea` filtrado por ano.
6. Quem foi vice em 2018? → `vice_campeao`.
7. Quem ficou em terceiro em 2010? → `terceiro_colocado`.
8. Liste campeão, vice e terceiro de todas as Copas. → três joins com `selecao`.
9. Quantas seleções participaram da Copa de 2006? → contar `selecao` por ano.
10. Quais seleções da UEFA participaram em 2022? → `pais.id_confederacao` + `confederacao`.
11. Em quais Copas a Argentina participou? → `selecao` + `pais`.
12. Em quais Copas a Alemanha participou? → sigla `GER`.
13. Qual grupo do Brasil em 2014? → `selecao.letra_grupo`.
14. Liste todos os grupos da Copa de 2018. → agrupar por `letra_grupo`.
15. Qual foi a tabela do grupo C de 2022? → padrão `classificacao_grupo`.
16. Quem liderou o grupo D em 2018? → classificação + `LIMIT 1` (líder é único).
17. Qual seleção teve maior saldo no grupo em 2010? → `selecao_grupo.saldo_gols`.
18. Quantos jogos houve na Copa de 2022? → contar `partida` por `ano`.
19. Quantos jogos há em cada edição? → agrupar `partida.ano`.
20. Liste as partidas da Copa de 2014. → `partida` + nomes das duas seleções.
21. Quais partidas foram finais? → filtro `tipo_de_fase = 'Final'`.
22. Quais partidas tiveram o Brasil em 2018? → padrão `jogos_por_selecao` com filtro.
23. Quantos jogos o Brasil fez em 2014? → padrão `jogos_por_selecao` com `BRA`.
24. Quantos jogos a Alemanha fez em cada Copa? → agrupar por `ano`, sigla `GER`.
25. Qual seleção fez mais jogos em uma edição? → padrão `jogos_por_selecao` SEM filtro de sigla, com CTE de MAX.
26. Qual o máximo de jogos de uma seleção em uma Copa? → mesmo padrão.
27. Quais seleções chegaram à final de 2022? → `partida` final + ambos os lados.
28. Quem venceu cada partida de mata-mata de 2022? → padrão `mata_mata`.
29. Qual foi o caminho do campeão de 2014 no mata-mata? → padrão `mata_mata` + campeão.
30. Quais partidas foram decididas nos pênaltis? → `gols_penaltis_* IS NOT NULL`.
31. Quais jogos tiveram prorrogação? → `gols_prorrogacao_* IS NOT NULL`.
32. Qual foi a final com mais gols? → finais, soma regulamentar+prorrogação.
33. Qual seleção fez mais gols em uma única edição? → padrão `gols_por_selecao_em_edicao`.
34. Qual seleção marcou mais gols entre 1998 e 2022? → mesmo padrão sem filtro de ano.
35. Qual seleção sofreu mais gols em 2010? → mesmo padrão invertendo gols pró/contra.
36. Qual adversário mais sofreu gols do Brasil? → padrão `gols_contra_adversario` com `BRA`.
37. Qual adversário mais sofreu gols da Alemanha? → mesmo padrão com `GER`.
38. Contra quem a Argentina mais fez gols? → mesmo padrão com `ARG`.
39. Quantos gols o Brasil marcou por edição? → perspectiva `BRA`, agrupar por ano.
40. Qual foi o saldo de gols da Alemanha em 2014? → perspectiva `GER`, gols pró-contra.
41. Quem marcou mais gols em 2022? → padrão `artilharia_jogador`.
42. Quem são os artilheiros de cada edição? → `artilharia_jogador` agrupado por ano.
43. Quantos gols Messi fez em 2022? → padrão `artilharia_jogador` com `ILIKE '%Messi%'`.
44. Quais jogadores fizeram mais de 3 gols em alguma edição? → filtro `gols_marcados > 3`.
45. Qual foi o elenco do Brasil em 2002? → `convocacao` + `jogador` + `selecao`.
46. Quem vestiu a camisa 10 da Argentina em 2022? → `numero_camisa = 10` + filtros.
47. Quais eventos ocorreram na partida X? → `evento_de_jogo` por `id_partida`.
48. Quais cidades sediaram a Copa de 2014? → `cidade_sedia_edicao`.
49. Qual cidade recebeu mais jogos na base? → `partida` + `estadio`, agrupar cidade.
50. Quantos jogos um campeão fez em sua campanha? → campeão por edição + contagem.
