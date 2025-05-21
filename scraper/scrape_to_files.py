import trafilatura, requests, json, hashlib, os, tempfile
from pathlib import Path
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.docstore.document import Document

RAW_PATH = Path("data")
RAW_PATH.mkdir(exist_ok=True, parents=True)
OUT_FILE = RAW_PATH / "raw_docs.jsonl"

urls = [
    "https://fiot.kpi.ua/",
    "https://fiot.kpi.ua/?page_id=60",
    "https://ist.kpi.ua/",
    "https://comsys.kpi.ua/",
]

docs: list[Document] = []
for url in tqdm(urls, desc="Fetching"):
    try:
        if url.lower().endswith(".pdf"):
            data = requests.get(url, timeout=30).content
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(data);
                tmp.flush()
                docs.extend(PyMuPDFLoader(tmp.name).load())
        else:
            html = trafilatura.fetch_url(url)
            text = trafilatura.extract(html, include_comments=False, include_tables=False)
            if text:
                docs.append(Document(page_content=text, metadata={"source": url}))
    except Exception as e:
        print(f"[WARN] {url}: {e}")

seen: set[str] = set()
unique_docs = []
for d in docs:
    h = hashlib.md5(d.page_content.encode("utf-8")).hexdigest()
    if h not in seen:
        seen.add(h)
        d.metadata["md5"] = h
        unique_docs.append(d)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for d in unique_docs:
        record = {"content": d.page_content, "metadata": d.metadata}
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Збережено {len(unique_docs)} унікальних документів у {OUT_FILE}")
