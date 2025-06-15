import os
from typing import List, Dict, Any
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF and return list of page-wise text"""
        logger.info(f"Extracting text from: {file_path}")
        pages = []

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({
                    "page": i + 1,
                    "content": text.strip()
                })

        logger.info(f"Extracted {len(pages)} pages.")
        return pages

    def split_into_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Document]:
        """Split each page's content into chunks and return as Documents"""
        all_chunks = []

        for page_data in pages_content:
            text = page_data["content"]
            page = page_data["page"]

            splits = self.splitter.split_text(text)
            for chunk in splits:
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata={"page": page}
                ))

        logger.info(f"Generated {len(all_chunks)} chunks from document.")
        return all_chunks

    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF file and return list of Document objects"""
        pages = self.extract_text_from_pdf(file_path)
        chunks = self.split_into_chunks(pages)
        return chunks
