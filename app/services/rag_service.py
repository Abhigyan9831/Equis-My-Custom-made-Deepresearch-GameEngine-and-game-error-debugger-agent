import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.services.ingestor import get_vectorstore
from app.services.cache import make_cache_key, get_cached, set_cached
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import DiagnosisResult, ResearchSource

logger = get_logger(__name__)
settings = get_settings()

SYSTEM_PROMPT = (
    "You are a Senior Graphics Engineer expert in Vulkan and Unreal Engine 5.\n"
    "Diagnose the error using retrieved documentation context.\n\n"
    "Respond in EXACTLY this format:\n\n"
    "DIAGNOSIS: <one sentence>\n"
    "ROOT_CAUSE: <technical explanation>\n"
    "CONFIDENCE: <high | medium | low>\n"
    "CODE_FIX:\n"
    "```\n"
    "<code or config fix>\n"
    "```"
)

HUMAN_PROMPT = (
    "Documentation Context:\n"
    "{context}\n\n"
    "Error to Diagnose:\n"
    "{question}"
)


def _format_docs(docs) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


def _build_rag_chain():
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
    )
    retriever = get_vectorstore().as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.TOP_K},
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ])
    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def _parse_output(raw: str) -> dict:
    diagnosis  = re.search(r"DIAGNOSIS:(.*?)(?:ROOT_CAUSE:|$)", raw, re.S)
    root_cause = re.search(r"ROOT_CAUSE:(.*?)(?:CONFIDENCE:|$)", raw, re.S)
    confidence = re.search(r"CONFIDENCE:(.*?)(?:CODE_FIX:|$)", raw, re.S)
    code_fix   = re.search(r"CODE_FIX:(.*)", raw, re.S)
    return {
        "diagnosis":  diagnosis.group(1).strip()           if diagnosis  else raw[:300],
        "root_cause": root_cause.group(1).strip()          if root_cause else "",
        "confidence": confidence.group(1).strip().lower()  if confidence else "medium",
        "code_fix":   code_fix.group(1).strip()            if code_fix   else "No fix extracted.",
    }


async def analyze_log(log_text: str, context: str = "") -> DiagnosisResult:
    query = f"{log_text}\nContext: {context}" if context else log_text
    cache_key = make_cache_key(query)

    # 1. Cache check
    cached = get_cached(cache_key)
    if cached:
        cached["cached"] = True
        return DiagnosisResult(**cached)

    # 2. Retrieve + generate
    chain, retriever = _build_rag_chain()
    source_docs = await retriever.aget_relevant_documents(query)
    raw_output  = await chain.ainvoke(query)

    # 3. Parse
    parsed = _parse_output(raw_output)
    parsed["sources"] = [
        ResearchSource(
            title=d.metadata.get("source_type", "doc"),
            url=d.metadata.get("url", d.metadata.get("source", "")),
            snippet=d.page_content[:200],
        ).model_dump()
        for d in source_docs
    ]
    parsed["cached"] = False

    # 4. Cache + return
    set_cached(cache_key, parsed)
    return DiagnosisResult(**parsed)