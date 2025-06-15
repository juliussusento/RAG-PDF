from typing import List, Dict, Any
from langchain.schema import Document
from services.vector_store import VectorStoreService
from langchain_community.llms import HuggingFaceHub
from config import settings
import time
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store

        self.llm = HuggingFaceHub(
            repo_id=settings.huggingface_model_id,
            huggingfacehub_api_token=settings.huggingfacehub_api_token,
            model_kwargs={
                "temperature": settings.llm_temperature,
                "max_new_tokens": settings.max_tokens,
            },
        )

    def generate_answer(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        start_time = time.time()
        chat_history = chat_history or []

        documents = self._retrieve_documents(question)
        context = self._generate_context(documents)
        answer = self._generate_llm_response(question, context, chat_history)

        duration = time.time() - start_time

        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content,
                    "page": doc.metadata.get("page", -1),
                    "metadata": doc.metadata,
                    "score": 0.0
                }
                for doc in documents
            ],
            "processing_time": duration
        }

    def _retrieve_documents(self, query: str) -> List[Document]:
        results = self.vector_store.similarity_search(query, k=settings.retrieval_k)
        return [doc for doc, score in results if score >= settings.similarity_threshold]

    def _generate_context(self, documents: List[Document]) -> str:
        return "\n\n".join([doc.page_content for doc in documents])

    def _generate_llm_response(self, question: str, context: str, chat_history: List[Dict[str, str]]) -> str:
        prompt = (
            "You are a helpful assistant specialized in financial documents.\n"
            "Use the following context to answer the user's question accurately.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        try:
            response = self.llm.client(
                inputs=prompt,
                params={
                    "temperature": settings.llm_temperature,
                    "max_new_tokens": settings.max_tokens
                },
                raw_response=True
            )

            json_data = response.json()

            # Menangani respons berupa list atau dict
            if isinstance(json_data, list) and json_data and "generated_text" in json_data[0]:
                return json_data[0]["generated_text"].strip()
            elif isinstance(json_data, dict) and "generated_text" in json_data:
                return json_data["generated_text"].strip()
            elif isinstance(json_data, dict) and "error" in json_data:
                return f"❌ Error from model: {json_data['error']}"
            else:
                return f"⚠️ Unexpected response format: {str(json_data).strip()}"

        except Exception as e:
            return f"❌ Exception while parsing response: {str(e)}"
