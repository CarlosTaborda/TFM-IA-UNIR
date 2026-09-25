# RAG para normativa de tránsito de Colombia

Este proyecto implementa una solución tipo RAG (Retrieval-Augmented Generation) para consultar y responder preguntas sobre normativa de tránsito en Colombia usando Azure AI Search + Azure OpenAI.

La idea principal es permitir que un usuario haga preguntas en lenguaje natural sobre normas, decretos, resoluciones, artículos o conceptos del tránsito colombiano y recibir respuestas basadas en documentos reales indexados, con referencias y trazabilidad a las fuentes originales.

## ¿Para qué sirve este proyecto?

El proyecto está orientado a:

- Buscar y recuperar fragmentos de normativa legal desde archivos PDF.
- Vectorizar esos contenidos con embeddings de Azure OpenAI.
- Indexarlos en Azure AI Search para recuperación híbrida (texto + vector).
- Responder preguntas sobre tránsito colombiano con contexto recuperado.
- Mantener la trazabilidad a la fuente documental para poder verificar la respuesta.

Este tipo de sistema resulta útil para:

- Consultas rápidas de normativa.
- Búsqueda documental especializada en regulación de tránsito.
- Asistencia para analistas, abogados o personal de movilidad.
- Construcción de un backend RAG que pueda integrarse con una aplicación web o chatbot.

---

## Arquitectura general

El flujo del proyecto es el siguiente:

1. Los PDFs de normativa se almacenan en Azure Blob Storage.
2. Un data source y un indexer de Azure AI Search leen esos archivos.
3. Un skillset divide el documento en chunks y genera embeddings con Azure OpenAI.
4. El índice vectorial almacena el contenido y sus metadatos.
5. El backend FastAPI consulta el índice para recuperar contexto relevante.
6. El modelo generativo responde la pregunta usando ese contexto.

---

## Estructura del proyecto

### [claves.py](claves.py)

Script auxiliar para gestionar variables y credenciales del entorno.

Funciona para:

- crear o actualizar nombres de recursos en Azure,
- obtener claves de Azure Storage, Azure AI Search y Azure OpenAI,
- escribirlas en el archivo .env del proyecto.

Es útil para automatizar la configuración inicial del entorno.


### [requirements.txt](requirements.txt)

Dependencias del proyecto Python principal, incluyendo:

- FastAPI
- Azure SDK
- Pulumi
- LangChain
- OpenAI
- Azure Search
- Azure Storage
- pydantic y demás librerías del backend y la ingesta

### [infraestructure](infraestructure)

Contiene la infraestructura como código con Pulumi para provisionar los recursos de Azure.

Archivos principales:

- [infraestructure/__main__.py](infraestructure/__main__.py): define la creación del Resource Group, Storage Account, Azure OpenAI, Azure AI Search y el backend web.
- [infraestructure/Pulumi.yaml](infraestructure/Pulumi.yaml): configuración del proyecto Pulumi.
- [infraestructure/Pulumi.dev.yaml](infraestructure/Pulumi.dev.yaml): configuración del stack de desarrollo.
- [infraestructure/requirements.txt](infraestructure/requirements.txt): dependencias de Pulumi.
- [infraestructure/README.md](infraestructure/README.md): documentación base del template de infraestructura.

### [procesar_fuentes](procesar_fuentes)

Carpeta encargada de la ingesta y preparación del corpus documental.

Incluye los scripts:

- [procesar_fuentes/upload_files.py](procesar_fuentes/upload_files.py): sube los PDF al contenedor de Blob Storage.
- [procesar_fuentes/create_datasource.py](procesar_fuentes/create_datasource.py): crea el data source de Azure AI Search.
- [procesar_fuentes/create_index.py](procesar_fuentes/create_index.py): crea el índice vectorial y los campos necesarios.
- [procesar_fuentes/create_splitskill.py](procesar_fuentes/create_splitskill.py): crea el skillset para fragmentar y vectorizar chunks.
- [procesar_fuentes/create_indexer.py](procesar_fuentes/create_indexer.py): crea y ejecuta el indexer para procesar documentos.
- [procesar_fuentes/adjust_infra.sh](procesar_fuentes/adjust_infra.sh): ejecuta el pipeline en orden.

### [corpus](corpus)

Carpeta donde se guardan los documentos fuente, normalmente PDFs legales o normativos de tránsito.

Es el origen de los datos que luego se cargan a Azure Blob Storage y se indexan.

### [rag_backend](rag_backend)

Contiene el backend de la aplicación RAG.

Archivo principal:

- [rag_backend/main.py](rag_backend/main.py): define la API FastAPI con el endpoint /chat para responder preguntas con recuperación semántica y generación con OpenAI.

---

## Variables de entorno

El proyecto usa un archivo .env con las credenciales y nombres de recursos de Azure. Algunas de las variables clave son:

- RESOURCE_GROUP_NAME
- AZURE_STORAGE_ACCOUNT_NAME
- AZURE_STORAGE_API_KEY
- AZURE_STORAGE_CONTAINER_NAME
- AZURE_SEARCH_SERVICE_NAME
- AZURE_SEARCH_ADMIN_KEY
- AZURE_SEARCH_INDEX
- AZURE_OPENAI_ACCOUNT_NAME
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_EMBEDDING_NAME

Estas se generan normalmente con [claves.py](claves.py) y se utilizan por la infraestructura, los scripts de indexación y el backend.

---

## Requisitos previos

Antes de desplegar el proyecto necesitas:

- Una suscripción de Azure activa.
- Azure CLI instalado y autenticado con az login.
- Python 3.10+ recomendado.
- Pulumi instalado.
- Acceso a Azure OpenAI y Azure AI Search.
- Documentos PDF de normativa en la carpeta [corpus](corpus).

---

## Cómo desplegar el proyecto

### 1. Preparar el entorno

Desde la raíz del proyecto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si necesitas generar o actualizar credenciales de Azure:

```bash
python claves.py
```

Selecciona la opción correspondiente para:

- crear nombres de recursos,
- configurar claves de Azure y guardarlas en .env.

### 2. Desplegar la infraestructura en Azure

Entra a la carpeta [infraestructure](infraestructure):

```bash
cd infraestructure
pip install -r requirements.txt
pulumi up
```

Esto creará los recursos principales de Azure:

- Resource Group
- Storage Account
- Blob Container
- Azure OpenAI
- Azure AI Search
- Web App de backend

### 3. Subir documentos al almacenamiento

Desde la raíz:

```bash
python procesar_fuentes/upload_files.py
```

Esto sube los PDFs de la carpeta [corpus](corpus) al contenedor configurado en Azure Blob Storage.

### 4. Crear data source, índice y skillset

Ejecuta el pipeline de indexación:

```bash
python procesar_fuentes/adjust_infra.sh
```

O bien en orden manual:

```bash
python procesar_fuentes/create_datasource.py
python procesar_fuentes/create_index.py
python procesar_fuentes/create_splitskill.py
python procesar_fuentes/create_indexer.py
```

Esto crea:

- un data source de Blob,
- un índice vectorial,
- un skillset para fragmentación y embeddings,
- un indexer para procesar los archivos.

### 5. Ejecutar el backend RAG

```bash
uvicorn rag_backend.main:app --host 0.0.0.0 --port 8000 --reload
```

La API queda disponible en:

- http://localhost:8000/docs

Endpoint principal:

- POST /chat

Ejemplo de payload:

```json
{
  "pregunta": "¿Qué establece la normativa sobre velocidad máxima en zona urbana?"
}
```

---

## Flujo de uso típico

1. Se crea la infraestructura Azure.
2. Se suben los PDFs de normativa al blob.
3. El indexer los procesa y genera embeddings.
4. El servicio RAG consulta el índice con la pregunta del usuario.
5. El modelo combina la respuesta con el contexto recuperado.
6. Se entrega la respuesta junto con las fuentes documentales.

---

## Buenas prácticas recomendadas

- Mantén una carpeta [corpus](corpus) ordenada y con documentos reales.
- Revisa el archivo [order_implementation.txt](order_implementation.txt) antes de desplegar cambios importantes.
- Ajusta el tamaño y solapamiento de chunks si el contenido legal se fragmenta en partes poco útiles.
- Verifica el índice y el skillset en Azure AI Search antes de cambiar el backend productivo.
- Evita mezclar documentos no relacionados con la temática de tránsito y normativa.

---

## Resultado esperado

El proyecto permite convertir documentos legales en un sistema conversacional capaz de responder preguntas sobre normativa de tránsito colombiano con base documental y trazabilidad a las fuentes.

Es una base sólida para construir un asistente legal o un motor de búsqueda especializado para normativas públicas.

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

Copyright (c) 2026

Se permite el uso, copia, modificación, fusión, publicación, distribución, sublicencia y/o venta de copias del software, siempre que se incluya el aviso de copyright y esta licencia en todas las copias o partes sustanciales del mismo.

El software se proporciona "tal cual", sin garantía de ningún tipo, ya sea expresa o implícita, incluyendo, pero no limitado a, la garantía de comerciabilidad, idoneidad para un propósito particular y no infracción.

Para más detalles, consulta el archivo [LICENSE](LICENSE).
