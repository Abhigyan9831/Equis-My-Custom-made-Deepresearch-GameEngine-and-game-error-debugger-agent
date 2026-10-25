
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.services.ingestor import get_vectorstore
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()




@tool
async def search_vulkan_docs(query: str) -> str:
    """
    Search the Vulkan specification and Khronos documentation.
    Use this for Vulkan API errors, validation errors, memory errors,
    pipeline issues, or any vk* function errors.
    """
    try:
        vectorstore = get_vectorstore()
        docs = await vectorstore.asimilarity_search(
            query,
            k=settings.TOP_K,
            filter={"source_type": "vulkan"},
        )
        if not docs:
            # fallback without filter
            docs = await vectorstore.asimilarity_search(query, k=settings.TOP_K)

        results = "\n\n---\n\n".join(
            f"Source: {d.metadata.get('url', d.metadata.get('source', 'unknown'))}\n{d.page_content}"
            for d in docs
        )
        logger.info("search_vulkan_docs", extra={"query": query[:60], "hits": len(docs)})
        return results or "No relevant Vulkan documentation found in vectorstore."
    except Exception as e:
        logger.warning(f"search_vulkan_docs vector search failed ({e}). Fallback to web search.")
        return f"Vulkan vector documentation search unavailable ({e}). Please use search_web to find the solution."




@tool
async def search_ue5_docs(query: str) -> str:
    """
    Search Unreal Engine 5 rendering documentation.
    Use this for UE5 shader errors, material issues, shadow problems,
    Blueprint errors, or any Unreal-specific rendering artifacts.
    """
    try:
        vectorstore = get_vectorstore()
        docs = await vectorstore.asimilarity_search(
            query,
            k=settings.TOP_K,
            filter={"source_type": "ue5"},
        )
        if not docs:
            docs = await vectorstore.asimilarity_search(query, k=settings.TOP_K)

        results = "\n\n---\n\n".join(
            f"Source: {d.metadata.get('url', d.metadata.get('source', 'unknown'))}\n{d.page_content}"
            for d in docs
        )
        logger.info("search_ue5_docs", extra={"query": query[:60], "hits": len(docs)})
        return results or "No relevant UE5 documentation found in vectorstore."
    except Exception as e:
        logger.warning(f"search_ue5_docs vector search failed ({e}). Fallback to web search.")
        return f"UE5 vector documentation search unavailable ({e}). Please use search_web to find the solution."




@tool
async def search_web(query: str) -> str:
    """
    Search the web for additional context: Reddit, Stack Overflow,
    GitHub issues, Unreal forums, developer blogs.
    Use this when Vulkan/UE5 docs don't have enough information,
    or to find real-world fixes from the developer community.
    """
    try:
        search = TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=2,
            search_depth="basic",
            include_domains=[
                "stackoverflow.com",
                "reddit.com",
                "github.com",
                "forums.unrealengine.com",
                "vulkan.gpuinfo.org",
                "gamedev.stackexchange.com",
            ],
        )
        results = await search.ainvoke(query)
        if isinstance(results, tuple):
            results = results[0]
        if isinstance(results, list):
            formatted = "\n\n".join(
                f"Source: {r.get('url', '')}\nSummary: {r.get('content', '')[:250]}"
                for r in results if isinstance(r, dict)
            )
        else:
            formatted = str(results)[:500]
        logger.info("search_web", extra={"query": query[:60], "hits": len(results) if isinstance(results, list) else 1})
        return formatted or "No web results found."
    except Exception as e:
        logger.warning(f"search_web failed: {e}")
        return f"Web search could not be completed: {e}"




@tool
async def search_reddit(query: str) -> str:
    """Search Reddit gamedev communities (r/vulkan, r/unrealengine, r/gamedev) for crash solutions."""
    try:
        search = TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=2,
            search_depth="basic",
            include_domains=["reddit.com"],
        )
        results = await search.ainvoke(f"{query} (site:reddit.com/r/vulkan OR site:reddit.com/r/unrealengine OR site:reddit.com/r/gamedev)")
        if isinstance(results, tuple):
            results = results[0]
        if isinstance(results, list):
            formatted = "\n\n".join(
                f"Source: {r.get('url', '')}\nSummary: {r.get('content', '')[:250]}"
                for r in results if isinstance(r, dict)
            )
        else:
            formatted = str(results)[:500]
        logger.info("search_reddit", extra={"query": query[:60], "hits": len(results) if isinstance(results, list) else 1})
        return formatted or "No Reddit results found."
    except Exception as e:
        logger.warning(f"search_reddit failed: {e}")
        return f"Reddit search failed: {e}"


@tool
async def search_forums(query: str) -> str:
    """Search developer forums (Unreal Engine forums, Khronos community, gamedevs.org, discourse.threejs.org)."""
    try:
        search = TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=2,
            search_depth="basic",
            include_domains=[
                "forums.unrealengine.com",
                "community.khronos.org",
                "gamedevs.org",
                "discourse.threejs.org",
            ],
        )
        results = await search.ainvoke(query)
        if isinstance(results, tuple):
            results = results[0]
        if isinstance(results, list):
            formatted = "\n\n".join(
                f"Source: {r.get('url', '')}\nSummary: {r.get('content', '')[:250]}"
                for r in results if isinstance(r, dict)
            )
        else:
            formatted = str(results)[:500]
        logger.info("search_forums", extra={"query": query[:60], "hits": len(results) if isinstance(results, list) else 1})
        return formatted or "No forum results found."
    except Exception as e:
        logger.warning(f"search_forums failed: {e}")
        return f"Forum search failed: {e}"


@tool
async def search_github_issues(query: str) -> str:
    """Search GitHub issues for known engine bugs, crash repros, and workarounds."""
    try:
        search = TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=2,
            search_depth="basic",
            include_domains=["github.com"],
        )
        results = await search.ainvoke(f"{query} site:github.com/*/issues")
        if isinstance(results, tuple):
            results = results[0]
        if isinstance(results, list):
            formatted = "\n\n".join(
                f"Source: {r.get('url', '')}\nSummary: {r.get('content', '')[:250]}"
                for r in results if isinstance(r, dict)
            )
        else:
            formatted = str(results)[:500]
        logger.info("search_github_issues", extra={"query": query[:60], "hits": len(results) if isinstance(results, list) else 1})
        return formatted or "No GitHub issues found."
    except Exception as e:
        logger.warning(f"search_github_issues failed: {e}")
        return f"GitHub issues search failed: {e}"


@tool
async def run_diagnostic_command(command: str) -> str:
    """Run whitelist-only local diagnostic commands: nvidia-smi, vulkaninfo, or glxinfo."""
    allowed_binaries = {"nvidia-smi", "vulkaninfo", "glxinfo"}
    cmd_clean = command.strip().split()[0] if command.strip() else ""
    if cmd_clean not in allowed_binaries:
        return f"Access Denied: command '{cmd_clean}' is not in the whitelist ({', '.join(allowed_binaries)})."
    try:
        import asyncio
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        output = (stdout.decode() or stderr.decode()).strip()
        logger.info("run_diagnostic_command", extra={"cmd": command[:40]})
        return output[:800] if output else "Command executed with no output."
    except Exception as e:
        logger.warning(f"Diagnostic command failed: {e}")
        return f"Command execution failed: {e}"


@tool
async def find_game_bug(bug_description: str, engine: str = "general") -> str:
    """Search known game bug databases, GitHub issues, and patch notes for shipped game bugs."""
    try:
        search = TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=2,
            search_depth="basic",
            include_domains=[
                "github.com",
                "pcgamingwiki.com",
                "forums.unrealengine.com",
                "steamcommunity.com",
            ],
        )
        query = f"{engine} bug patch notes issue: {bug_description}"
        results = await search.ainvoke(query)
        if isinstance(results, tuple):
            results = results[0]
        if isinstance(results, list):
            formatted = "\n\n".join(
                f"Source: {r.get('url', '')}\nSummary: {r.get('content', '')[:250]}"
                for r in results if isinstance(r, dict)
            )
        else:
            formatted = str(results)[:500]
        logger.info("find_game_bug", extra={"query": bug_description[:60]})
        return formatted or "No matching game bug reports found."
    except Exception as e:
        logger.warning(f"find_game_bug failed: {e}")
        return f"Game bug search failed: {e}"


@tool
async def generate_code_fix(problem_description: str) -> str:
    """Generate production-ready code or configuration fix for Vulkan, GLSL, or UE5."""
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model=settings.GROQ_MODEL_ID,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0.1,
        max_tokens=512,
        model_kwargs={"extra_body": {"reasoning_format": "hidden"}},
    )
    prompt = (
        "You are a Senior Graphics Engineer.\n"
        "Generate a precise, production-ready code fix for the following problem.\n"
        "Include comments explaining each important line.\n"
        "Use correct Vulkan API or GLSL or UE5 C++ syntax.\n\n"
        f"Problem: {problem_description}"
    )
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    logger.info("generate_code_fix called", extra={"problem": problem_description[:60]})
    return response.content