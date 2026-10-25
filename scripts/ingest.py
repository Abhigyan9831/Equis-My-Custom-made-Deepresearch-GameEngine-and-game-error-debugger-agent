
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestor import ingest_documents
from app.core.logging import setup_logging

setup_logging()

if __name__ == "__main__":
    print("Starting ingestion...")
    count = ingest_documents()
    print(f"Done {count} chunks ingested into Pinecone.")