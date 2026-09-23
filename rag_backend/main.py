import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Cargar variables de entorno generadas por claves.py
load_dotenv()

app = FastAPI(title="API RAG - Normativa de Tránsito Colombia")

# Configuración de variables (exportadas desde Pulumi y configuradas en .env)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "normativa-transito-index")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_NAME")

# 1. Inicializar Embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=EMBEDDING_DEPLOYMENT,
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
retriever = vector_store.as_retriever(search_type="hybrid", search_kwargs={"k": 4})

# 3. Inicializar LLM Generativo
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    openai_api_version="2024-05-13",
    temperature=0.1 # Temperatura baja para respuestas técnicas y precisas
)

# 4. Definir el Prompt para garantizar trazabilidad
system_prompt = (
    "Eres un experto en normativa de tránsito en Colombia. "
    "Responde basándote exclusivamente en el contexto normativo recuperado. "
    "Incluye siempre la referencia normativa visible (artículo, ley o decreto). "
    "Si no encuentras la respuesta en el contexto, indícalo claramente y no inventes información.\n\n"
    "Contexto:\n{context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 5. Crear las cadenas del pipeline RAG
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Modelo de datos para recibir la petición
class QueryRequest(BaseModel):
    pregunta: str

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        # Invocar la cadena RAG con la pregunta del usuario
        response = rag_chain.invoke({"input": request.pregunta})
        
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
            "fuentes": fuentes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))