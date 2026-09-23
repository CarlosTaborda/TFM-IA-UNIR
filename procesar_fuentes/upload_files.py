import os
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

STORAGE_ACCOUNT_NAME = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
STORAGE_API_KEY = os.environ["AZURE_STORAGE_API_KEY"]
CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;"
    f"AccountName={STORAGE_ACCOUNT_NAME};"
    f"AccountKey={STORAGE_API_KEY};"
    "EndpointSuffix=core.windows.net"
)
CONTAINER_NAME = os.environ["AZURE_STORAGE_CONTAINER_NAME"]
LOCAL_DOCUMENTS_PATH = Path(__file__).resolve().parents[1] / "corpus"




def main() -> None:
    if not LOCAL_DOCUMENTS_PATH.is_dir():
        raise FileNotFoundError(
            f"No existe la carpeta local: {LOCAL_DOCUMENTS_PATH}"
        )

    service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = service_client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
        print(f"Contenedor creado: {CONTAINER_NAME}")
    except ResourceExistsError:
        print(f"Usando contenedor existente: {CONTAINER_NAME}")

    files = [path for path in LOCAL_DOCUMENTS_PATH.rglob("*") if path.is_file()]

    if not files:
        print(f"No se encontraron archivos en: {LOCAL_DOCUMENTS_PATH}")
        return

    uploaded = 0
    skipped = 0

    for local_file in files:
        # Ejemplo: documents/normativa/ley_769.pdf
        # se guarda como: normativa/ley_769.pdf
        blob_name = local_file.relative_to(LOCAL_DOCUMENTS_PATH).as_posix()

        blob_client = container_client.get_blob_client(blob_name)

        try:
            with local_file.open("rb") as data:
                blob_client.upload_blob(data, overwrite=False)

            uploaded += 1
            print(f"[{uploaded}/{len(files)}] Subido: {blob_name}")

        except ResourceExistsError:
            skipped += 1
            print(f"Omitido, ya existe: {blob_name}")
            continue

    print(f"\nCarga terminada. Archivos subidos: {uploaded}")
    print(
        f"Contenedor: "
        f"https://{service_client.account_name}.blob.core.windows.net/"
        f"{CONTAINER_NAME}"
    )


if __name__ == "__main__":
    main()