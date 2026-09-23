import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerSkillset,
    SplitSkill,
    SplitSkillLanguage,
    AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
)
from dotenv import load_dotenv
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES Y ENDPOINTS
# ==========================================
endpoint = "https://" + os.getenv("AZURE_SEARCH_SERVICE_NAME") + ".search.windows.net"  # Tu endpoint de Azure AI Search
admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")

skillset_name = "normativa-transito-skillset"
index_name = "normativa-transito-index"

# Configuración de Azure OpenAI (para el skillset de embeddings)
openai_resource_uri = "https://" + os.getenv("AZURE_OPENAI_ACCOUNT_NAME") + ".openai.azure.com"
openai_deployment_id = os.getenv("AZURE_OPENAI_EMBEDDING_NAME")  # Ej: text-embedding-3-small
openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

def crear_skillset_vectorial():
    client = SearchIndexerClient(endpoint=endpoint, credential=AzureKeyCredential(admin_key))

    # 1. Definición del SplitSkill (Fragmentación del texto)
    split_skill = SplitSkill(
        name="#split-content",
        description="Divide el texto extraído en chunks",
        context="/document",
        text_split_mode="pages",
        maximum_page_length=1500,
        page_overlap_length=200,
        default_language_code=SplitSkillLanguage.ES,  # Opcional pero recomendado para español
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/content")
        ],
        outputs=[
            OutputFieldMappingEntry(name="textItems", target_name="pages")
        ]
    )

    # 2. Definición del AzureOpenAIEmbeddingSkill (Vectorización automática)
    embedding_skill = AzureOpenAIEmbeddingSkill(
        name="#embed-chunks",
        description="Genera vectores de los chunks mediante Azure OpenAI",
        context="/document/pages/*",
        resource_url=openai_resource_uri,
        deployment_name=openai_deployment_id,
        api_key=openai_api_key,
        model_name="text-embedding-3-small",
        dimensions=1536,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*")
        ],
        outputs=[
            OutputFieldMappingEntry(name="embedding", target_name="content_vector")
        ]
    )

    # 3. Configuración de Index Projections (Proyecciones al Índice)
    index_projections = SearchIndexerIndexProjection(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=index_name,
                parent_key_field_name="parent_id",
                source_context="/document/pages/*",
                mappings=[
                    InputFieldMappingEntry(name="content", source="/document/pages/*"),
                    InputFieldMappingEntry(name="content_vector", source="/document/pages/*/content_vector"),
                    InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),
                    InputFieldMappingEntry(name="source_path", source="/document/metadata_storage_path"),
                ],
            )
        ],
        parameters=SearchIndexerIndexProjectionsParameters(
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
        ),
    )

    # 4. Construcción y registro del Skillset en Azure AI Search
    skillset = SearchIndexerSkillset(
        name=skillset_name,
        description="Extrae, fragmenta y vectoriza PDFs de normativa de tránsito",
        skills=[split_skill, embedding_skill],
        index_projection=index_projections,
    )

    client.create_or_update_skillset(skillset)
    print(f"¡Skillset '{skillset_name}' creado o actualizado con éxito en Azure AI Search!")

if __name__ == "__main__":
    crear_skillset_vectorial()