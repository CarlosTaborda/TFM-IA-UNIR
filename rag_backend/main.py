import os
import secrets
from threading import Lock

import logging
import sys

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
    force=True,
)

logger = logging.getLogger(__name__)



# Cargar variables de entorno generadas por claves.py
load_dotenv()

# La API solo debe ser consumida por la app móvil oficial, nunca directamente
# desde un navegador u otro cliente. Se exige una API key compartida enviada
# en el header X-App-Api-Key y se deshabilita la documentación pública.
APP_API_KEY = os.getenv("app-api-key") or os.getenv("APP_API_KEY")
_is_prod = bool(APP_API_KEY)

app = FastAPI(
    title="API RAG - Normativa de Tránsito Colombia",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

api_key_header = APIKeyHeader(name="X-App-Api-Key", auto_error=False)


async def verify_app_api_key(api_key: str = Security(api_key_header)) -> None:
    """Solo permite el paso de peticiones autenticadas con la clave de la app."""
    if not APP_API_KEY:
        # Si no se configuró la clave (p.ej. entorno local), no se bloquea.
        return
    if not api_key or not secrets.compare_digest(api_key, APP_API_KEY):
        raise HTTPException(status_code=401, detail="No autorizado")

# Configuración de variables (exportadas desde Pulumi y configuradas en .env)
AZURE_SEARCH_ENDPOINT = "https://" + ( os.getenv("azure-search-service-name") or os.getenv("AZURE_SEARCH_SERVICE_NAME") ) + ".search.windows.net"
AZURE_OPENAI_API_KEY = os.getenv("azure-openai-api-key") or os.getenv("AZURE_OPENAI_API_KEY")
AZURE_SEARCH_KEY = os.getenv("azure-search-admin-key") or os.getenv("AZURE_SEARCH_ADMIN_KEY")
INDEX_NAME = os.getenv("azure-search-index") or os.getenv("AZURE_SEARCH_INDEX", "normativa-transito-index")
AZURE_OPENAI_EMBEDDING_NAME =  os.getenv("azure-openai-embedding-name") or os.getenv("AZURE_OPENAI_EMBEDDING_NAME")
AZURE_OPENAI_ENDPOINT = "https://" + ( os.getenv("azure-openai-account-name") or os.getenv("AZURE_OPENAI_ACCOUNT_NAME") ) + ".openai.azure.com/"

logger.debug("AZURE_SEARCH_ENDPOINT: %s", AZURE_SEARCH_ENDPOINT)
logger.debug("AZURE_OPENAI_API_KEY: %s", AZURE_OPENAI_API_KEY)
logger.debug("AZURE_SEARCH_KEY: %s", AZURE_SEARCH_KEY)
logger.debug("INDEX_NAME: %s", INDEX_NAME)
logger.debug("AZURE_OPENAI_EMBEDDING_NAME: %s", AZURE_OPENAI_EMBEDDING_NAME)
logger.debug("AZURE_OPENAI_ENDPOINT: %s", AZURE_OPENAI_ENDPOINT)
logger.debug("APP_API_KEY: %s", APP_API_KEY)

# 1. Inicializar Embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=AZURE_OPENAI_EMBEDDING_NAME,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    openai_api_version="2023-05-15",
)

# 2. Inicializar Conexión a Azure AI Search
vector_store = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=AZURE_SEARCH_KEY,
    index_name=INDEX_NAME,
    embedding_function=embeddings.embed_query,
)

# Configurar el retriever híbrido (texto + vectores)
retriever = vector_store.as_retriever(search_type="hybrid", k=4)

# 3. Inicializar LLM Generativo
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    openai_api_version="2024-12-01-preview",
    temperature=0.1
)

# 4. Definir el Prompt para garantizar trazabilidad, incluyendo el historial
# de la conversación asociado a cada chat_id
system_prompt = (
    "Eres un experto en normativa de tránsito en Colombia. "
    "Responde basándote exclusivamente en el contexto normativo recuperado. "
    "Incluye siempre la referencia normativa visible (artículo, ley o decreto). "
    "Si no encuentras la respuesta en el contexto, indícalo claramente y no inventes información.\n\n"
    "Contexto:\n{context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
])

# 5. Crear las cadenas del pipeline RAG
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 6. Cada chat (identificado por un chat_id único generado por la app) tiene
# su propio historial de mensajes, aislado del resto de conversaciones.
_chat_histories: dict[str, InMemoryChatMessageHistory] = {}
_chat_histories_lock = Lock()


def _get_chat_history(chat_id: str) -> InMemoryChatMessageHistory:
    with _chat_histories_lock:
        if chat_id not in _chat_histories:
            _chat_histories[chat_id] = InMemoryChatMessageHistory()
        return _chat_histories[chat_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    _get_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


# Modelo de datos para recibir la petición
class QueryRequest(BaseModel):
    pregunta: str
    chat_id: str = Field(..., min_length=1, description="Identificador único del chat")


@app.post("/chat", dependencies=[Depends(verify_app_api_key)])
async def chat_endpoint(request: QueryRequest):
    try:
        # Invocar la cadena RAG con la pregunta del usuario, aislando el
        # historial de conversación por chat_id
        response = conversational_rag_chain.invoke(
            {"input": request.pregunta},
            config={"configurable": {"session_id": request.chat_id}},
        )

        # Extraer metadatos para la trazabilidad normativa
        fuentes = []
        for doc in response["context"]:
            fuentes.append({
                "title": doc.metadata.get("title", "Desconocido"),
                "source_path": doc.metadata.get("source_path", "Desconocido"),
                "page_number": doc.metadata.get("page_number", 0)
            })

        return {
            "respuesta": response["answer"],
            "fuentes": fuentes,
            "chat_id": request.chat_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/{chat_id}", dependencies=[Depends(verify_app_api_key)])
async def delete_chat_history(chat_id: str):
    """Elimina el historial en memoria de un chat (p.ej. al borrarlo en la app)."""
    with _chat_histories_lock:
        _chat_histories.pop(chat_id, None)
    return {"deleted": chat_id}


@app.get("/health")
async def health_check():
    """Endpoint sin autenticación usado por Azure App Service para health checks."""
    return {"status": "ok"}
