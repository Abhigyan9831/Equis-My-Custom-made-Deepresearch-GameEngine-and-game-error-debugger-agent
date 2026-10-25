import time
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.schemas import LogAnalysisRequest, LogAnalysisResponse, ImageAnalysisResponse
from app.services.agent_service import run_agent
from app.services.vlm_service import describe_rendering_artifact
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/analyze-log", response_model=LogAnalysisResponse)
async def analyze_log(request: LogAnalysisRequest):
    """
    Accept Vulkan/UE5 error log text.
    Runs deep research agent -> returns structured diagnosis.
    """
    start = time.perf_counter()
    try:
        query = (
            f"{request.log_text}\nContext: {request.context}"
            if request.context
            else request.log_text
        )
        session_id = request.session_id or "default-session"
        result = await run_agent(query, session_id=session_id)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("analyze_log done", extra={"latency_ms": latency_ms, "cached": result.cached, "session_id": session_id})
        return LogAnalysisResponse(success=True, result=result, latency_ms=latency_ms)
    except Exception as e:
        logger.error("analyze_log failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(..., description="Screenshot of rendering glitch"),
    context: Optional[str] = Form(None, description="Optional developer context"),
    session_id: Optional[str] = Form("default-session", description="Session ID for persistent memory"),
):
    """
    Accept screenshot + optional context.
    Step 1: Gemini Flash VLM describes the visual artifact.
    Step 2: Agent runs deep research on that description.
    Returns structured diagnosis.
    """
    start = time.perf_counter()
    try:
        image_bytes = await file.read()
        mime_type = file.content_type or "image/png"

        # Step 1: VLM describes the visual artifact
        description = await describe_rendering_artifact(
            image_bytes, mime_type, context or ""
        )

        # Step 2: Agent researches based on VLM description
        query = f"Visual rendering artifact detected:\n{description}"
        if context:
            query += f"\nDeveloper context: {context}"

        result = await run_agent(query, session_id=session_id or "default-session")
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("analyze_image done", extra={"latency_ms": latency_ms, "session_id": session_id})
        return ImageAnalysisResponse(success=True, result=result, latency_ms=latency_ms)
    except Exception as e:
        logger.error("analyze_image failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))