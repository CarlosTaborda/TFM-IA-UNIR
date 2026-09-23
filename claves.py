from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values, set_key, load_dotenv

load_dotenv()

ENV_FILE = Path(__file__).resolve().parent / ".env"
RESOURCE_GROUP_VAR = "RESOURCE_GROUP_NAME"
SEARCH_SERVICE_VAR = "AZURE_SEARCH_SERVICE_NAME"
ADMIN_KEY_VAR = "AZURE_SEARCH_ADMIN_KEY"


def main() -> None:

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


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)