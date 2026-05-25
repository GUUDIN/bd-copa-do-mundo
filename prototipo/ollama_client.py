"""Conversão de pergunta em linguagem natural para SQL via Ollama local.

Host e modelo podem ser sobrescritos por OLLAMA_HOST e OLLAMA_MODEL.
"""
import os
import re
import requests
import sqlparse
import unicodedata
from pathlib import Path

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/chat"
MODELO_PADRAO = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:3b")

# Sentinela que o modelo retorna quando a pergunta não pode ser respondida
# usando o schema (ou quando não é sobre dados do banco).
SENTINELA_NAO_SEI = "-- NAO_SEI"


def _carregar_treinamento():
    caminho = Path(__file__).with_name("IA_TREINAMENTO.md")
    try:
        return caminho.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


TREINAMENTO_IA = _carregar_treinamento()


ESQUEMA_SQL = """
CREATE TABLE confederacao (
    id_confederacao SERIAL PRIMARY KEY,
    nome_confederacao VARCHAR(255) NOT NULL
);

CREATE TABLE pais (
    sigla_pais VARCHAR(3) PRIMARY KEY,
    nome_pais VARCHAR(255),
    id_confederacao INTEGER NOT NULL REFERENCES confederacao(id_confederacao)
);

CREATE TABLE edicao_da_copa (
    ano INTEGER PRIMARY KEY,
    pais_sede VARCHAR(3) NOT NULL REFERENCES pais(sigla_pais),
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    campea INTEGER,           -- FK para selecao(id_selecao, ano)
    vice_campeao INTEGER,     -- FK para selecao(id_selecao, ano)
    terceiro_colocado INTEGER -- FK para selecao(id_selecao, ano)
);

CREATE TABLE cidade_sede (
    cidade VARCHAR(255),
    estado VARCHAR(2),
    PRIMARY KEY (cidade, estado)
);

CREATE TABLE cidade_sedia_edicao (
    cidade VARCHAR(255),
    estado VARCHAR(2),
    ano_edicao INTEGER REFERENCES edicao_da_copa(ano),
    PRIMARY KEY (cidade, estado, ano_edicao)
);

CREATE TABLE estadio (
    id_estadio SERIAL PRIMARY KEY,
    cidade VARCHAR(255) NOT NULL,
    estado VARCHAR(2) NOT NULL
);

CREATE TABLE fase (
    tipo_de_fase VARCHAR(50),  -- 'Fase de Grupos', 'Oitavas de Final',
                               -- 'Quartas de Final', 'Semifinais',
                               -- 'Disputa de Terceiro Lugar', 'Final'
    ano INTEGER REFERENCES edicao_da_copa(ano),
    PRIMARY KEY (tipo_de_fase, ano)
);

CREATE TABLE grupo (
    letra_grupo CHAR(1),
    ano INTEGER REFERENCES edicao_da_copa(ano),
    PRIMARY KEY (letra_grupo, ano)
);

CREATE TABLE tecnico (
    id_tecnico SERIAL PRIMARY KEY,
    nome_tecnico VARCHAR(255) NOT NULL
);

CREATE TABLE selecao (
    id_selecao SERIAL,
    ano INTEGER NOT NULL,
    letra_grupo CHAR(1) NOT NULL,
    id_tecnico INTEGER NOT NULL REFERENCES tecnico(id_tecnico),
    sigla_pais VARCHAR(3) NOT NULL REFERENCES pais(sigla_pais),
    PRIMARY KEY (id_selecao, ano),
    UNIQUE (sigla_pais, ano)
);

CREATE TABLE selecao_grupo (
    id_selecao INTEGER,
    ano INTEGER,
    letra_grupo CHAR(1),
    pontos INTEGER NOT NULL,
    gols_pro INTEGER,
    gols_contra INTEGER,
    saldo_gols INTEGER GENERATED ALWAYS AS (gols_pro - gols_contra) STORED,
    PRIMARY KEY (id_selecao, letra_grupo, ano)
);

CREATE TABLE jogador (
    id_jogador SERIAL PRIMARY KEY,
    nome_jogador VARCHAR(255) NOT NULL
);

CREATE TABLE convocacao (
    ano INTEGER NOT NULL,
    id_selecao INTEGER NOT NULL,
    id_jogador INTEGER NOT NULL REFERENCES jogador(id_jogador),
    numero_camisa INTEGER NOT NULL,
    gols_marcados INTEGER,
    PRIMARY KEY (id_jogador, ano)
);

CREATE TABLE partida (
    id_partida SERIAL PRIMARY KEY,
    tipo_de_fase VARCHAR(50) NOT NULL,
    ano INTEGER NOT NULL,
    id_estadio INTEGER NOT NULL REFERENCES estadio(id_estadio),
    data_hora TIMESTAMP NOT NULL,
    selecao1 INTEGER NOT NULL,
    selecao2 INTEGER NOT NULL,
    gols_regulamentares_selecao1 INTEGER,
    gols_regulamentares_selecao2 INTEGER,
    gols_prorrogacao_selecao1 INTEGER,
    gols_prorrogacao_selecao2 INTEGER,
    gols_penaltis_selecao1 INTEGER,
    gols_penaltis_selecao2 INTEGER,
    id_vencedor INTEGER
);

CREATE TABLE arbitro (
    id_arbitro SERIAL PRIMARY KEY
);

CREATE TABLE arbitragem_partida (
    id_partida INTEGER REFERENCES partida(id_partida),
    id_arbitro INTEGER REFERENCES arbitro(id_arbitro),
    funcao VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_partida, id_arbitro)
);

CREATE TABLE evento_de_jogo (
    id_evento SERIAL,
    id_jogador INTEGER REFERENCES jogador(id_jogador),
    id_partida INTEGER REFERENCES partida(id_partida),
    tipo_evento VARCHAR(50) NOT NULL,  -- 'Gol', 'Gol Contra',
                                        -- 'Pênalti Convertido',
                                        -- 'Cartão Amarelo', 'Cartão Vermelho',
                                        -- 'Substituição'
    tempo TIME NOT NULL,
    PRIMARY KEY (id_evento, id_partida)
);
""".strip()


# Anos que existem no DML. Fora desse conjunto, IA deve responder NAO_SEI.
ANOS_DISPONIVEIS = (1998, 2002, 2006, 2010, 2014, 2018, 2022)


SYSTEM_PROMPT = f"""
Você é um gerador de SQL PostgreSQL para um banco de dados sobre Copas do Mundo da FIFA.

REGRAS OBRIGATÓRIAS:
- Responda APENAS com uma consulta SQL PostgreSQL válida ou exatamente `{SENTINELA_NAO_SEI}`.
- Não explique. Não use markdown. Não coloque ```sql nem ```.
- Gere apenas SELECT (ou WITH ... SELECT). Nunca INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Use exclusivamente tabelas e colunas listadas no SCHEMA.
- Para textos digitados pelo usuário use ILIKE ou UPPER(...) = UPPER(...).
- Sempre qualifique colunas com alias (`s.ano`, `pt.id_partida`).

ESCOPO TEMPORAL:
- A base tem exatamente 7 edições: 1998, 2002, 2006, 2010, 2014, 2018 e 2022.
- Se a pergunta citar um ano fora desse conjunto (ex.: 1990, 1994, 2026, 1970,
  2030), responda exatamente: {SENTINELA_NAO_SEI}
- Se a pergunta disser "todas as copas", "todas as edições", "no geral" ou
  não citar ano, NÃO filtre por ano — o resultado natural cobre só essas 7.

REGRAS CRÍTICAS (estatísticas baseadas em partidas):
1. "Perspectiva de UMA seleção" (pergunta cita uma seleção específica): normalize
   `partida` com UNION ALL em duas linhas (uma com a seleção como `selecao1`,
   outra como `selecao2`) e filtre por `sigla_pais` em AMBOS os lados.
2. "Estatística sobre TODAS as seleções" (não cita seleção específica): mesma
   normalização UNION ALL, SEM filtro de sigla. Agrupe por `ano + sigla_pais`.
3. Gols MARCADOS da seleção do lado X = `gols_regulamentares_selecaoX + gols_prorrogacao_selecaoX`.
4. Gols SOFRIDOS da seleção do lado X = mesma expressão do lado oposto Y.
5. Nunca use `gols_penaltis_*` como gols de jogo (só para "disputa de pênaltis").
6. "Em uma única edição" → GROUP BY ano + sigla_pais.
7. "Máximo / maior / mais X" → calcule MAX em CTE auxiliar e retorne TODOS os
   empatados via JOIN. NUNCA use LIMIT 1 nesses casos.
8. Adversário só entra em GROUP BY se a pergunta falar "adversário", "contra
   quem", "contra qual seleção". Nunca atribua gols de uma seleção ao adversário.
9. Gols de JOGADORES → `convocacao.gols_marcados`.
   Gols de SELEÇÕES / placares → tabela `partida`. Nunca confunda.

CONVENÇÕES DO SCHEMA:
- PK de `edicao_da_copa` é `ano` (INTEGER).
- `selecao` tem PK composta `(id_selecao, ano)`. Em todo JOIN com `selecao` case OS DOIS campos.
- `partida` usa `selecao1`/`selecao2` (não mandante/visitante).
- `partida.id_vencedor` já guarda o vencedor de eliminatórias.
- Siglas: Alemanha=GER, Brasil=BRA, Argentina=ARG, França=FRA, Espanha=ESP,
  Holanda=NED, Inglaterra=ENG, Itália=ITA, Portugal=POR, Estados Unidos=USA,
  Japão=JPN, Coreia do Sul=KOR, México=MEX, Croácia=CRO.
- Fases: 'Fase de Grupos', 'Oitavas de Final', 'Quartas de Final', 'Semifinais',
  'Disputa de Terceiro Lugar', 'Final'.

SCHEMA:
{ESQUEMA_SQL}

PADRÕES/EXEMPLOS RECUPERADOS POR INTENÇÃO:
__TREINAMENTO_DINAMICO__

EXEMPLOS BASE (resposta é SEMPRE somente o SQL ou a sentinela):

Pergunta: Quantos jogos houve na copa de 2022?
SELECT COUNT(*) AS total_partidas FROM partida WHERE ano = 2022;

Pergunta: Quem foi campeão em 2022?
SELECT p.nome_pais FROM edicao_da_copa e JOIN selecao s ON e.campea = s.id_selecao AND e.ano = s.ano JOIN pais p ON s.sigla_pais = p.sigla_pais WHERE e.ano = 2022;

Pergunta: Quem foi campeão em 1994?
{SENTINELA_NAO_SEI}

Pergunta: Faça um poema.
{SENTINELA_NAO_SEI}
""".strip()


# Comandos que nunca podem aparecer na saída do modelo.
_COMANDOS_PROIBIDOS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)
# Início válido para uma consulta de leitura.
_COMECO_VALIDO = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)


class RespostaNaoSei(Exception):
    """O modelo respondeu com a sentinela -- NAO_SEI."""


def _normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower()
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def _tokens(texto):
    ignorar = {
        "a", "as", "o", "os", "um", "uma", "de", "da", "do", "das", "dos",
        "em", "na", "no", "nas", "nos", "para", "por", "que", "qual",
        "quais", "quanto", "quantos", "com", "todas", "todos", "copa",
        "copas", "mundo", "selecao", "selecoes",
    }
    return {tok for tok in _normalizar_texto(texto).split() if len(tok) > 2 and tok not in ignorar}


def _extrair_padroes_canonicos(documento):
    """Parser de blocos `### <nome>` ... (até o próximo `###` ou `---`).

    Retorna lista de dicts {nome, gatilhos, texto_completo}, onde `gatilhos` são
    os tokens normalizados do bloco USAR QUANDO.
    """
    secao_padroes = re.search(
        r"## PADRÕES CANÔNICOS\s*(.*?)(?=^---|\Z)",
        documento,
        re.DOTALL | re.MULTILINE,
    )
    if not secao_padroes:
        return []

    padroes = []
    for match in re.finditer(
        r"### (\S+)\s*\n(.*?)(?=^### |\Z)",
        secao_padroes.group(1),
        re.DOTALL | re.MULTILINE,
    ):
        nome = match.group(1).strip()
        corpo = match.group(2).strip()

        usar_quando = re.search(r"USAR QUANDO:\s*(.*?)(?:OBRIGATÓRIO|SQL_TEMPLATE|\Z)", corpo, re.DOTALL)
        gatilhos = _tokens(usar_quando.group(1) if usar_quando else "")

        padroes.append({
            "nome": nome,
            "gatilhos": gatilhos,
            "texto": f"### {nome}\n{corpo}",
        })
    return padroes


_PADROES_CANONICOS = _extrair_padroes_canonicos(TREINAMENTO_IA)


def _treinamento_relevante(pergunta, limite_perguntas=8, limite_padroes=2):
    """Seleciona padrões canônicos e perguntas de treino relevantes.

    Estratégia lexical (sem embeddings):
    1. Padrões canônicos: rank por match de tokens entre pergunta e gatilhos
       do "USAR QUANDO". Top N injetado COMPLETO (regras + SQL_TEMPLATE).
    2. Perguntas de treino: rank por match de tokens entre pergunta e linha.
       Top M injetado como lista curta.
    """
    if not TREINAMENTO_IA:
        return ""

    termos_pergunta = _tokens(pergunta)
    if not termos_pergunta:
        return ""

    # 1. Padrões canônicos por gatilho
    ranqueados_padroes = []
    for padrao in _PADROES_CANONICOS:
        score = len(termos_pergunta & padrao["gatilhos"])
        if score >= 2:  # exige pelo menos 2 tokens em comum para evitar match espúrio
            ranqueados_padroes.append((score, padrao))
    ranqueados_padroes.sort(key=lambda x: x[0], reverse=True)
    padroes_selecionados = [p["texto"] for _score, p in ranqueados_padroes[:limite_padroes]]

    # 2. Perguntas de treino
    marcador_perguntas = "## PERGUNTAS DE TREINO"
    marcador_armadilhas = "## ARMADILHAS COMUNS"
    perguntas_texto = ""
    armadilhas = ""
    if marcador_perguntas in TREINAMENTO_IA:
        _cab, resto = TREINAMENTO_IA.split(marcador_perguntas, 1)
        if marcador_armadilhas in _cab:
            armadilhas = _cab.split(marcador_armadilhas, 1)[1]
        perguntas_texto = resto

    perguntas = [
        linha.strip()
        for linha in perguntas_texto.splitlines()
        if re.match(r"^\d+\.", linha.strip())
    ]
    ranqueadas = []
    for indice, linha in enumerate(perguntas):
        termos_linha = _tokens(linha)
        score = len(termos_pergunta & termos_linha)
        if score:
            ranqueadas.append((score, -indice, linha))
    perguntas_selecionadas = [
        linha for _score, _idx, linha in sorted(ranqueadas, reverse=True)[:limite_perguntas]
    ]

    # 3. Armadilhas relevantes
    armadilhas_relevantes = []
    for linha in armadilhas.splitlines():
        linha = linha.strip()
        if linha.startswith("-") and (_tokens(linha) & termos_pergunta):
            armadilhas_relevantes.append(linha)

    partes = []
    if padroes_selecionados:
        partes.append("PADRÕES CANÔNICOS RELEVANTES:\n\n" + "\n\n".join(padroes_selecionados))
    if perguntas_selecionadas:
        partes.append("PERGUNTAS DE TREINO RELEVANTES:\n" + "\n".join(perguntas_selecionadas))
    if armadilhas_relevantes:
        partes.append("ARMADILHAS RELEVANTES:\n" + "\n".join(armadilhas_relevantes[:5]))
    return "\n\n".join(partes).strip()


def _system_prompt(pergunta):
    return SYSTEM_PROMPT.replace(
        "__TREINAMENTO_DINAMICO__",
        _treinamento_relevante(pergunta),
    )


def _chamar_ollama(mensagens, modelo=MODELO_PADRAO, timeout=300):
    payload = {
        "model": modelo,
        "messages": mensagens,
        "stream": False,
        "options": {"temperature": 0.0},
    }

    try:
        resposta = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resposta.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(
            f"Não foi possível conectar ao Ollama em {OLLAMA_HOST}. "
            "Verifique se o container está rodando (docker ps) e se a porta "
            "11434 está publicada. Defina OLLAMA_HOST se necessário."
        ) from e
    except requests.exceptions.Timeout as e:
        raise ConnectionError(
            f"Tempo esgotado ({timeout}s) aguardando resposta do Ollama. "
            "Tente uma pergunta mais simples ou aguarde — o primeiro pedido "
            "após subir o container é mais lento (carregamento do modelo)."
        ) from e
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(
            f"Ollama retornou erro HTTP {resposta.status_code}: {resposta.text[:200]}"
        ) from e

    try:
        dados = resposta.json()
    except ValueError as e:
        raise ConnectionError("Resposta do Ollama não é um JSON válido.") from e

    return dados.get("message", {}).get("content", "")


def _limpar_resposta(texto):
    """Remove cercas markdown, prefixos comuns e espaços extras."""
    texto = texto.strip()

    # Se veio em bloco ```sql ... ```, extrai o miolo.
    match = re.search(r"```(?:sql|postgres|postgresql)?\s*(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    if match:
        texto = match.group(1).strip()

    # Remove prefixos como "SQL:", "Resposta:", "Answer:".
    texto = re.sub(r"^\s*(SQL|Resposta|Answer|Query)\s*:\s*", "", texto, flags=re.IGNORECASE)

    return texto.strip()


def _validar_sql(texto):
    """Valida a saída do modelo e retorna o SQL pronto para execução.

    Lança RespostaNaoSei se o modelo sinalizou que não sabe.
    Lança ValueError em qualquer outra saída inválida.
    """
    if not texto:
        raise ValueError("O modelo retornou resposta vazia.")

    # Sentinela: aceita qualquer linha que comece com -- NAO_SEI.
    if texto.upper().startswith(SENTINELA_NAO_SEI.upper()):
        raise RespostaNaoSei(
            "A pergunta não pôde ser respondida com os dados disponíveis. "
            "Tente reformular usando termos do schema "
            "(seleção, partida, edição, ano, fase, jogador, etc.)."
        )

    # Markdown que escapou da limpeza → rejeita.
    if "```" in texto:
        raise ValueError("Resposta contém marcação markdown e foi rejeitada.")

    # Tem que começar com SELECT ou WITH.
    if not _COMECO_VALIDO.match(texto):
        raise ValueError(
            "O modelo não gerou uma consulta SELECT válida. "
            "Tente reformular a pergunta (ex.: 'Quantos jogos houve na copa de 2022?')."
        )

    comandos = [cmd.strip() for cmd in sqlparse.split(texto) if cmd.strip()]
    if len(comandos) != 1:
        raise ValueError("Resposta contém múltiplos comandos SQL e foi rejeitada.")

    # Não pode conter comandos de escrita/DDL.
    if _COMANDOS_PROIBIDOS.search(texto):
        raise ValueError("Resposta contém comando proibido (INSERT/UPDATE/DELETE/DDL) e foi rejeitada.")

    return texto.rstrip(";").strip() + ";"


def gerar_sql(pergunta, modelo=MODELO_PADRAO, timeout=300):
    """Chama o Ollama e retorna SQL validado.

    Pode lançar:
      - ConnectionError: falha de rede / timeout / HTTP.
      - RespostaNaoSei: modelo sinalizou que não sabe.
      - ValueError: saída inválida (markdown, comando proibido, vazio, etc.).
    """
    conteudo = _chamar_ollama(
        [
            {"role": "system", "content": _system_prompt(pergunta)},
            {"role": "user", "content": pergunta},
        ],
        modelo=modelo,
        timeout=timeout,
    )
    return _validar_sql(_limpar_resposta(conteudo))


def corrigir_sql(pergunta, sql_invalido, erro_postgres, modelo=MODELO_PADRAO, timeout=300):
    """Pede ao modelo para corrigir uma consulta rejeitada pelo PostgreSQL."""
    pedido = f"""
Pergunta original:
{pergunta}

SQL gerado que falhou:
{sql_invalido}

Erro retornado pelo PostgreSQL:
{erro_postgres}

Corrija a consulta. Responda somente com SQL PostgreSQL válido, sem explicações.
""".strip()
    conteudo = _chamar_ollama(
        [
            {"role": "system", "content": _system_prompt(pergunta)},
            {"role": "user", "content": pedido},
        ],
        modelo=modelo,
        timeout=timeout,
    )
    return _validar_sql(_limpar_resposta(conteudo))


def revisar_sql_sem_resultados(pergunta, sql_sem_resultados, modelo=MODELO_PADRAO, timeout=300):
    """Pede revisão quando o SQL compila, mas retorna zero linhas."""
    pedido = f"""
Pergunta original:
{pergunta}

SQL gerado compilou, mas retornou zero linhas:
{sql_sem_resultados}

Revise filtros de país/seleção, siglas e joins. Se houver nome de país em português,
prefira comparar com `pais.nome_pais ILIKE` ou use a sigla correta do banco.
Responda somente com SQL PostgreSQL válido, sem explicações.
""".strip()
    conteudo = _chamar_ollama(
        [
            {"role": "system", "content": _system_prompt(pergunta)},
            {"role": "user", "content": pedido},
        ],
        modelo=modelo,
        timeout=timeout,
    )
    return _validar_sql(_limpar_resposta(conteudo))
