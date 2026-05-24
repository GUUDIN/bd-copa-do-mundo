#!/bin/bash
# =============================================================================
# Cria o repositório no GitHub e faz o push inicial
# Execute UMA VEZ após clonar/copiar este repositório.
# =============================================================================
set -e

REPO_NAME="bd-copa-do-mundo"

echo "🔐 Fazendo login no GitHub (siga as instruções abaixo)..."
gh auth login

echo ""
echo "📦 Criando repositório '$REPO_NAME' no GitHub..."
gh repo create "$REPO_NAME" \
    --public \
    --description "SCC0640 – Sistema de Copas do Mundo FIFA (USP/ICMC)" \
    --source=. \
    --remote=origin \
    --push

echo ""
echo "✅ Pronto! Repositório criado e código enviado."
echo "   👉 Acesse: $(gh repo view --json url -q .url)"
echo ""
echo "📝 Próximos passos:"
echo "   1. Atualize os nomes do grupo no README.md e 08.Instrucoes.txt"
echo "   2. Adicione o código do protótipo na pasta prototipo/"
echo "   3. Preencha o 06.DML.sql com os dados reais"
echo "   4. Faça git push para acionar o CI (export dos diagramas para SVG)"
