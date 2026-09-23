#!/usr/bin/env bash
set -euo pipefail

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

echo "Pipeline completado con éxito."