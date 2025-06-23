# app/services/document_service.py

from app.retrievers import get_compressor, get_retriever
from app.templates import format_docs
from langchain_google_vertexai import VertexAIEmbeddings
import vertexai
import os
import google.auth

EMBEDDING_MODEL = "text-embedding-005"
LOCATION = "us-central1"

credentials, project_id = google.auth.default()
vertexai.init(project=project_id, location=LOCATION)

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

embedding = VertexAIEmbeddings(
    project=project_id, location=LOCATION, model_name=EMBEDDING_MODEL
)

retriever = get_retriever(
    project_id=project_id,
    data_store_id=os.getenv("DATA_STORE_ID", "my-awesome-agent-datastore"),
    data_store_region=os.getenv("DATA_STORE_REGION", "us"),
    embedding=embedding,
    embedding_column="embedding",
    max_documents=10,
)

compressor = get_compressor(project_id=project_id)


def retrieve_docs(query: str) -> str:
    """
    Useful for retrieving relevant documents based on a query.
    Use this when you need additional information to answer a question.

    Args:
        query (str): The user's question or search query.

    Returns:
        str: Formatted string containing relevant document content retrieved and ranked based on the query.
    """
    try:
        retrieved_docs = retriever.invoke(query)
        ranked_docs = compressor.compress_documents(documents=retrieved_docs, query=query)
        formatted_docs = format_docs.format(docs=ranked_docs)
        return formatted_docs
    except Exception as e:
        return f"[Document Retrieval Error]\nQuery: {query}\nError: {type(e)}: {e}"
