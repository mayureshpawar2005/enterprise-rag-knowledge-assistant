"""Enterprise RAG Knowledge Assistant — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.ask import router as ask_router
from app.routes.health import router as health_router
from app.routes.search import router as search_router
from app.routes.upload import router as upload_router
from app.utils.exceptions import (
    ConfigurationError,
    EmptyDocumentError,
    InvalidPDFError,
    LLMError,
    RAGException,
    VectorStoreError,
)
from app.utils.logger import get_logger, setup_logging
from app.utils.openapi import patch_binary_file_uploads

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure directories and log configuration status."""
    settings = get_settings()
    settings.ensure_directories()
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY is not set — /ask will fail until configured.")
    else:
        logger.info("Application started. Model: %s", settings.gemini_model)
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="Enterprise RAG Knowledge Assistant",
    description=(
        "Upload PDF documents, index them in ChromaDB, and ask questions "
        "answered by Google Gemini using retrieved context."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(search_router)


def custom_openapi() -> dict:
    """Generate OpenAPI schema with file-upload fields compatible with Swagger UI."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = patch_binary_file_uploads(schema)
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.exception_handler(InvalidPDFError)
@app.exception_handler(EmptyDocumentError)
async def client_error_handler(request: Request, exc: RAGException) -> JSONResponse:
    logger.warning("Client error on %s: %s", request.url.path, exc.message)
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(ConfigurationError)
async def config_error_handler(request: Request, exc: ConfigurationError) -> JSONResponse:
    logger.error("Configuration error: %s", exc.message)
    return JSONResponse(status_code=503, content={"detail": exc.message})


@app.exception_handler(VectorStoreError)
async def vector_error_handler(request: Request, exc: VectorStoreError) -> JSONResponse:
    logger.error("Vector store error: %s", exc.message)
    return JSONResponse(status_code=500, content={"detail": exc.message})


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    logger.error("LLM error: %s", exc.message)
    return JSONResponse(status_code=502, content={"detail": exc.message})


@app.exception_handler(RAGException)
async def rag_error_handler(request: Request, exc: RAGException) -> JSONResponse:
    logger.error("RAG error: %s", exc.message)
    return JSONResponse(status_code=500, content={"detail": exc.message})


@app.get("/")
async def root() -> dict:
    """API root with quick links."""
    return {
        "service": "Enterprise RAG Knowledge Assistant",
        "docs": "/docs",
        "health": "/health",
        "upload": "POST /upload",
        "ask": "POST /ask",
        "search": "POST /search",
    }
