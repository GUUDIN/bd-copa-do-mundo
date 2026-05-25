# Treinamento de padrões para NL -> SQL

Este material orienta o modelo a gerar SQL para o schema do projeto. Não contém
respostas prontas. Cada exemplo descreve a intenção, os termos esperados e as
tabelas/colunas que devem ser usadas.

## Escopo dos dados

- A base cobre as Copas de 1998, 2002, 2006, 2010, 2014, 2018 e 2022.
- Todas as edições carregadas usam formato com 32 seleções, fase de grupos e
  mata-mata.
- Não há dados da Copa de 2026.
- "Todas as copas" significa todas as edições carregadas na tabela
  `edicao_da_copa`.
- "Copa", "edição", "mundial" e "torneio" normalmente se referem a
  `edicao_da_copa.ano`.

## Vocabulário do schema

- edição, copa, mundial, torneio -> `edicao_da_copa`
- país sede, sede, anfitrião -> `edicao_da_copa.pais_sede` + `pais`
- campeão, campeã, vencedor da copa -> `edicao_da_copa.campea`
- vice, finalista derrotado -> `edicao_da_copa.vice_campeao`
- terceiro colocado -> `edicao_da_copa.terceiro_colocado`
- seleção, time, equipe, país participante -> `selecao` + `pais`
- grupo, chave -> `grupo`, `selecao.letra_grupo`, `selecao_grupo`
- classificação, tabela, pontos, saldo -> `selecao_grupo`
- partida, jogo, confronto -> `partida`
- fase, etapa -> `partida.tipo_de_fase` ou `fase.tipo_de_fase`
- mata-mata, eliminatórias -> fases diferentes de `'Fase de Grupos'`
- oitavas -> `'Oitavas de Final'`
- quartas -> `'Quartas de Final'`
- semi, semifinal -> `'Semifinais'`
- terceiro lugar -> `'Disputa de Terceiro Lugar'`
- final -> `'Final'`
- elenco, convocados, convocação -> `convocacao` + `jogador`
- camisa, número -> `convocacao.numero_camisa`
- jogador, atleta -> `jogador`
- artilheiro, goleador, gols marcados -> `convocacao.gols_marcados`
- evento, lance -> `evento_de_jogo`
- cartão amarelo/vermelho, substituição, gol, pênalti convertido -> `evento_de_jogo.tipo_evento`
- estádio, cidade -> `estadio`, `cidade_sede`, `cidade_sedia_edicao`

## Regras de modelagem que sempre valem

- Sempre use aliases existentes e qualifique colunas: `s.ano`, `pt.id_partida`.
- Sempre junte `selecao` usando `id_selecao` e `ano`.
- `partida.selecao1` e `partida.selecao2` são os dois lados da partida. Não são
  mandante/visitante.
- Para perguntas "da perspectiva de uma seleção", monte uma CTE com `UNION ALL`
  trazendo os dois lados da partida.
- Para gols de jogo, some gols regulamentares e de prorrogação. Não some
  `gols_penaltis_*`, salvo se a pergunta falar explicitamente em pênaltis.
- Para placar final de jogo com prorrogação, use regulamentar + prorrogação.
- Para vencedor de mata-mata, prefira `partida.id_vencedor`.
- Para artilharia, prefira `convocacao.gols_marcados`, pois é mantida por
  trigger a partir dos eventos.
- Para nomes de países digitados em português, compare com `pais.nome_pais ILIKE`
  ou use a sigla correta.
- Não use siglas inventadas. Alemanha é `GER`, não `ALE`; Holanda é `NED`;
  Inglaterra é `ENG`; Coreia do Sul é `KOR`; Estados Unidos é `USA`.

## Siglas e aliases úteis

- Alemanha/Germany -> `GER`
- Argentina -> `ARG`
- Austrália -> `AUS`
- Bélgica -> `BEL`
- Brasil/Brazil -> `BRA`
- Camarões -> `CMR`
- Canadá -> `CAN`
- Chile -> `CHI`
- Coreia do Sul/South Korea -> `KOR`
- Croácia -> `CRO`
- Dinamarca -> `DEN`
- Equador -> `ECU`
- Espanha/Spain -> `ESP`
- Estados Unidos/EUA/USA -> `USA`
- França/France -> `FRA`
- Gana -> `GHA`
- Holanda/Países Baixos/Netherlands -> `NED`
- Inglaterra/England -> `ENG`
- Irã -> `IRN`
- Itália/Italy -> `ITA`
- Japão/Japan -> `JPN`
- México -> `MEX`
- Marrocos -> `MAR`
- Nigéria -> `NGA`
- Paraguai -> `PAR`
- Polônia -> `POL`
- Portugal -> `POR`
- Rússia -> `RUS`
- Senegal -> `SEN`
- Sérvia -> `SRB`
- Suécia -> `SWE`
- Suíça -> `SUI`
- Tunísia -> `TUN`
- Uruguai -> `URU`

## Padrões de SQL por intenção

- Contar edições: agregue `edicao_da_copa`.
- Listar edições com sede/campeão: `edicao_da_copa` + `pais` + `selecao`.
- Seleções de uma edição: `selecao` + `pais`, filtro `s.ano`.
- Grupo de seleção: `selecao.letra_grupo`, filtro por país e ano.
- Classificação de grupo: `selecao_grupo` + `selecao` + `pais`, ordenar pontos,
  saldo e gols pró.
- Partidas de edição: `partida` + duas junções com `selecao` + duas com `pais`.
- Partidas de seleção: CTE com os dois lados da partida.
- Total de jogos de seleção: conte linhas da CTE por seleção/ano.
- Gols de seleção contra adversários: CTE com os dois lados e soma de gols pró.
- Gols sofridos por seleção: CTE com os dois lados e soma de gols contra.
- Saldo de gols em partidas: gols pró menos gols contra pela perspectiva da
  seleção.
- Artilheiros: `convocacao.gols_marcados` + `jogador` + `selecao` + `pais`.
- Eventos de partida: `evento_de_jogo` + `jogador`, filtro `id_partida`.
- Jogadores de seleção em edição: `convocacao` + `jogador` + `selecao` + `pais`.
- Campeão/vice/terceiro: `edicao_da_copa` com FK para `selecao` e `pais`.
- Mata-mata: `partida.tipo_de_fase <> 'Fase de Grupos'`.
- Finais: `partida.tipo_de_fase = 'Final'`.
- Disputa de pênaltis: use `gols_penaltis_selecao1/2`.
- Jogos decididos na prorrogação: `gols_prorrogacao_* IS NOT NULL` e soma maior
  que zero ou placar final alterado.
- Sedes e cidades: `cidade_sedia_edicao`, `cidade_sede`, `estadio`.

## Perguntas de treino por padrão

1. Quantas edições da Copa estão cadastradas? -> contar `edicao_da_copa`.
2. Quais Copas estão cadastradas? -> listar `edicao_da_copa.ano`.
3. Quais foram os países-sede de todas as edições? -> `edicao_da_copa.pais_sede` + `pais`.
4. Quem sediou a Copa de 2014? -> filtro `e.ano = 2014`.
5. Em que anos o Brasil sediou a Copa na base? -> sede com `pais.nome_pais ILIKE '%Brasil%'`.
6. Quem foi campeão em cada edição? -> `edicao_da_copa.campea`.
7. Quem foi campeão em 2022? -> `campea` + `selecao` + `pais`.
8. Quem foi vice em 2018? -> `vice_campeao`.
9. Quem ficou em terceiro em 2010? -> `terceiro_colocado`.
10. Liste campeão, vice e terceiro de todas as Copas. -> três joins com `selecao` e `pais`.
11. Quantas seleções participaram da Copa de 2006? -> contar `selecao` por ano.
12. Quais seleções jogaram a Copa de 1998? -> `selecao` + `pais`.
13. Quais seleções da UEFA participaram em 2022? -> `pais.id_confederacao` + `confederacao`.
14. Quantas seleções da CONMEBOL participaram em cada edição? -> agrupar por ano.
15. Em quais Copas a Argentina participou? -> `selecao` + `pais`.
16. Em quais Copas a Alemanha participou? -> usar sigla `GER`.
17. Qual grupo do Brasil em 2014? -> `selecao.letra_grupo`.
18. Quais seleções estavam no grupo A de 2022? -> `selecao` + `pais` + grupo.
19. Liste todos os grupos da Copa de 2018. -> `selecao.letra_grupo`, `pais.nome_pais`.
20. Quantas seleções havia em cada grupo de 2010? -> agrupar por `letra_grupo`.
21. Qual foi a tabela do grupo C de 2022? -> `selecao_grupo`, ordenar pontos/saldo/gols.
22. Quem liderou o grupo D em 2018? -> classificação do grupo com `LIMIT 1`.
23. Qual seleção fez mais pontos na fase de grupos de 2014? -> `selecao_grupo`.
24. Qual seleção teve maior saldo no grupo em 2010? -> `saldo_gols`.
25. Qual seleção sofreu menos gols no grupo de 2022? -> `gols_contra`.
26. Quantos jogos houve na Copa de 2022? -> contar `partida` por `ano`.
27. Quantos jogos há em cada edição? -> agrupar `partida.ano`.
28. Liste as partidas da Copa de 2014. -> `partida` + nomes das duas seleções.
29. Quais partidas foram finais? -> filtro `tipo_de_fase = 'Final'`.
30. Quais partidas foram semifinais em 2002? -> fase e ano.
31. Quais partidas tiveram o Brasil em 2018? -> CTE dos dois lados ou OR nos lados.
32. Quais seleções enfrentaram a França em 2022? -> adversários pelos dois lados.
33. Quantos jogos o Brasil fez em 2014? -> contar partidas com `BRA` nos dois lados.
34. Quantos jogos a Alemanha fez em cada Copa? -> agrupar por `s.ano`, sigla `GER`.
35. Qual seleção fez mais jogos em uma edição? -> contar por seleção/ano, ordenar desc.
36. Qual o mínimo de jogos de uma seleção em uma Copa? -> contar por seleção/ano e `MIN`.
37. Qual o máximo de jogos de uma seleção em uma Copa? -> contar por seleção/ano e `MAX`.
38. Quantos jogos uma seleção finalista fez? -> finalistas + contagem de partidas.
39. Quais seleções chegaram à final de 2022? -> `partida` final + seleções dos dois lados.
40. Quais seleções jogaram disputa de terceiro lugar em 2018? -> fase correspondente.
41. Quem venceu cada partida de mata-mata de 2022? -> `id_vencedor` + `pais`.
42. Qual foi o caminho do campeão de 2014 no mata-mata? -> partidas de mata-mata envolvendo campeão.
43. Quais partidas foram decididas nos pênaltis? -> `gols_penaltis_* IS NOT NULL`.
44. Quais jogos tiveram prorrogação? -> `gols_prorrogacao_* IS NOT NULL`.
45. Qual foi a final com mais gols? -> finais, soma regulamentar+prorrogação.
46. Qual foi a partida com mais gols em 2022? -> soma de gols dos dois lados, ordenar.
47. Quantos gols foram marcados em cada edição? -> somar gols regulamentares/prorrogação.
48. Quantos gols de pênaltis houve em disputas por edição? -> somar `gols_penaltis_*`.
49. Qual seleção fez mais gols em partidas em 2014? -> CTE de gols pró pelos dois lados.
50. Qual seleção sofreu mais gols em 2010? -> CTE de gols contra pelos dois lados.
51. Qual adversário mais sofreu gols do Brasil? -> CTE perspectiva `BRA`, agrupar adversário.
52. Qual adversário mais sofreu gols da Alemanha? -> CTE perspectiva `GER`, agrupar adversário.
53. Contra quem a Argentina mais fez gols? -> CTE perspectiva `ARG`, agrupar adversário.
54. Qual adversário mais marcou contra o Brasil? -> CTE perspectiva `BRA`, somar gols contra.
55. Quantos gols o Brasil marcou por edição? -> CTE perspectiva `BRA`, agrupar ano.
56. Quantos gols a França sofreu por edição? -> CTE perspectiva `FRA`, agrupar ano.
57. Qual foi o saldo de gols da Alemanha em 2014? -> gols pró menos gols contra por partidas.
58. Qual seleção teve melhor saldo total em 2022? -> CTE gols pró/contra por seleção.
59. Qual seleção venceu mais partidas? -> usar `id_vencedor` em mata-mata e placar em grupos.
60. Qual seleção perdeu mais partidas? -> perspectiva por seleção e vencedor/placar.
61. Quais jogos terminaram empatados no tempo normal? -> gols regulamentares iguais.
62. Quantos empates houve por edição? -> contar partidas com gols regulamentares iguais.
63. Qual seleção empatou mais jogos? -> perspectiva por seleção, tempo regulamentar.
64. Quem marcou mais gols em 2022? -> `convocacao.gols_marcados`.
65. Quem são os artilheiros de cada edição? -> ranking por ano.
66. Quantos gols Messi fez em 2022? -> `jogador.nome_jogador ILIKE '%Messi%'`.
67. Quantos gols Mbappé fez em 2022? -> artilharia por jogador.
68. Quais jogadores do Brasil marcaram gols em 2014? -> convocação + gols > 0.
69. Quais jogadores fizeram mais de 3 gols em alguma edição? -> filtro `gols_marcados > 3`.
70. Qual país teve o artilheiro de 2018? -> top jogador + país.
71. Liste os 10 maiores artilheiros da base inteira. -> agrupar jogador e somar gols.
72. Qual jogador marcou mais gols por uma seleção em uma edição? -> ordenar `gols_marcados`.
73. Quantos jogadores marcaram gols pela França em 2018? -> convocação + seleção.
74. Qual seleção teve mais jogadores diferentes marcando em 2022? -> contar jogadores com gols > 0.
75. Qual foi o elenco do Brasil em 2002? -> `convocacao` + `jogador` + `selecao`.
76. Quem vestiu a camisa 10 da Argentina em 2022? -> número camisa + seleção/ano.
77. Liste os jogadores convocados da Alemanha em 2014. -> elenco por sigla/ano.
78. Quantos jogadores foram convocados por seleção em 2018? -> contar convocação por seleção.
79. Quais jogadores de Portugal em 2022 fizeram gols? -> `gols_marcados > 0`.
80. Qual seleção teve mais gols de jogadores convocados em 2010? -> somar `gols_marcados`.
81. Quais eventos ocorreram na partida 1? -> `evento_de_jogo` por `id_partida`.
82. Quantos gols aparecem em eventos na Copa de 2022? -> eventos tipo Gol/Pênalti Convertido/Gol Contra por ano.
83. Quais partidas tiveram gol contra? -> `evento_de_jogo.tipo_evento = 'Gol Contra'`.
84. Quais jogadores marcaram pênalti convertido? -> evento tipo `'Pênalti Convertido'`.
85. Quantos cartões amarelos há na base? -> evento tipo `'Cartão Amarelo'`.
86. Quantos cartões vermelhos há por edição? -> evento + partida, agrupar ano.
87. Em que minuto saiu o primeiro gol de uma partida? -> `MIN(evento_de_jogo.tempo)`.
88. Quais jogadores marcaram após os 90 minutos? -> `evento_de_jogo.tempo > '01:30:00'`.
89. Quais estádios receberam jogos em 2022? -> `partida` + `estadio`, agrupar cidade/estado.
90. Quais cidades sediaram a Copa de 2014? -> `cidade_sedia_edicao`.
91. Quantas cidades-sede houve em cada edição? -> agrupar `cidade_sedia_edicao`.
92. Qual cidade recebeu mais jogos na base? -> `partida` + `estadio`, agrupar cidade.
93. Quantos jogos aconteceram em cada cidade em 2018? -> filtro ano.
94. Em quais cidades o Brasil jogou em 2014? -> partidas do Brasil + estádio/cidade.
95. Qual confederação teve mais seleções em 2022? -> `pais` + `confederacao`.
96. Quantos títulos tem cada país na base? -> `edicao_da_copa.campea`.
97. Quantas finais cada seleção disputou? -> final e dois lados.
98. Quantas vezes cada seleção ficou em terceiro? -> `terceiro_colocado`.
99. Qual país chegou mais vezes ao top 3? -> união de campeão/vice/terceiro.
100. Qual seleção participou de mais edições? -> contar `selecao` por país.
101. Quais seleções participaram de todas as edições carregadas? -> contar anos distintos igual total de edições.
102. Quais seleções participaram apenas uma vez? -> contar anos distintos igual 1.
103. Em quais anos Brasil e Alemanha se enfrentaram? -> partidas com `BRA` e `GER` em lados opostos.
104. Qual foi o placar de Brasil contra Alemanha? -> partida com os dois lados e gols.
105. Quantas vezes Argentina enfrentou Holanda? -> lados opostos `ARG` e `NED`.
106. Qual adversário o Brasil enfrentou mais vezes? -> CTE adversários do Brasil, contar.
107. Qual seleção enfrentou mais adversários diferentes? -> pares de seleções, contar distintos.
108. Quantos jogos de mata-mata cada seleção disputou? -> fase diferente de grupos, perspectiva seleção.
109. Qual seleção mais jogou finais? -> `partida.tipo_de_fase = 'Final'`, ambos os lados.
110. Quais finais foram decididas nos pênaltis? -> final com `gols_penaltis_* IS NOT NULL`.
111. Qual final teve maior diferença de gols? -> finais e diferença absoluta.
112. Qual foi a maior goleada da base? -> diferença absoluta de gols final da partida.
113. Qual seleção aplicou a maior goleada? -> perspectiva vencedor/gols pró.
114. Qual seleção sofreu a maior goleada? -> perspectiva perdedor/gols contra.
115. Qual edição teve mais gols? -> soma gols por ano.
116. Qual edição teve menos gols? -> soma gols por ano, ordenar asc.
117. Média de gols por jogo em cada edição. -> soma gols dividido por contagem de partidas.
118. Média de gols do Brasil por jogo em cada edição. -> CTE perspectiva `BRA`.
119. Qual fase teve mais gols em 2022? -> agrupar `tipo_de_fase`.
120. Qual fase tem mais jogos no formato carregado? -> contar partidas por `tipo_de_fase`.
121. Quantos jogos de fase de grupos existem por edição? -> `tipo_de_fase = 'Fase de Grupos'`.
122. Quantos jogos de mata-mata existem por edição? -> fase diferente de grupos.
123. Quais seleções foram campeãs invictas na base? -> requer vitórias/empates/derrotas por seleção campeã.
124. Quais campeões tiveram mais gols marcados? -> campeão por edição + CTE gols pró.
125. Quais campeões sofreram menos gols? -> campeão por edição + CTE gols contra.
126. Quem eliminou o Brasil em cada Copa? -> jogos de mata-mata do Brasil em que `id_vencedor` não é Brasil.
127. Quem eliminou a Alemanha em cada Copa? -> usar `GER`.
128. Qual seleção eliminou mais adversários no mata-mata? -> `id_vencedor`, contar partidas de mata-mata.
129. Quantas partidas cada país venceu no mata-mata? -> `id_vencedor` por país.
130. Quantos jogos um campeão fez em sua campanha? -> campeão por edição + contagem de partidas.

## Armadilhas comuns

- Não traduzir Alemanha para `ALE`; use `GER`.
- Não contar gols com `COUNT(*)`; gols exigem `SUM(...)`.
- Não contar só `selecao1`; a seleção pode estar em qualquer lado.
- Não agrupar por alias inexistente.
- Não usar `convocacao.gols_marcados` para gols de seleções ou placares de
  partidas. Essa coluna é para gols de jogadores.
- Não usar `id_vencedor` para jogos de fase de grupos quando ele é `NULL`; em
  grupos, determine vitória pelo placar regulamentar.
- Não somar pênaltis da disputa ao placar normal quando a pergunta for "gols".
- Não assumir que "Holanda" é `HOL`; use `NED`.
- Não usar `pais_sede` diretamente como nome; é uma sigla, junte com `pais`.
- Não usar `campea` diretamente como país; é `id_selecao`, junte com `selecao`
  usando também `ano`.
