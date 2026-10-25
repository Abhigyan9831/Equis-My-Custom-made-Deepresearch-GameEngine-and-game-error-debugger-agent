from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.v1.routes import router
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="GameEngine-Doctor",
    description="Multimodal Deep Research AI Agent for Vulkan/UE5 debugging",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
async def serve_ui():
    return FileResponse("app/static/index.html")

app.include_router(router, prefix="/api/v1", tags=["Analysis"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", extra={"path": str(request.url), "error": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "2.0.0"}