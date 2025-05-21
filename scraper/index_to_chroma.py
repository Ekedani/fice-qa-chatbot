import json, gzip, os
from pathlib import Path
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

RAW_FILE = Path("data/raw_docs.jsonl")
CHROMA_DIR = "./chroma_db"
COLL_NAME = "fice_docs"

docs = []
with open(RAW_FILE, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        docs.append(Document(page_content=r["content"], metadata=r["metadata"]))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"}
)

db = Chroma(
    collection_name=COLL_NAME,
    persist_directory=CHROMA_DIR,
    embedding_function=emb
)

db.add_documents(chunks)
db.persist()
print(f"Додано {len(chunks)} чанків у Chroma «{COLL_NAME}»")
