import json
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from server.services.vectorstore import get_vectordb

RAW_FILE = Path("data/raw_docs.jsonl")
COLL_NAME = "fice_docs"

docs = []
with open(RAW_FILE, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        docs.append(Document(page_content=r["content"], metadata=r["metadata"]))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

db = get_vectordb()
db.add_documents(chunks)
db.persist()
print(f"Додано {len(chunks)} чанків у Chroma «{COLL_NAME}»")
