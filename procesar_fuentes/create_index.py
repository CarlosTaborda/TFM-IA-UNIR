import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    LexicalAnalyzerName,
)

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES
# ==========================================
load_dotenv()
endpoint = "https://"+os.getenv("AZURE_SEARCH_SERVICE_NAME")+".search.windows.net"  # Reemplaza con tu endpoint de Azure AI Search
admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")  # Reemplaza con tu admin key de Azure AI Search
index_name = "normativa-transito-index"

def crear_indice_vectorial():
    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(admin_key))

    # 1. Definición de campos mínimos requeridos
    fields = [
        SearchableField(
            name="chunk_id",
            key=True,
            filterable=True,
            sortable=True,
            analyzer_name=LexicalAnalyzerName.KEYWORD,
        ),
        SimpleField(name="parent_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String, searchable=True, retrievable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # Coincide con text-embedding-3-small (1536 dimensiones)
            vector_search_profile_name="mi-perfil-vectorial"
        ),
        SearchableField(name="title", type=SearchFieldDataType.String, filterable=True, retrievable=True),
        SimpleField(name="source_path", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
        SearchableField(name="section_title", type=SearchFieldDataType.String, filterable=True, retrievable=True),
        SimpleField(name="metadata_storage_last_modified", type=SearchFieldDataType.DateTimeOffset, filterable=True)
    ]

    # 2. Configuración del perfil de búsqueda vectorial (Vector Search Profile)
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="mi-perfil-vectorial",
                algorithm_configuration_name="mi-algoritmo-hnsw"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="mi-algoritmo-hnsw"
            )
        ]
    )

    # 3. Construcción del objeto de índice
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search
    )

    # 4. Crear o actualizar el índice en Azure
    client.create_or_update_index(index)
    print(f"¡Índice '{index_name}' creado correctamente en Azure AI Search con los campos especificados!")

if __name__ == "__main__":
    crear_indice_vectorial()