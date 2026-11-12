from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logging import setup_logging, get_logger
from backend.core.exceptions import KnovaException
from backend.api.routes import workspaces
from backend.api.routes import documents
from backend.api.routes import chat
from backend.api.routes import workspace_members
from backend.api.routes import auth


setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Knowledge Intelligence Platform — RAG-powered document search and Q&A",
    version=settings.APP_VERSION,
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(workspace_members.router)

logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")



@app.exception_handler(KnovaException)
async def knova_exception_handler(request: Request, exc: KnovaException):
    logger.warning(f"KnovaException: {exc.message} (status={exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.get("/")
def read_root():
    logger.debug("Root endpoint called")
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
def health_check():
    logger.debug("Health check called")
    return {"status": "ok"}


