"""Conversão de pergunta em linguagem natural para SQL via Ollama local.

Host e modelo podem ser sobrescritos por OLLAMA_HOST e OLLAMA_MODEL.
"""
import os
import re
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/chat"
MODELO_PADRAO = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:3b")

# Sentinela que o modelo retorna quando a pergunta não pode ser respondida
# usando o schema (ou quando não é sobre dados do banco).
SENTINELA_NAO_SEI = "-- NAO_SEI"


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


SYSTEM_PROMPT = f"""
Você é um gerador de SQL PostgreSQL para um banco de dados sobre Copas do Mundo da FIFA.

REGRAS OBRIGATÓRIAS:
- Responda APENAS com uma consulta SQL PostgreSQL válida.
- Não explique.
- Não use markdown.
- Não coloque ```sql nem ```.
- Não invente tabelas.
- Não invente colunas.
- Use exclusivamente as tabelas e colunas listadas no SCHEMA.
- Se a pergunta não puder ser respondida usando o SCHEMA, responda exatamente:
{SENTINELA_NAO_SEI}
- Se a pergunta não for sobre dados da Copa do Mundo no banco (ex.: pedir um poema, conversar, fazer matemática genérica), responda exatamente:
{SENTINELA_NAO_SEI}
- Não assuma ano, seleção, fase ou edição se o usuário não especificar.
- Gere apenas SELECT (ou WITH ... SELECT). Nunca gere INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Para contar partidas de uma seleção, considere que a seleção pode aparecer tanto em `partida.selecao1` quanto em `partida.selecao2` — some os dois lados.
- Para perguntas de ranking, máximo ou "mais X", use agregação com GROUP BY, ORDER BY ... DESC e LIMIT quando apropriado.
- Para perguntas ambíguas, prefira uma consulta geral (sem filtro de ano/seleção inventado) a inventar valores.
- Para comparações de texto digitadas pelo usuário, use ILIKE ou UPPER(...) = UPPER(...).

CONVENÇÕES DO SCHEMA:
- PK de `edicao_da_copa` é `ano` (INTEGER). Não existe coluna `id_edicao`.
- País usa `sigla_pais` VARCHAR(3), ex.: 'BRA', 'ARG', 'FRA'.
- `selecao` tem PK composta `(id_selecao, ano)`. Em todo JOIN com `selecao` case OS DOIS campos.
- `partida` usa `selecao1`/`selecao2` (não mandante/visitante).
- Gols ficam em três pares: `gols_regulamentares_*`, `gols_prorrogacao_*`, `gols_penaltis_*`.
- `partida.id_vencedor` já guarda o vencedor de eliminatórias.
- `convocacao.gols_marcados` é atualizado por trigger — use para artilheiros.
- Fases válidas: 'Fase de Grupos', 'Oitavas de Final', 'Quartas de Final', 'Semifinais', 'Disputa de Terceiro Lugar', 'Final'.
- Eventos válidos: 'Gol', 'Gol Contra', 'Pênalti Convertido', 'Cartão Amarelo', 'Cartão Vermelho', 'Substituição'.

SCHEMA:
{ESQUEMA_SQL}

EXEMPLOS (a resposta é SEMPRE somente o SQL ou a sentinela, sem qualquer texto extra):

Pergunta: Quantos jogos houve na copa de 2022?
SELECT COUNT(*) AS total_partidas FROM partida WHERE ano = 2022;

Pergunta: Faça um poema.
{SENTINELA_NAO_SEI}

Pergunta: Qual o telefone do presidente da FIFA?
{SENTINELA_NAO_SEI}

Pergunta: Quem foi campeão em 2022?
SELECT p.nome_pais FROM edicao_da_copa e JOIN selecao s ON e.campea = s.id_selecao AND e.ano = s.ano JOIN pais p ON s.sigla_pais = p.sigla_pais WHERE e.ano = 2022;

Pergunta: Liste as seleções da copa de 2022.
SELECT p.nome_pais FROM selecao s JOIN pais p ON s.sigla_pais = p.sigla_pais WHERE s.ano = 2022 ORDER BY p.nome_pais;

Pergunta: Quais foram os artilheiros da copa de 2022?
SELECT j.nome_jogador, p.nome_pais, c.gols_marcados FROM convocacao c JOIN jogador j ON c.id_jogador = j.id_jogador JOIN selecao s ON c.id_selecao = s.id_selecao AND c.ano = s.ano JOIN pais p ON s.sigla_pais = p.sigla_pais WHERE c.ano = 2022 AND c.gols_marcados > 0 ORDER BY c.gols_marcados DESC LIMIT 10;

Pergunta: Qual a quantidade máxima de jogos feita por uma seleção em uma edição de Copa do Mundo?
SELECT s.ano, p.nome_pais, COUNT(pt.id_partida) AS total_jogos FROM selecao s JOIN pais p ON s.sigla_pais = p.sigla_pais JOIN partida pt ON pt.ano = s.ano AND (pt.selecao1 = s.id_selecao OR pt.selecao2 = s.id_selecao) GROUP BY s.ano, p.nome_pais ORDER BY total_jogos DESC LIMIT 1;

Pergunta: Qual seleção fez mais jogos em uma edição de copa?
SELECT s.ano, p.nome_pais, COUNT(pt.id_partida) AS total_jogos FROM selecao s JOIN pais p ON s.sigla_pais = p.sigla_pais JOIN partida pt ON pt.ano = s.ano AND (pt.selecao1 = s.id_selecao OR pt.selecao2 = s.id_selecao) GROUP BY s.ano, p.nome_pais ORDER BY total_jogos DESC LIMIT 1;
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
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pergunta},
        ],
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

    conteudo = dados.get("message", {}).get("content", "")
    return _validar_sql(_limpar_resposta(conteudo))
