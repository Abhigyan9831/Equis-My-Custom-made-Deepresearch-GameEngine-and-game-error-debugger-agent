from pydantic import BaseModel, Field
from typing import Optional




class LogAnalysisRequest(BaseModel):
    """Input for text-based error log analysis."""
    log_text: str = Field(..., min_length=10, description="Vulkan or UE5 error log")
    context: Optional[str] = Field(None, description="GPU model, scene info, etc.")
    session_id: Optional[str] = Field("default-session", description="Session ID for persistent memory")

    model_config = {
        "json_schema_extra": {
            "example": {
                "log_text": "VK_ERROR_OUT_OF_DEVICE_MEMORY on vkAllocateMemory at frame 42",
                "context": "RTX 3060 6GB, 200 draw calls, 4K textures",
                "session_id": "session-123"
            }
        }
    }




class ResearchSource(BaseModel):
    """A single source found during deep research."""
    title: str
    url: str
    snippet: str


class DiagnosisResult(BaseModel):
    """Structured output from the agent pipeline."""
    diagnosis: str                        # One-line problem summary
    root_cause: str                       # Technical explanation
    code_fix: Optional[str] = None        # GLSL / C++ / config fix (ONLY provided if strictly necessary)
    console_commands: list[str] = []      # Terminal / engine console commands
    affected_systems: list[str] = []      # Engine systems involved (e.g., Vulkan RHI, Nanite, Memory)
    sources: list[ResearchSource]         # All sources used
    confidence: str                       # high / medium / low
    cached: bool = False
    session_id: Optional[str] = None




class LogAnalysisResponse(BaseModel):
    """API response wrapper for log analysis."""
    success: bool
    result: Optional[DiagnosisResult] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None


class ImageAnalysisResponse(BaseModel):
    """API response wrapper for image analysis."""
    success: bool
    result: Optional[DiagnosisResult] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None