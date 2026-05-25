# Protótipo – Sistema de Copas do Mundo

## Requisitos
- Python 3.10+
- PostgreSQL rodando localmente (ou remoto)
- [Ollama](https://ollama.com) instalado e rodando localmente com um modelo carregado
  ```bash
  ollama pull qwen2.5-coder:3b
  ollama serve              # deixe rodando em background
  ```

## Instalação
```bash
pip install psycopg2-binary requests
```

## Execução
```bash
python main.py
```

O programa pedirá os parâmetros de conexão ao PostgreSQL (host, porta, banco, usuário, senha)
e apresentará um menu com as 10 consultas disponíveis + opção de consulta em linguagem natural via ollama.

## Funcionalidades
1. Login interativo no banco
2. Menu com as 10 consultas do projeto
3. Consulta em linguagem natural → SQL (via ollama local, modelo qwen2.5-coder:3b)
4. Execução de SQL arbitrário com tratamento de erros

## Camada IA (NL → SQL)

A IA segue três camadas para gerar SQL:

1. **System prompt fixo** ([ollama_client.py](ollama_client.py)): regras críticas
   sempre presentes (escopo temporal 1998-2022, padrões UNION ALL para estatísticas
   por seleção, tratamento de empates com CTE de MAX, etc.).
2. **Schema real** do banco injetado no prompt.
3. **Recuperação lexical** de padrões canônicos e perguntas de treino relevantes
   a partir de [IA_TREINAMENTO.md](IA_TREINAMENTO.md). Em cada chamada, só os 1-2
   padrões mais parecidos com a pergunta entram no prompt (mantém latência baixa).

Antes de executar o SQL, o protótipo:
- Valida com `EXPLAIN` (read-only) — se falhar, pede correção à IA (até 3×).
- Exibe o SQL formatado e pede confirmação.
- Executa em transação `READ ONLY` com `statement_timeout = 15s`.
- Mostra aviso do escopo temporal abaixo do resultado.

## Testes da camada IA

```bash
cd prototipo
python -m tests.test_ia
```

12 testes comportamentais que checam propriedades do SQL gerado (contém
`UNION ALL`, não usa `LIMIT 1` em perguntas de máximo, usa a tabela certa,
executa sem erro, etc.) — sem comparar SQL exato. Útil quando trocar o modelo
ou ajustar o prompt.
