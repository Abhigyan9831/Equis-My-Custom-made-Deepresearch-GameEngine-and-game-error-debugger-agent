
import base64
from pathlib import Path
from google import genai
from google.genai import types
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def describe_rendering_artifact(
    image_bytes: bytes,
    mime_type: str = "image/png",
    extra_context: str = "",
) -> str:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        "You are a Senior Graphics Engineer analyzing a rendering artifact screenshot.\n"
        "Describe in technical detail:\n"
        "1. What visual artifact or glitch is visible\n"
        "2. Which rendering system is likely causing it (shadows, normals, depth, etc.)\n"
        "3. Any visible error patterns (acne, z-fighting, flickering, etc.)\n"
        "Be specific — your description will be used to search Vulkan/UE5 documentation.\n"
    )
    if extra_context:
        prompt += f"\nDeveloper context: {extra_context}"

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_VLM_MODEL,
        contents=[prompt, image_part],
    )
    description = (response.text or "").strip()
    logger.info("VLM description generated", extra={"chars": len(description)})
    return description