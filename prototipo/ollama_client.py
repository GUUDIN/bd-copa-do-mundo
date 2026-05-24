"""Integração com Ollama para conversão NL→SQL.

O serviço Ollama roda via Docker. Por padrão assumimos que o container
publica a porta 11434 no host:

    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    docker exec -it ollama ollama pull qwen3.5:2b

Para apontar para outro endereço ou modelo, use as variáveis de ambiente
OLLAMA_HOST e OLLAMA_MODEL.

Estrutura alinhada ao exemplo do professor (endpoint /api/chat com array
de mensagens, temperatura 0.0).
"""
import os
import re
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/chat"
MODELO_PADRAO = os.environ.get("OLLAMA_MODEL", "qwen3.5:2b")

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
"""

SYSTEM_PROMPT = f"""
Você é um assistente especializado em SQL PostgreSQL para um banco da Copa do Mundo da FIFA.
As perguntas do usuário virão em português brasileiro.

Use exclusivamente o seguinte esquema relacional:

{ESQUEMA_SQL}

Convenções importantes do schema:
- A chave primária de `edicao_da_copa` é `ano` (INTEGER). Não existe coluna `id_edicao`.
- Países são identificados por `sigla_pais` VARCHAR(3), ex.: 'BRA', 'ARG', 'FRA'.
- `selecao` tem PK composta `(id_selecao, ano)`. Em todo JOIN com `selecao`,
  case os DOIS campos (ex.: `pt.selecao1 = s.id_selecao AND pt.ano = s.ano`).
- `partida` usa `selecao1`/`selecao2` (não mandante/visitante) e divide gols em
  três pares de colunas: `gols_regulamentares_*`, `gols_prorrogacao_*`, `gols_penaltis_*`.
- `partida.id_vencedor` já guarda o vencedor de eliminatórias — use diretamente.
- `convocacao.gols_marcados` é atualizado por trigger; para "artilheiros" basta
  somar/ordenar essa coluna, sem precisar agregar `evento_de_jogo`.
- Fases em `fase.tipo_de_fase`: 'Fase de Grupos', 'Oitavas de Final',
  'Quartas de Final', 'Semifinais', 'Disputa de Terceiro Lugar', 'Final'.
- Tipos em `evento_de_jogo.tipo_evento`: 'Gol', 'Gol Contra', 'Pênalti Convertido',
  'Cartão Amarelo', 'Cartão Vermelho', 'Substituição'.

Regras:
- Gere apenas consultas SQL compatíveis com PostgreSQL.
- Não invente tabelas nem atributos.
- Para comparar nomes ou siglas digitados pelo usuário, use UPPER(...) = UPPER(%s)
  ou ILIKE — os dados no banco têm capitalização ('Brasil', 'BRA') que pode
  divergir do que o usuário digita.
- Se a pergunta não puder ser respondida com esse esquema, diga que não é possível.
- Quando gerar SQL, retorne APENAS o comando SQL, sem explicações, sem markdown,
  sem cercas ```.

Exemplos:

Pergunta: "Quem foi campeão em 2022?"
SQL: SELECT p.nome_pais FROM edicao_da_copa e JOIN selecao s ON e.campea = s.id_selecao AND e.ano = s.ano JOIN pais p ON s.sigla_pais = p.sigla_pais WHERE e.ano = 2022;

Pergunta: "Quais jogadores do Brasil foram convocados em 2026?"
SQL: SELECT j.nome_jogador, c.numero_camisa FROM convocacao c JOIN jogador j ON c.id_jogador = j.id_jogador JOIN selecao s ON c.id_selecao = s.id_selecao AND c.ano = s.ano WHERE c.ano = 2026 AND UPPER(s.sigla_pais) = 'BRA' ORDER BY c.numero_camisa;

Pergunta: "Quantos gols Messi fez na Copa de 2022?"
SQL: SELECT c.gols_marcados FROM convocacao c JOIN jogador j ON c.id_jogador = j.id_jogador WHERE c.ano = 2022 AND j.nome_jogador ILIKE '%Messi%';
""".strip()


def _extrair_sql(texto):
    """Remove cercas markdown e prefixos comuns, mantendo só o SQL."""
    texto = texto.strip()
    # Remove blocos ```sql ... ``` ou ``` ... ```
    match = re.search(r"```(?:sql)?\s*(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    if match:
        texto = match.group(1).strip()
    # Remove prefixos comuns que o modelo às vezes adiciona
    texto = re.sub(r"^(SQL\s*:\s*)", "", texto, flags=re.IGNORECASE)
    return texto.strip().rstrip(";") + ";"


def gerar_sql(pergunta, modelo=MODELO_PADRAO, timeout=120):
    """Chama o Ollama (endpoint /api/chat) e retorna o SQL gerado.

    Lança ConnectionError se o serviço estiver offline ou retornar erro.
    """
    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pergunta},
    ]

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
            "11434 está publicada. Você pode definir OLLAMA_HOST para outro endereço."
        ) from e
    except requests.exceptions.Timeout as e:
        raise ConnectionError("Tempo esgotado aguardando resposta do Ollama.") from e
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(
            f"Ollama retornou erro HTTP {resposta.status_code}: {resposta.text[:200]}"
        ) from e

    try:
        dados = resposta.json()
    except ValueError as e:
        raise ConnectionError("Resposta do Ollama não é um JSON válido.") from e

    conteudo = dados.get("message", {}).get("content", "")
    return _extrair_sql(conteudo)
