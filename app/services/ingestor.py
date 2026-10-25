from langchain_community.document_loaders import (
    PyPDFLoader,
    DirectoryLoader,
    TextLoader,
    AsyncHtmlLoader,
)
from langchain_community.document_transformers import Html2TextTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

EMBEDDING_DIM = 768  # Gemini text-embedding-004 output dimension


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Gemini cloud embeddings — no local model needed."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBED_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        output_dimensionality=384, 
    )


def _ensure_index() -> None:
    """Create Pinecone index if it does not exist."""
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]
    if settings.PINECONE_INDEX_NAME not in existing:
        logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )


def get_vectorstore() -> PineconeVectorStore:
    """Return LangChain Pinecone vectorstore using Gemini embeddings."""
    _ensure_index()
    return PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=get_embeddings(),
        pinecone_api_key=settings.PINECONE_API_KEY,
    )


def _load_urls(urls: list[str], source_type: str) -> list[Document]:
    """
    Load URLs using AsyncHtmlLoader + Html2TextTransformer.
    No local model needed — pure HTTP fetch + html2text parsing.
    Follows LangChain docs: https://python.langchain.com/docs/integrations/document_loaders/async_html/
    """
    if not urls:
        return []

    try:
        # Step 1: Fetch all URLs async in parallel
        loader = AsyncHtmlLoader(urls)
        raw_docs = loader.load()

        # Step 2: Strip HTML tags -> clean plain text
        transformer = Html2TextTransformer()
        clean_docs = transformer.transform_documents(raw_docs)

        # Step 3: Tag metadata for retrieval filtering
        for doc in clean_docs:
            doc.metadata["source_type"] = source_type
            doc.metadata["url"] = doc.metadata.get("source", "")

        logger.info(f"Loaded {len(clean_docs)} docs from {source_type} URLs")
        return list(clean_docs)

    except Exception as e:
        logger.warning(f"URL loading failed for {source_type}: {e}")
        return []


def ingest_documents() -> int:
    """
    Load docs from:
    - data/docs/ folder (PDF, MD, TXT)
    - Vulkan spec URLs (AsyncHtmlLoader)
    - UE5 docs URLs (AsyncHtmlLoader)
    Embed via Gemini text-embedding-004 -> store in Pinecone.
    """
    docs = []

    # ── Local files ────────────────────────────────────────────────────────────
    for glob, cls in [
        ("**/*.pdf", PyPDFLoader),
        ("**/*.md",  TextLoader),
        ("**/*.txt", TextLoader),
    ]:
        try:
            loaded = DirectoryLoader(
                settings.DOCS_PATH,
                glob=glob,
                loader_cls=cls,
                show_progress=True,
            ).load()
            docs.extend(loaded)
            logger.info(f"Loaded {len(loaded)} local files ({glob})")
        except Exception as e:
            logger.warning(f"Local loader skipped ({glob}): {e}")

    # ── Vulkan URLs ────────────────────────────────────────────────────────────
    vulkan_docs = _load_urls(settings.VULKAN_URLS, "vulkan")
    docs.extend(vulkan_docs)

    # ── UE5 URLs ───────────────────────────────────────────────────────────────
    ue5_docs = _load_urls(settings.UE5_URLS, "ue5")
    docs.extend(ue5_docs)

    if not docs:
        logger.warning("No documents loaded — check data/docs/ and URLs")
        return 0

    # ── Split into chunks ──────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Total chunks to embed: {len(chunks)}")

    # ── Embed via Gemini + upsert to Pinecone ──────────────────────────────────
    import json
    import os
    import time

    checkpoint_file = os.path.join(settings.DOCS_PATH, ".ingest_checkpoint.json")
    start_index = 0
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, "r") as f:
                data = json.load(f)
                start_index = data.get("completed_chunks", 0)
                logger.info(f"Resuming ingestion from chunk {start_index}/{len(chunks)}")
        except Exception:
            start_index = 0

    if start_index >= len(chunks):
        logger.info(f"All {len(chunks)} chunks are already ingested.")
        return len(chunks)

    vectorstore = get_vectorstore()
    batch_size = 50  # chunks per batch to stay under Gemini free tier quota (100 RPM)
    for i in range(start_index, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        for attempt in range(5):
            try:
                vectorstore.add_documents(batch)
                break
            except Exception as e:
                err_str = str(e)
                if any(k in err_str for k in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
                    wait = 15 * (attempt + 1)
                    logger.warning(f"Transient error ({err_str[:40]}...). Retrying in {wait}s... (attempt {attempt + 1}/5)")
                    time.sleep(wait)
                else:
                    raise
        # Save checkpoint after each successfully ingested batch
        completed = min(i + batch_size, len(chunks))
        try:
            os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
            with open(checkpoint_file, "w") as f:
                json.dump({"completed_chunks": completed, "total_chunks": len(chunks)}, f)
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")

        time.sleep(1.5)

    logger.info(f"Ingested {len(chunks)} chunks into Pinecone")
    return len(chunks)