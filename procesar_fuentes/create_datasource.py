import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import SearchIndexerDataSourceConnection

# Configuración de credenciales y endpoints
from dotenv import load_dotenv
load_dotenv()

endpoint = "https://"+os.getenv("AZURE_SEARCH_SERVICE_NAME")+".search.windows.net"  # Tu servicio de búsqueda en Azure
admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")  # Tu admin key de Azure Search

# Credenciales de tu Blob Storage (tomadas de la infraestructura generada)
connection_string = "DefaultEndpointsProtocol=https;AccountName="+os.getenv("AZURE_STORAGE_ACCOUNT_NAME")+";AccountKey="+os.getenv("AZURE_STORAGE_API_KEY")+";EndpointSuffix=core.windows.net"
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
data_source_name = "normativa-transito-blob-ds"

def crear_data_source_blob():
    client = SearchIndexerClient(endpoint=endpoint, credential=AzureKeyCredential(admin_key))

    # Definir la conexión al Blob Storage
    data_source = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type="azureblob",
        connection_string=connection_string,
        container={"name": container_name}
    )

    # Crear o actualizar el data source en Azure AI Search
    client.create_or_update_data_source_connection(data_source)
    print(f"¡Data Source '{data_source_name}' creado o actualizado con éxito en Azure AI Search!")

if __name__ == "__main__":
    crear_data_source_blob()