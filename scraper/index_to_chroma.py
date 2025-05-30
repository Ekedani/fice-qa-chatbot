import json
from pathlib import Path

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

RAW_FILE = Path("data/raw_docs.jsonl")
COLL_NAME = "fice_docs"
PERSIST_DIR = "../chroma"
BATCH_SIZE = 5000

docs: list[Document] = []
with RAW_FILE.open(encoding="utf-8") as fh:
    for line in fh:
        rec = json.loads(line)
        docs.append(Document(page_content=rec["content"], metadata=rec["metadata"]))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

vectordb = Chroma(
    collection_name=COLL_NAME,
    persist_directory=PERSIST_DIR,
    embedding_function=emb,
)

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i + BATCH_SIZE]
    vectordb.add_documents(batch)

vectordb.persist()

print(f"Додано {len(chunks)} чанків у Chroma «{COLL_NAME}» (директорія: {PERSIST_DIR})")