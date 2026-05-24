"""Integração com Ollama para conversão NL→SQL.

O serviço Ollama roda via Docker. Por padrão assumimos que o container
publica a porta 11434 no host (docker run -p 11434:11434 ollama/ollama).
Para apontar para outro endereço (ex.: nome de serviço em docker-compose),
defina a variável de ambiente OLLAMA_HOST, ex.:
    OLLAMA_HOST=http://ollama:11434
    OLLAMA_MODEL=qwen2.5-coder
"""
import json
import os
import re
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
MODELO_PADRAO = os.environ.get("OLLAMA_MODEL", "llama3")

SYSTEM_PROMPT = (
    "Você é um assistente especializado em SQL para PostgreSQL. "
    "O banco se chama copa_mundo e contém as tabelas: "
    "confederacao, pais, selecao, tecnico, jogador, arbitro, "
    "edicaocopa, cidadesede, estadio, fase, grupo, selecaogrupo, "
    "participacaoedicao, convocacao, partida, escalaarbitragem, "
    "eventojogo, classificacaogrupo. "
    "Converta a pergunta do usuário em uma única query SQL válida "
    "para PostgreSQL. Retorne APENAS o SQL, sem explicações."
)


def _extrair_sql(texto):
    """Remove cercas markdown e mantém só o SQL."""
    texto = texto.strip()
    # Remove blocos ```sql ... ``` ou ``` ... ```
    match = re.search(r"```(?:sql)?\s*(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    if match:
        texto = match.group(1).strip()
    # Remove prefixos comuns
    texto = re.sub(r"^(SQL\s*:\s*)", "", texto, flags=re.IGNORECASE)
    return texto.strip().rstrip(";") + ";"


def gerar_sql(pergunta, modelo=MODELO_PADRAO, timeout=120):
    """Chama o Ollama e retorna o SQL gerado a partir da pergunta.

    Lança ConnectionError se o serviço estiver offline.
    """
    payload = {
        "model": modelo,
        "system": SYSTEM_PROMPT,
        "prompt": pergunta,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(
            f"Não foi possível conectar ao Ollama em {OLLAMA_HOST}. "
            "Verifique se o container está rodando (docker ps) e se a porta "
            "11434 está publicada. Você pode definir OLLAMA_HOST para outro endereço."
        ) from e
    except requests.exceptions.Timeout as e:
        raise ConnectionError("Tempo esgotado aguardando resposta do Ollama.") from e

    if resp.status_code != 200:
        raise ConnectionError(
            f"Ollama retornou status {resp.status_code}: {resp.text[:200]}"
        )

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        raise ConnectionError("Resposta do Ollama não é um JSON válido.") from e

    texto = data.get("response", "")
    return _extrair_sql(texto)
