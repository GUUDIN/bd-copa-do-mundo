"""Bateria de testes comportamentais da camada IA (NL -> SQL).

Cada teste descreve uma pergunta e propriedades que o SQL gerado deve satisfazer.
Não comparamos SQL exato (o modelo pode escolher aliases diferentes), apenas
checamos que regras críticas foram aplicadas:
    - usa UNION ALL quando devia;
    - não usa LIMIT 1 em perguntas de máximo;
    - usa a tabela certa;
    - executa sem erro;
    - retorna número plausível de linhas.

Como rodar:
    cd prototipo
    OLLAMA_HOST=http://<ip>:11434 python -m tests.test_ia

Pré-requisitos: PostgreSQL com DDL+DML carregados, Ollama com qwen2.5-coder:3b.
"""
import os
import re
import sys
import time
from pathlib import Path

# Permite rodar como `python -m tests.test_ia` ou `python tests/test_ia.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2  # noqa: E402

from db import Database  # noqa: E402
import ollama_client  # noqa: E402


HOST_DEFAULT = os.environ.get("PG_HOST", "172.17.0.3")
PORT_DEFAULT = os.environ.get("PG_PORT", "5432")
DB_DEFAULT = os.environ.get("PG_DB", "copa_mundo")
USER_DEFAULT = os.environ.get("PG_USER", "postgres")
PASS_DEFAULT = os.environ.get("PG_PASS", "copa123")


def _normaliza(sql):
    return re.sub(r"\s+", " ", sql or "").upper()


# Cada teste é um dict. Chaves opcionais:
#   esperado_nao_sei: bool
#   deve_conter: lista de substrings (case-insensitive, comparadas no SQL normalizado)
#   nao_deve_conter: lista de substrings
#   executa_sem_erro: bool (default True quando há SQL)
#   linhas_min: int — número mínimo de linhas esperadas
#   linhas_max: int — número máximo de linhas esperadas
#   valor_esperado: dict {coluna: valor} — checa se aparece em alguma linha
TESTES = [
    {
        "id": "max_jogos_campea",
        "pergunta": "Qual seleção marcou mais gols em uma única edição entre 1998 e 2022?",
        "deve_conter": ["UNION ALL", "GROUP BY"],
        "nao_deve_conter": [" LIMIT 1"],
        "executa_sem_erro": True,
        "linhas_min": 1,
    },
    {
        "id": "jogos_argentina_2022",
        "pergunta": "Quantos jogos a Argentina disputou na copa de 2022?",
        "deve_conter": ["ARG"],
        "executa_sem_erro": True,
        "linhas_min": 1,
    },
    {
        "id": "artilheiro_2022",
        "pergunta": "Quem foi o artilheiro da copa de 2022?",
        "deve_conter": ["CONVOCACAO", "GOLS_MARCADOS"],
        "nao_deve_conter": [],
        "executa_sem_erro": True,
        "linhas_min": 1,
    },
    {
        "id": "campeoes_todas",
        "pergunta": "Liste os campeões de todas as copas.",
        "deve_conter": ["EDICAO_DA_COPA", "CAMPEA", "NOME_PAIS"],
        "executa_sem_erro": True,
        "linhas_min": 5,  # tolerante: 5 países distintos ou 7 edições
        "linhas_max": 7,
    },
    {
        "id": "campeao_2022",
        "pergunta": "Quem foi campeão em 2022?",
        "deve_conter": ["= 2022"],
        "executa_sem_erro": True,
        "linhas_min": 1,
        "linhas_max": 1,
    },
    {
        "id": "ano_fora_escopo",
        "pergunta": "Quem foi campeão em 1994?",
        "esperado_nao_sei": True,
    },
    {
        # Modelo pequeno pode gerar SQL ao invés de NAO_SEI; aceita ambos os
        # caminhos válidos: NAO_SEI ou SQL que executa e retorna 0 linhas
        # (o CLI mostra o aviso "base só tem 1998-2022" nesse caso).
        "id": "ano_2026",
        "pergunta": "Quem foi campeão da Copa de 2026?",
        "esperado_nao_sei_ou_vazio": True,
    },
    {
        # Aceita NAO_SEI ou ValueError (modelo gera texto que não é SELECT).
        "id": "poema",
        "pergunta": "Faça um poema sobre futebol.",
        "esperado_nao_sei_ou_invalido": True,
    },
    {
        # Modelo às vezes gera SELECT 2+2 trivial (sintaticamente válido).
        # Aceitamos NAO_SEI, erro, OU SQL sem referência ao schema da copa.
        "id": "matematica",
        "pergunta": "Quanto é 2 + 2?",
        "esperado_nao_sei_ou_sem_schema": True,
    },
    {
        "id": "classificacao_grupo_a",
        "pergunta": "Qual foi a tabela do grupo A em 2022?",
        "deve_conter": ["SELECAO_GRUPO", "PONTOS"],
        "executa_sem_erro": True,
        "linhas_min": 4,
        "linhas_max": 4,
    },
    {
        "id": "partidas_2014",
        "pergunta": "Quantos jogos houve na copa de 2014?",
        "deve_conter": ["PARTIDA"],
        "executa_sem_erro": True,
        "linhas_min": 1,
    },
    {
        "id": "adversario_brasil",
        "pergunta": "Qual adversário mais sofreu gols do Brasil?",
        "deve_conter": ["UNION ALL", "BRA"],
        "executa_sem_erro": True,
        "linhas_min": 1,
    },
]


def avaliar(teste, sql_resultado, exec_resultado):
    """Retorna lista de (ok: bool, msg: str)."""
    checks = []

    if teste.get("esperado_nao_sei"):
        ok = sql_resultado == "__NAO_SEI__"
        checks.append((ok, "Modelo respondeu NAO_SEI" if ok else f"Esperava NAO_SEI, recebeu: {sql_resultado[:80]}"))
        return checks

    # Aceita NAO_SEI ou SQL que executa e retorna 0 linhas
    if teste.get("esperado_nao_sei_ou_vazio"):
        if sql_resultado == "__NAO_SEI__":
            checks.append((True, "NAO_SEI (caminho preferido)"))
        elif sql_resultado.startswith("__ERRO__"):
            checks.append((True, "Saída inválida tratada (caminho aceitável)"))
        elif exec_resultado and not isinstance(exec_resultado, Exception):
            _cols, linhas = exec_resultado
            ok = len(linhas) == 0
            checks.append((ok, "SQL executou e retornou 0 linhas (CLI mostrará aviso)" if ok else f"SQL retornou {len(linhas)} linhas para ano fora do escopo"))
        else:
            checks.append((False, f"Comportamento inesperado: {sql_resultado[:80]}"))
        return checks

    # Aceita NAO_SEI ou ValueError (modelo retornou texto não-SQL)
    if teste.get("esperado_nao_sei_ou_invalido"):
        ok = sql_resultado == "__NAO_SEI__" or sql_resultado.startswith("__ERRO__")
        checks.append((ok, "NAO_SEI ou saída inválida (ambos tratados)" if ok else f"Modelo gerou SQL para pergunta fora do escopo: {sql_resultado[:80]}"))
        return checks

    # Aceita NAO_SEI, erro, ou SQL sem referência a tabelas do schema
    if teste.get("esperado_nao_sei_ou_sem_schema"):
        if sql_resultado in ("__NAO_SEI__",) or sql_resultado.startswith("__ERRO__"):
            checks.append((True, "NAO_SEI ou saída inválida"))
        else:
            sql_norm = _normaliza(sql_resultado)
            tabelas = ["PARTIDA", "SELECAO", "CONVOCACAO", "EDICAO_DA_COPA", "JOGADOR", "PAIS", "EVENTO_DE_JOGO", "ESTADIO"]
            usa_schema = any(t in sql_norm for t in tabelas)
            ok = not usa_schema
            checks.append((ok, "SQL trivial sem referência ao schema (aceitável)" if ok else f"Modelo inventou uso do schema: {sql_resultado[:80]}"))
        return checks

    if sql_resultado == "__NAO_SEI__":
        checks.append((False, "Modelo respondeu NAO_SEI quando deveria gerar SQL"))
        return checks

    if sql_resultado.startswith("__ERRO__"):
        checks.append((False, sql_resultado.replace("__ERRO__", "Geração falhou: ")))
        return checks

    sql_norm = _normaliza(sql_resultado)

    for sub in teste.get("deve_conter", []):
        ok = sub.upper() in sql_norm
        checks.append((ok, f"SQL contém '{sub}'" if ok else f"SQL deveria conter '{sub}'"))

    for sub in teste.get("nao_deve_conter", []):
        ok = sub.upper() not in sql_norm
        checks.append((ok, f"SQL não contém '{sub.strip()}'" if ok else f"SQL não deveria conter '{sub.strip()}'"))

    if teste.get("executa_sem_erro", True):
        if exec_resultado is None:
            checks.append((False, "SQL não foi executado"))
            return checks
        if isinstance(exec_resultado, Exception):
            checks.append((False, f"Erro de execução: {exec_resultado}"))
            return checks
        checks.append((True, "Executa sem erro"))

        _cols, linhas = exec_resultado
        n = len(linhas)
        if "linhas_min" in teste:
            ok = n >= teste["linhas_min"]
            checks.append((ok, f"{n} linhas >= {teste['linhas_min']}" if ok else f"Esperava ≥ {teste['linhas_min']} linhas, recebeu {n}"))
        if "linhas_max" in teste:
            ok = n <= teste["linhas_max"]
            checks.append((ok, f"{n} linhas <= {teste['linhas_max']}" if ok else f"Esperava ≤ {teste['linhas_max']} linhas, recebeu {n}"))

    return checks


def main():
    print("=" * 70)
    print(f"  Bateria de testes IA — modelo: {ollama_client.MODELO_PADRAO}")
    print(f"  Ollama: {ollama_client.OLLAMA_HOST}")
    print(f"  Postgres: {USER_DEFAULT}@{HOST_DEFAULT}:{PORT_DEFAULT}/{DB_DEFAULT}")
    print("=" * 70)

    db = Database()
    try:
        db.conectar(HOST_DEFAULT, PORT_DEFAULT, DB_DEFAULT, USER_DEFAULT, PASS_DEFAULT)
    except psycopg2.Error as e:
        print(f"[ERRO] Falha ao conectar no PostgreSQL: {e}")
        sys.exit(2)

    total = len(TESTES)
    passou = 0
    falhou_detalhes = []

    for i, teste in enumerate(TESTES, 1):
        print(f"\n[{i}/{total}] {teste['id']}: {teste['pergunta']}")
        t = time.time()

        sql_resultado = None
        exec_resultado = None
        try:
            sql_resultado = ollama_client.gerar_sql(teste["pergunta"])
        except ollama_client.RespostaNaoSei:
            sql_resultado = "__NAO_SEI__"
        except (ConnectionError, ValueError) as e:
            sql_resultado = f"__ERRO__{type(e).__name__}: {e}"

        if sql_resultado not in ("__NAO_SEI__",) and not sql_resultado.startswith("__ERRO__"):
            try:
                exec_resultado = db.executar_leitura(sql_resultado)
            except psycopg2.Error as e:
                exec_resultado = e

        checks = avaliar(teste, sql_resultado, exec_resultado)
        elapsed = time.time() - t
        ok_total = all(ok for ok, _ in checks)

        if ok_total:
            passou += 1
            print(f"  ✓ ({elapsed:.0f}s) — {len(checks)} checks passaram")
        else:
            print(f"  ✗ ({elapsed:.0f}s)")
            for ok, msg in checks:
                marker = "✓" if ok else "✗"
                print(f"    {marker} {msg}")
            if sql_resultado not in ("__NAO_SEI__",) and not sql_resultado.startswith("__ERRO__"):
                falhou_detalhes.append((teste["id"], sql_resultado))

    print("\n" + "=" * 70)
    print(f"RESUMO: {passou}/{total} testes passaram")
    print("=" * 70)

    if falhou_detalhes:
        print("\nSQL gerado em testes que falharam:")
        for tid, sql in falhou_detalhes:
            print(f"\n--- {tid} ---")
            print(sql)

    db.fechar()
    sys.exit(0 if passou == total else 1)


if __name__ == "__main__":
    main()
