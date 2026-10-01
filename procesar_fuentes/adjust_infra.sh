#!/usr/bin/env bash
set -euo pipefail
set -x

# Ejecuta el pipeline de Azure AI Search en el orden correcto de dependencias.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-python3}"

scripts=(
    "create_datasource.py"
    "create_index.py"
    "create_splitskill.py"
    "create_indexer.py"
)

for script in "${scripts[@]}"; do
    echo "==> Ejecutando $script"
    "$PYTHON" "$script"
    echo
done

cd ..
source .env

az webapp config appsettings set \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$AZURE_APP_BACKEND_URL" \
  --settings \
    AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
    AZURE_SEARCH_ADMIN_KEY="$AZURE_SEARCH_ADMIN_KEY" \
    AZURE_SEARCH_SERVICE_NAME="$AZURE_SEARCH_SERVICE_NAME" \
    AZURE_OPENAI_EMBEDDING_NAME="$AZURE_OPENAI_EMBEDDING_NAME" \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_ACCOUNT_NAME="$AZURE_OPENAI_ACCOUNT_NAME" \
    APP_API_KEY="$APP_API_KEY"

az acr build --registry "$AZURE_ACR_NAME" --image rag-backend:latest ./rag_backend

sleep 10

az webapp config container set \
  --name "$AZURE_APP_BACKEND_URL" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --docker-custom-image-name "$AZURE_ACR_NAME.azurecr.io/rag-backend:latest" \
  --docker-registry-server-url "https://$AZURE_ACR_NAME.azurecr.io"




az webapp restart --name "$AZURE_APP_BACKEND_URL" --resource-group "$RESOURCE_GROUP_NAME"




echo "Pipeline completado con éxito."