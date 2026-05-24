# Protótipo – Sistema de Copas do Mundo

## Requisitos
- Python 3.10+
- PostgreSQL rodando localmente (ou remoto)
- [Ollama](https://ollama.com) instalado e rodando localmente com um modelo carregado
  ```bash
  ollama pull llama3        # ou outro modelo de sua escolha
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
3. Consulta em linguagem natural → SQL (via ollama local)
4. Execução de SQL arbitrário com tratamento de erros
