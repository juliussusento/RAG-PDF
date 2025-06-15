from typing import List, Tuple
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import settings
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.vector_db_path

        # HuggingFace embedding (GRATIS & lokal)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )

    def add_documents(self, documents: List[Document]) -> None:
        logger.info(f"Adding {len(documents)} documents to vector store...")
        self.vstore.add_documents(documents)
        self.vstore.persist()

    def similarity_search(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        k = k or settings.retrieval_k
        logger.info(f"Performing similarity search for: {query}")
        return self.vstore.similarity_search_with_score(query, k=k)

    def get_document_count(self) -> int:
        return self.vstore._collection.count()

    def delete_documents(self, document_ids: List[str]) -> None:
        logger.warning("Document deletion not implemented due to ChromaDB limitations.")
