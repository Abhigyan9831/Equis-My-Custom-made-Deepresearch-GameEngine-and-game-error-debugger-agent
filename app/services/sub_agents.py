import asyncio
import concurrent.futures
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langsmith import traceable
from langgraph.prebuilt import create_react_agent
from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.tools import (
    search_vulkan_docs,
    search_ue5_docs,
    search_web,
    search_reddit,
    search_forums,
    search_github_issues,
    run_diagnostic_command,
    find_game_bug,
    generate_code_fix,
)

logger = get_logger(__name__)
settings = get_settings()

def _get_llm(max_tokens: int = 512) -> ChatGroq:
    return ChatGroq(
        model=settings.GROQ_MODEL_ID,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0.1,
        max_tokens=max_tokens,
        model_kwargs={"extra_body": {"reasoning_format": "hidden"}},
    )

# ── Sub-Agent Executors (max_tokens=512) ──
def _create_sub_agent(system_prompt: str, tools: list):
    llm = _get_llm(max_tokens=512)
    return create_react_agent(model=llm, tools=tools)

# Vulkan Expert Agent
VULKAN_PROMPT = (
    "You are a Vulkan Graphics Sub-Agent. Analyze the Vulkan error, validation hazard, "
    "or memory allocation failure. Search docs or diagnostic info and summarize findings and exact fix."
)
_vulkan_agent = _create_sub_agent(
    VULKAN_PROMPT,
    [search_vulkan_docs, run_diagnostic_command, search_forums, generate_code_fix]
)

# UE5 Expert Agent
UE5_PROMPT = (
    "You are an Unreal Engine 5 Sub-Agent. Analyze the UE5 crash, RHI/rendering error, "
    "material, or Nanite/Lumen artifact. Search docs and summarize findings and exact fix."
)
_ue5_agent = _create_sub_agent(
    UE5_PROMPT,
    [search_ue5_docs, search_forums, generate_code_fix]
)

# Web & Community Research Agent
WEB_PROMPT = (
    "You are a Web & Community Research Sub-Agent. Search Reddit, developer forums, "
    "and GitHub issues for community repros, workarounds, and discussions for the error."
)
_web_agent = _create_sub_agent(
    WEB_PROMPT,
    [search_reddit, search_forums, search_github_issues, search_web]
)

# Game Bug Specialist Agent
GAME_BUG_PROMPT = (
    "You are a Game Bug Specialist Sub-Agent specialized in shipped game bugs, regression reports, "
    "patch notes, and player workarounds. Suggest console commands, ini config tweaks, or workarounds."
)
_game_bug_agent = _create_sub_agent(
    GAME_BUG_PROMPT,
    [find_game_bug, search_github_issues, search_reddit, search_forums]
)


# ── Shared thread-based runner for true timeout enforcement ──
# asyncio.wait_for cannot cancel LangGraph ainvoke (non-cooperative).
# Running each agent in its own OS thread lets asyncio cancel the *thread future*
# and return immediately, while the abandoned thread finishes quietly in the bg.
_sub_agent_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="sub_agent")

def _run_agent_in_thread(agent, messages: list, recursion_limit: int = 6):
    """Synchronous wrapper — runs agent.ainvoke in a fresh event loop inside a worker thread."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            agent.ainvoke({"messages": messages}, config={"recursion_limit": recursion_limit})
        )
    finally:
        loop.close()

def _extract_content(res) -> str:
    content = res["messages"][-1].content
    if isinstance(content, list):
        content = "".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)


# ── Sub-Agent Node Functions with 20s hard timeout via ThreadPoolExecutor ──
@traceable(name="SubAgent_Vulkan", run_type="chain")
async def vulkan_node(query: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        res = await asyncio.wait_for(
            loop.run_in_executor(
                _sub_agent_pool, _run_agent_in_thread, _vulkan_agent,
                [SystemMessage(content=VULKAN_PROMPT), HumanMessage(content=query)], 6
            ),
            timeout=20.0,
        )
        return _extract_content(res)
    except asyncio.TimeoutError:
        logger.warning("vulkan_node timed out after 20s")
        return "Vulkan analysis timed out after 20s."
    except Exception as e:
        logger.warning(f"vulkan_node error: {e}")
        return f"Vulkan analysis encountered an error: {e}"


@traceable(name="SubAgent_UE5", run_type="chain")
async def ue5_node(query: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        res = await asyncio.wait_for(
            loop.run_in_executor(
                _sub_agent_pool, _run_agent_in_thread, _ue5_agent,
                [SystemMessage(content=UE5_PROMPT), HumanMessage(content=query)], 6
            ),
            timeout=20.0,
        )
        return _extract_content(res)
    except asyncio.TimeoutError:
        logger.warning("ue5_node timed out after 20s")
        return "UE5 analysis timed out after 20s."
    except Exception as e:
        logger.warning(f"ue5_node error: {e}")
        return f"UE5 analysis encountered an error: {e}"


@traceable(name="SubAgent_Web", run_type="chain")
async def web_node(query: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        res = await asyncio.wait_for(
            loop.run_in_executor(
                _sub_agent_pool, _run_agent_in_thread, _web_agent,
                [SystemMessage(content=WEB_PROMPT), HumanMessage(content=query)], 6
            ),
            timeout=20.0,
        )
        return _extract_content(res)
    except asyncio.TimeoutError:
        logger.warning("web_node timed out after 20s")
        return "Web search timed out after 20s."
    except Exception as e:
        logger.warning(f"web_node error: {e}")
        return f"Web search encountered an error: {e}"


@traceable(name="SubAgent_GameBug", run_type="chain")
async def game_bug_node(query: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        res = await asyncio.wait_for(
            loop.run_in_executor(
                _sub_agent_pool, _run_agent_in_thread, _game_bug_agent,
                [SystemMessage(content=GAME_BUG_PROMPT), HumanMessage(content=query)], 6
            ),
            timeout=20.0,
        )
        return _extract_content(res)
    except asyncio.TimeoutError:
        logger.warning("game_bug_node timed out after 20s")
        return "Game bug research timed out after 20s."
    except Exception as e:
        logger.warning(f"game_bug_node error: {e}")
        return f"Game bug research encountered an error: {e}"
