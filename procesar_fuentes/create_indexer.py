import os
import time
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from datetime import timedelta
from azure.search.documents.indexes.models import (
    SearchIndexer,
    IndexingParameters,
    IndexingParametersConfiguration,
    BlobIndexerDataToExtract,
    BlobIndexerParsingMode,
    FieldMapping,
    IndexingSchedule,
)
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES Y NOMBRES
# ==========================================
endpoint = "https://" + os.getenv("AZURE_SEARCH_SERVICE_NAME") + ".search.windows.net"
admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")

indexer_name = "normativa-transito-indexer"
data_source_name = "normativa-transito-blob-ds"
index_name = "normativa-transito-index"
skillset_name = "normativa-transito-skillset"

def crear_y_ejecutar_indexer():
    client = SearchIndexerClient(endpoint=endpoint, credential=AzureKeyCredential(admin_key))

    # 1. Configuración de parámetros de extracción
    parameters = IndexingParameters(
        configuration=IndexingParametersConfiguration(
            data_to_extract=BlobIndexerDataToExtract.CONTENT_AND_METADATA,
            parsing_mode=BlobIndexerParsingMode.DEFAULT,
        )
    )

    # 2. Mapeos de campos directos (origen -> destino)
    field_mappings = [
        FieldMapping(
            source_field_name="metadata_storage_name",
            target_field_name="title"
        )
    ]

    # 3. Definición del Indexer
    # Al no definir 'schedule', el indexador queda configurado para ejecución bajo demanda
    indexer = SearchIndexer(
        name=indexer_name,
        description="Indexador bajo demanda para PDFs de normativa de tránsito",
        data_source_name=data_source_name,
        target_index_name=index_name,
        skillset_name=skillset_name,
        parameters=parameters,
        field_mappings=field_mappings,
        schedule=IndexingSchedule(interval=timedelta(minutes=60)),
    )

    # 4. Crear o actualizar el indexador en Azure
    client.create_or_update_indexer(indexer)
    print(f"¡Indexer '{indexer_name}' creado o actualizado con éxito!")

    # 5. Ejecutar la indexación bajo demanda
    print(f"Iniciando ejecución del indexer '{indexer_name}'...")
    client.run_indexer(indexer_name)

    # 6. Monitorear el estado de la ejecución
    time.sleep(3)
    status = client.get_indexer_status(indexer_name)
    print(f"Estado general del indexer: {status.status}")
    if status.last_result:
        print(f"Último resultado: {status.last_result.status} | Documentos procesados: {status.last_result.item_count}")

if __name__ == "__main__":
    crear_y_ejecutar_indexer()