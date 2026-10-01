from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
import random

from dotenv import dotenv_values, set_key, load_dotenv

load_dotenv()




def set_api_keys():
    ENV_FILE = Path(__file__).resolve().parent / ".env"
    RESOURCE_GROUP_VAR = "RESOURCE_GROUP_NAME"
    SEARCH_SERVICE_VAR = "AZURE_SEARCH_SERVICE_NAME"
    ADMIN_KEY_VAR = "AZURE_SEARCH_ADMIN_KEY"
    result = subprocess.run(
        "az storage account keys list --account-name " + os.getenv("AZURE_STORAGE_ACCOUNT_NAME")+ 
        " --resource-group " + os.getenv("RESOURCE_GROUP_NAME") + 
        " --query \"[0].value\"",
        shell=True,
        capture_output=True,
        text=True
    )
    
    print("storage key: " + result.stdout)
    primary_key = result.stdout.strip()
    set_key(str(ENV_FILE), "AZURE_STORAGE_API_KEY", primary_key, quote_mode="never")

    result = subprocess.run(
        "az search admin-key show \
        --resource-group " + os.getenv("RESOURCE_GROUP_NAME") + " \
        --service-name " + os.getenv("AZURE_SEARCH_SERVICE_NAME") + " \
        --query primaryKey \
        --output tsv",
        shell=True,
        capture_output=True,
        text=True
    )
    
    print("search admin key: " + result.stdout)
    admin_key = result.stdout.strip()
    set_key(str(ENV_FILE), "AZURE_SEARCH_ADMIN_KEY", admin_key, quote_mode="never")


    result = subprocess.run(
        "az cognitiveservices account keys list \
        -n " + os.getenv("AZURE_OPENAI_ACCOUNT_NAME") + " \
        -g " + os.getenv("RESOURCE_GROUP_NAME") + " \
        --query key1 \
        -o tsv",
        shell=True,
        capture_output=True,
        text=True
    )

    print("openai key: " + result.stdout)
    openai_key = result.stdout.strip()
    set_key(str(ENV_FILE), "AZURE_OPENAI_API_KEY", openai_key, quote_mode="never")


def set_resource_names():
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
    resultado = "".join(random.choice(letras) for _ in range(2))

    ENV_FILE = Path(__file__).resolve().parent / ".env"


    set_key(str(ENV_FILE), "AZURE_STORAGE_ACCOUNT_NAME", "stnormatransitox" + resultado, quote_mode="never")
    set_key(str(ENV_FILE), "AZURE_OPENAI_ACCOUNT_NAME", "oai-transitocolx" + resultado, quote_mode="never")
    set_key(str(ENV_FILE), "AZURE_OPENAI_ENDPOINT", "https://oai-transitocolx" + resultado + ".openai.azure.com/", quote_mode="never")
    set_key(str(ENV_FILE), "AZURE_SEARCH_SERVICE_NAME", "search-movilidad-colx" + resultado, quote_mode="never")

def test_remote_endpoint():
    result = subprocess.run(
        "curl -X POST \"https://app-transito-api.azurewebsites.net/chat\"   -H \"Content-Type: application/json\"   -H \"X-App-Api-Key: "+os.getenv("APP_API_KEY")+"\"   -d '{"
        "\"pregunta\": \"¿Cuál es la sanción por no usar cinturón de seguridad?\","
        "\"chat_id\": \"test-chat-001\""
        "}'",
        shell=True,
        capture_output=True,
        text=True
    )
    print("remote endpoint: " + result.stdout)

def test_local_endpoint():
    result = subprocess.run(
        "curl -X POST \"http://localhost:8000/chat\"   -H \"Content-Type: application/json\"   -H \"X-App-Api-Key: "+os.getenv("APP_API_KEY")+"\"   -d '{"
        "\"pregunta\": \"¿Cuál es la sanción por no usar cinturón de seguridad?\","
        "\"chat_id\": \"test-chat-001\""
        "}'",
        shell=True,
        capture_output=True,
        text=True
    )
    print("local endpoint: " + result.stdout)

def main() -> None:

    opcion = int(input('''Introduce un número: 
    1. Establecer nombres de recursos
    2. Configurar claves API
    3. Probar endpoint remoto
    4. Probar endpoint local
'''))
    if opcion == 1:
        set_resource_names()
    elif opcion == 2:
        set_api_keys()
    elif opcion == 3:
        test_remote_endpoint()
    elif opcion == 4:
        test_local_endpoint()
    


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)