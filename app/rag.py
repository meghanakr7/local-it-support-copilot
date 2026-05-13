from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.config import settings


COLLECTION_NAME = "it_support_docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(settings.vector_store_dir))


def _get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )


def _get_collection():
    client = _get_client()
    embedding_function = _get_embedding_function()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "Local IT support knowledge base"}
    )


def _read_markdown_files() -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []

    for file_path in sorted(settings.docs_dir.glob("*.md")):
        text = file_path.read_text(encoding="utf-8").strip()
        if text:
            docs.append((file_path.name, text))

    return docs


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    words = text.split()
    chunks: list[str] = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def reset_vector_store() -> None:
    client = _get_client()

    existing = [collection.name for collection in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    _get_collection()


def build_index(reset: bool = True) -> dict[str, Any]:
    if reset:
        reset_vector_store()

    collection = _get_collection()
    docs = _read_markdown_files()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []

    for filename, text in docs:
        chunks = _chunk_text(text)

        for index, chunk in enumerate(chunks):
            chunk_id = f"{filename}::chunk-{index}"

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": filename,
                    "chunk_index": index
                }
            )

    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    return {
        "collection": COLLECTION_NAME,
        "documents_loaded": len(docs),
        "chunks_indexed": len(ids),
        "sources": [filename for filename, _ in docs]
    }


def search_docs(query: str, top_k: int = 4) -> dict[str, Any]:
    collection = _get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    matches: list[dict[str, Any]] = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances
    ):
        matches.append(
            {
                "id": chunk_id,
                "source": metadata.get("source"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": distance,
                "content": document
            }
        )

    return {
        "query": query,
        "matches": matches
    }


def format_search_results(results: dict[str, Any]) -> str:
    formatted_chunks: list[str] = []

    for index, match in enumerate(results["matches"], start=1):
        formatted_chunks.append(
            f"[Document {index}: {match['source']}]\n"
            f"{match['content']}"
        )

    return "\n\n---\n\n".join(formatted_chunks)