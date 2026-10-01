import os

import pulumi
from dotenv import load_dotenv
from pulumi_azure_native import resources, cognitiveservices, search, web, storage, containerregistry
import pulumi_azure_native as azure_native

load_dotenv()


RESOURCE_GROUP_NAME = os.getenv("RESOURCE_GROUP_NAME")
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AI_ACCOUNT_NAME = os.getenv("AZURE_OPENAI_ACCOUNT_NAME")
SEARCH_SERVICE_NAME = os.getenv("AZURE_SEARCH_SERVICE_NAME")
FUNCTION_APP_NAME = os.getenv("AZURE_FUNCTION_APP_NAME", "func-transito-ingesta")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_OPENAI_EMBEDDING_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_APP_BACKEND_URL = os.getenv("AZURE_APP_BACKEND_URL")
APP_API_KEY = os.getenv("APP_API_KEY")
AZURE_ACR_NAME = os.getenv("AZURE_ACR_NAME")

# 1. Grupo de Recursos
resource_group = resources.ResourceGroup("tfm-rag-rg",
    resource_group_name=RESOURCE_GROUP_NAME
)

# 2. Azure Blob Storage (Para almacenamiento de PDFs normativos)
storage_account = storage.StorageAccount("sttransito",
    resource_group_name=resource_group.name,
    account_name=STORAGE_ACCOUNT_NAME,
    sku=storage.SkuArgs(name=storage.SkuName.STANDARD_LRS),
    kind=storage.Kind.STORAGE_V2,
)

blob_container = storage.BlobContainer("docs-container",
    resource_group_name=resource_group.name,
    account_name=storage_account.name,
    container_name=AZURE_STORAGE_CONTAINER_NAME
)

storage_keys = storage.list_storage_account_keys_output(
    resource_group_name=resource_group.name,
    account_name=storage_account.name,
)
storage_connection_string = pulumi.Output.all(
    account_name=storage_account.name,
    keys=storage_keys,
).apply(
    lambda values: (
        "DefaultEndpointsProtocol=https;"
        f"AccountName={values['account_name']};"
        f"AccountKey={values['keys'].keys[0].value};"
        "EndpointSuffix=core.windows.net"
    )
)

# 3. Azure OpenAI Service (Sube tus modelos de Chat y Embeddings)
openai_account = cognitiveservices.Account("openai-account",
    resource_group_name=resource_group.name,
    account_name=AI_ACCOUNT_NAME,
    kind="OpenAI",
    sku=cognitiveservices.SkuArgs(name="S0"),
    properties=cognitiveservices.AccountPropertiesArgs(
        custom_sub_domain_name=AI_ACCOUNT_NAME
    )
)

# Deploy del Modelo de Embeddings (text-embedding-3-small)
embedding_deployment = cognitiveservices.Deployment("embedding-deployment",
    resource_group_name=resource_group.name,
    account_name=openai_account.name,
    deployment_name=AZURE_OPENAI_EMBEDDING_NAME,
    properties=cognitiveservices.DeploymentPropertiesArgs(
        model=cognitiveservices.DeploymentModelArgs(
            format="OpenAI",
            name="text-embedding-3-small",
        )
    ),
    sku=cognitiveservices.SkuArgs(
        name="Standard",
        capacity=5,
    )
)

# Deploy del Modelo Generativo (GPT-4o o GPT-3.5-Turbo)
gpt_deployment = cognitiveservices.Deployment("gpt-deployment",
    resource_group_name=resource_group.name,
    account_name=openai_account.name,
    deployment_name="gpt-4o",
    properties=cognitiveservices.DeploymentPropertiesArgs(
        model=cognitiveservices.DeploymentModelArgs(
            format="OpenAI",
            name="gpt-4o", # o gpt-3.5-turbo
            version="2024-11-20"
            #version="latest"
        )
    ),
    sku=cognitiveservices.SkuArgs(
        name="Standard",
        capacity=5,
    )
)

# 4. Azure AI Search (Soporta Búsqueda Híbrida y Vectorial)
search_service = search.Service("search-service",
    resource_group_name=resource_group.name,
    search_service_name=SEARCH_SERVICE_NAME,
    sku=search.SkuArgs(name="basic"), # Sku básico soporta búsqueda vectorial
    replica_count=1,
    partition_count=1
)

# 5. Azure App Service Plan + Web App (Hosting para Backend FastAPI)
app_service_plan = web.AppServicePlan("asp-backend",
    resource_group_name=resource_group.name,
    name="asp-transito-backend",
    sku=web.SkuDescriptionArgs(
        name="B1",
        tier="Basic"
    ),
    kind="linux",
    reserved=True # Requerido para contenedores Linux/Python
)

backend_app = web.WebApp("app-backend-fastapi",
    resource_group_name=resource_group.name,
    name=AZURE_APP_BACKEND_URL,
    server_farm_id=app_service_plan.id,
    site_config=web.SiteConfigArgs(
        linux_fx_version="PYTHON|3.12", # Entorno Python para FastAPI
        always_on=True,
        # Instala requirements.txt durante el despliegue y arranca con gunicorn+uvicorn
        # app_command_line=(
        #     "gunicorn -w 2 -k uvicorn.workers.UvicornWorker "
        #     "--timeout 600 --bind 0.0.0.0:8000 main:app"
        # ),
        # app_settings=[
        #     #web.NameValuePairArgs(name="SCM_DO_BUILD_DURING_DEPLOYMENT", value="true"),
        #     web.NameValuePairArgs(name="AZURE_OPENAI_ACCOUNT_NAME", value=AI_ACCOUNT_NAME),
        #     web.NameValuePairArgs(name="AZURE_OPENAI_API_KEY", value=AZURE_OPENAI_API_KEY),
        #     web.NameValuePairArgs(name="AZURE_OPENAI_EMBEDDING_NAME", value=AZURE_OPENAI_EMBEDDING_NAME),
        #     web.NameValuePairArgs(name="AZURE_SEARCH_SERVICE_NAME", value=SEARCH_SERVICE_NAME),
        #     web.NameValuePairArgs(name="AZURE_SEARCH_ADMIN_KEY", value=AZURE_SEARCH_ADMIN_KEY),
        #     web.NameValuePairArgs(name="AZURE_SEARCH_INDEX", value="normativa-transito-index"),
        #     web.NameValuePairArgs(name="APP_API_KEY", value=APP_API_KEY),
        # ]
    )
)

# 6. Azure Container Registry (ACR) para alojar las imágenes Docker del backend
acr = containerregistry.Registry("acr-transito",
    resource_group_name=resource_group.name,
    registry_name=AZURE_ACR_NAME,  # Debe ser un nombre único globalmente (solo letras y números)
    sku=containerregistry.SkuArgs(
        name=containerregistry.SkuName.BASIC,
    ),
    admin_user_enabled=True,  # Habilita el usuario administrador para facilitar la autenticación
)



# Exportar variables críticas para el archivo .env del backend FastAPI
pulumi.export("openai_endpoint", openai_account.properties.endpoint)
pulumi.export("search_service_name", search_service.name)
pulumi.export("backend_url", backend_app.default_host_name)
pulumi.export("acr_login_server", acr.login_server)