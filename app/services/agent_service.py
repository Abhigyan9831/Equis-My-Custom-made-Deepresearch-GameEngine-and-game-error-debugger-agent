import re
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langsmith import traceable
from app.services.sub_agents import vulkan_node, ue5_node, web_node, game_bug_node
from app.services.cache import make_cache_key, get_cached, set_cached
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import DiagnosisResult, ResearchSource
from app.services.memory_service import add_turn, get_conversation_history
from app.core.security import sanitize_input

logger = get_logger(__name__)
settings = get_settings()

ORCHESTRATOR_PROMPT = (
    "You are an expert Graphics & Game Engine Routing Classifier.\n"
    "Classify the input error query into EXACTLY ONE category:\n"
    "- VULKAN_ERROR (pure Vulkan API/validation errors, memory, barriers, shaders)\n"
    "- UE5_ERROR (Unreal Engine 5 crashes, RHI, Blueprints, Nanite/Lumen, materials)\n"
    "- GAME_BUG (shipped game crashes, FPS drops, player bug reports, console commands)\n"
    "- SHADER_ERROR (GLSL, HLSL, spirv, shader compilation/runtime errors)\n"
    "- GENERAL (ambiguous, mixed, or general rendering questions)\n\n"
    "Respond with ONLY the category keyword."
)

SYNTHESIZER_PROMPT = (
    "You are a Senior Graphics Architect. You are given sub-agent research findings from Vulkan, UE5, "
    "Web, and Game Bug experts.\n\n"
    "Tasks:\n"
    "1. Synthesize a unified, authoritative diagnosis and root cause.\n"
    "2. Autonomously decide: is a code fix strictly necessary? DO NOT provide code if the problem can be resolved via engine CVars, project settings, driver update, or asset reconfiguration. Only provide CODE_FIX if a code/shader patch is mandatory.\n"
    "3. List all involved engine systems (e.g., Vulkan RHI, Nanite, Memory Allocator, Driver, PSO Cache).\n"
    "4. List any applicable console commands or config variables (e.g., r.Shadow.MaxResolution, vkCmd*).\n\n"
    "Respond in EXACTLY this format:\n\n"
    "DIAGNOSIS: <one-sentence problem summary>\n"
    "ROOT_CAUSE: <technical explanation>\n"
    "AFFECTED_SYSTEMS: <comma-separated list of engine systems>\n"
    "CONSOLE_COMMANDS: <comma-separated list of console commands or None>\n"
    "CONFIDENCE: <high | medium | low>\n"
    "CODE_FIX: <None or code block with exact fix>\n"
    "SOURCES: <comma-separated list of URLs used>"
)


@traceable(name="Orchestrator_Classifier", run_type="chain")
async def _classify_query(query: str) -> str:
    """Orchestrator: classify query with max_tokens=256 via Groq."""
    try:
        llm = ChatGroq(
            model=settings.GROQ_MODEL_ID,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.0,
            max_tokens=256,
            model_kwargs={"extra_body": {"reasoning_format": "hidden"}},
        )
        res = await llm.ainvoke([
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=query[:500]),
        ])
        raw_content = res.content
        if isinstance(raw_content, list):
            cat = "".join(item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_content).strip().upper()
        else:
            cat = str(raw_content or "").strip().upper()
        for valid in ["VULKAN_ERROR", "UE5_ERROR", "GAME_BUG", "SHADER_ERROR", "GENERAL"]:
            if valid in cat:
                logger.info(f"Orchestrator classified query as: {valid}")
                return valid
    except Exception as e:
        logger.warning(f"Classification failed ({e}), defaulting to GENERAL")
    return "GENERAL"


def _parse_synthesizer_output(raw_in) -> dict:
    if isinstance(raw_in, list):
        raw = "".join(item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_in)
    else:
        raw = str(raw_in or "")
    diagnosis = re.search(r"DIAGNOSIS:(.*?)(?:ROOT_CAUSE:|$)", raw, re.S)
    root_cause = re.search(r"ROOT_CAUSE:(.*?)(?:AFFECTED_SYSTEMS:|$)", raw, re.S)
    affected_sys = re.search(r"AFFECTED_SYSTEMS:(.*?)(?:CONSOLE_COMMANDS:|$)", raw, re.S)
    console_cmds = re.search(r"CONSOLE_COMMANDS:(.*?)(?:CONFIDENCE:|$)", raw, re.S)
    confidence = re.search(r"CONFIDENCE:(.*?)(?:CODE_FIX:|$)", raw, re.S)
    code_fix = re.search(r"CODE_FIX:(.*?)(?:SOURCES:|$)", raw, re.S)
    sources_raw = re.search(r"SOURCES:(.*)", raw, re.S)

    sources = []
    if sources_raw:
        for url in sources_raw.group(1).strip().split(","):
            url = url.strip()
            if url and ("http://" in url or "https://" in url):
                sources.append(ResearchSource(title="source", url=url, snippet="").model_dump())

    # Fallback to extracting any URLs in raw output if SOURCES tag had none
    if not sources:
        urls = re.findall(r'https?://[^\s,\)\]]+', raw)
        for url in urls[:4]:
            sources.append(ResearchSource(title="source", url=url, snippet="").model_dump())

    aff_list = []
    if affected_sys:
        aff_list = [s.strip() for s in affected_sys.group(1).split(",") if s.strip() and s.strip().lower() != "none"]

    cmd_list = []
    if console_cmds:
        cmd_list = [c.strip() for c in console_cmds.group(1).split(",") if c.strip() and c.strip().lower() != "none"]

    fix_val = code_fix.group(1).strip() if code_fix else None
    if fix_val and (fix_val.lower() == "none" or "no code fix needed" in fix_val.lower()):
        fix_val = None

    return {
        "diagnosis": diagnosis.group(1).strip() if diagnosis else raw[:250],
        "root_cause": root_cause.group(1).strip() if root_cause else "",
        "affected_systems": aff_list,
        "console_commands": cmd_list,
        "confidence": confidence.group(1).strip().lower() if confidence else "medium",
        "code_fix": fix_val,
        "sources": sources,
        "cached": False,
    }


@traceable(name="Equis_Agent_Pipeline", run_type="chain")
async def run_agent(query: str, session_id: str = "default-session") -> DiagnosisResult:
    # 0. Security Guardrails: Sanitize query and detect prompt injection
    sanitized_query, injection_detected, redacted_items = sanitize_input(query)
    if injection_detected:
        logger.warning("Prompt injection detected", extra={"query": query[:60]})
        return DiagnosisResult(
            diagnosis="Security Violation: Prompt Injection Attempt Blocked",
            root_cause="The input contains forbidden instructions attempting to bypass agent safety boundaries.",
            code_fix=None,
            console_commands=[],
            affected_systems=["Security Guardrail Filter"],
            sources=[],
            confidence="high",
            cached=False,
            session_id=session_id
        )

    cache_key = make_cache_key(sanitized_query, prefix="agent_v2")

    # Cache check
    cached = get_cached(cache_key)
    if cached:
        logger.info("Agent cache hit")
        cached["cached"] = True
        cached["session_id"] = session_id
        # Record turn in persistent memory
        add_turn(session_id, "user", sanitized_query)
        add_turn(session_id, "assistant", cached.get("diagnosis", ""))
        return DiagnosisResult(**cached)

    logger.info("Agent starting multi-agent pipeline", extra={"query": sanitized_query[:80], "session_id": session_id})

    # Retrieve past conversation history from persistent memory
    history = get_conversation_history(session_id, limit=4)
    history_context = ""
    if history:
        history_context = "\n".join([f"[{t['role'].upper()}]: {t['content']}" for t in history])

    # 1. Orchestrator classification
    category = await _classify_query(sanitized_query)

    # 2. Select parallel sub-agents based on classification (skip irrelevant ones)
    tasks = []
    task_names = []

    if category == "VULKAN_ERROR":
        tasks = [vulkan_node(sanitized_query), web_node(sanitized_query)]
        task_names = ["Vulkan Expert", "Web Research"]
    elif category == "UE5_ERROR":
        tasks = [ue5_node(sanitized_query), web_node(sanitized_query)]
        task_names = ["UE5 Expert", "Web Research"]
    elif category == "GAME_BUG":
        tasks = [game_bug_node(sanitized_query), web_node(sanitized_query)]
        task_names = ["Game Bug Specialist", "Web Research"]
    elif category == "SHADER_ERROR":
        tasks = [vulkan_node(sanitized_query), ue5_node(sanitized_query)]
        task_names = ["Vulkan Expert", "UE5 Expert"]
    else:  # GENERAL
        tasks = [vulkan_node(sanitized_query), ue5_node(sanitized_query), web_node(sanitized_query)]
        task_names = ["Vulkan Expert", "UE5 Expert", "Web Research"]

    # Run selected sub-agents concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect sub-agent outputs
    combined_findings = []
    for name, res in zip(task_names, results):
        if isinstance(res, Exception):
            combined_findings.append(f"### {name}:\nEncountered error: {res}")
        else:
            combined_findings.append(f"### {name}:\n{res}")

    findings_text = "\n\n".join(combined_findings)

    # 3. Synthesizer node (max_tokens=1536)
    synthesizer_llm = ChatGroq(
        model=settings.GROQ_MODEL_ID,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0.1,
        max_tokens=1536,
        model_kwargs={"extra_body": {"reasoning_format": "hidden"}},
    )
    synth_prompt = (
        f"Conversation History:\n{history_context if history_context else 'None'}\n\n"
        f"Original User Error:\n{sanitized_query}\n\n"
        f"Sub-Agent Findings:\n{findings_text}\n\n"
        "Please provide the final authoritative diagnosis according to instructions. "
        "Only output CODE_FIX if a code patch is strictly necessary, otherwise state None."
    )
    synth_res = await synthesizer_llm.ainvoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=synth_prompt),
    ])

    parsed = _parse_synthesizer_output(synth_res.content or "")
    parsed["session_id"] = session_id
    set_cached(cache_key, parsed)

    # Record turn in persistent SQLite memory
    add_turn(session_id, "user", sanitized_query)
    add_turn(session_id, "assistant", parsed.get("diagnosis", ""))

    return DiagnosisResult(**parsed)