from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from models.schemas import (
    ChatRequest, ChatResponse,
    UploadResponse, DocumentsResponse,
    DocumentInfo, ChunksResponse, ChunkInfo
)
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStoreService
from services.rag_pipeline import RAGPipeline
from config import settings
import logging
import time
import os

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG-based Financial Statement Q&A System",
    description="AI-powered Q&A system for financial documents using RAG",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
pdf_processor = None
vector_store = None
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline services on app startup"""
    global pdf_processor, vector_store, rag_pipeline
    logger.info("Initializing RAG pipeline services...")
    pdf_processor = PDFProcessor()
    vector_store = VectorStoreService()
    rag_pipeline = RAGPipeline(vector_store=vector_store)


@app.get("/")
async def root():
    return {"message": "RAG-based Financial Statement Q&A System is running"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    start_time = time.time()
    os.makedirs(settings.pdf_upload_path, exist_ok=True)
    save_path = os.path.join(settings.pdf_upload_path, file.filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    pages = pdf_processor.extract_text_from_pdf(save_path)
    chunks = pdf_processor.split_into_chunks(pages)
    vector_store.add_documents(chunks)

    processing_time = time.time() - start_time

    return UploadResponse(
        message="PDF processed successfully.",
        filename=file.filename,
        chunks_count=len(chunks),
        processing_time=processing_time
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate answer from question using RAG"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = rag_pipeline.generate_answer(
        request.question,
        chat_history=request.chat_history
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        processing_time=result["processing_time"]
    )


@app.get("/api/documents", response_model=DocumentsResponse)
async def get_documents():
    files = [f for f in os.listdir(settings.pdf_upload_path) if f.endswith(".pdf")]
    documents = []
    for filename in files:
        info = DocumentInfo(
            filename=filename,
            upload_date=datetime.fromtimestamp(os.path.getctime(os.path.join(settings.pdf_upload_path, filename))),
            chunks_count=0,
            status="processed"
        )
        documents.append(info)
    return DocumentsResponse(documents=documents)

@app.get("/api/chunks", response_model=ChunksResponse)
async def get_chunks():
    chunks = []
    for filename in os.listdir(settings.pdf_upload_path):
        if filename.endswith(".pdf"):
            path = os.path.join(settings.pdf_upload_path, filename)
            doc_chunks = pdf_processor.process_pdf(path)
            for i, chunk in enumerate(doc_chunks):
                chunks.append(ChunkInfo(
                    id=f"{filename}-{i}",
                    content=chunk.page_content,
                    page=chunk.metadata.get("page", 0),
                    metadata=chunk.metadata
                ))

    return ChunksResponse(chunks=chunks, total_count=len(chunks))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
