import hashlib
import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urljoin, urldefrag

import scrapy
import trafilatura
from langchain_community.document_loaders import PyMuPDFLoader
from scrapy.crawler import CrawlerProcess

START_URLS = [
    "https://fiot.kpi.ua/",
    "https://ist.kpi.ua/",
    "https://comsys.kpi.ua/",
    "https://ipi.kpi.ua/",
    "https://telegra.ph/121-%D0%86nzhener%D1%96ya-programnogo-zabezpechennya-07-05",
    "https://telegra.ph/123-Kompyutern%D1%96-sistemi-ta-merezh%D1%96-07-07",
    "https://telegra.ph/126-%D0%86nformac%D1%96jn%D1%96-sistemi-ta-tehnolog%D1%96i-07-30-2",
    "https://teletype.in/@kpicampus/campus_guide"
]
RAW_PATH = Path("data")
RAW_PATH.mkdir(parents=True, exist_ok=True)
OUT_FILE = RAW_PATH / "raw_docs.jsonl"
MAX_DEPTH = 5
FOLLOW_FILETYPES = (".html", ".php", ".pdf", "/")

ALLOWED_DOMAINS = {urlparse(url).netloc for url in START_URLS}

class ContentSpider(scrapy.Spider):
    name = "content"
    start_urls = START_URLS
    custom_settings = {
        "DEPTH_LIMIT": MAX_DEPTH,
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_TIMEOUT": 30,
        "ITEM_PIPELINES": {__name__ + ".JsonlPipeline": 300},
        "LOG_LEVEL": "INFO",
    }

    seen_hashes: set[str] = set()

    def parse(self, response, **kwargs):
        url = response.url

        if url.lower().endswith(".pdf"):
            yield scrapy.Request(url, callback=self.parse_pdf, dont_filter=True)
            return

        text = trafilatura.extract(
            response.text, include_comments=False, include_tables=False
        )
        if text:
            item_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
            if item_hash not in self.seen_hashes:
                self.seen_hashes.add(item_hash)
                yield {
                    "content": text,
                    "metadata": {
                        "source": url,
                        "md5": item_hash,
                        "title": response.css("title::text").get(default="").strip(),
                        "language": response.css("html::attr(lang)").get(default="uk"),
                    },
                }

        for href in response.css("a::attr(href)").getall():
            full_url = urljoin(url, href)
            full_url, _ = urldefrag(full_url)

            parsed = urlparse(full_url)
            if (
                    parsed.netloc in ALLOWED_DOMAINS
                    and any(parsed.path.lower().endswith(ext) for ext in FOLLOW_FILETYPES)
            ):
                yield response.follow(full_url, callback=self.parse)

    def parse_pdf(self, response):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(response.body)
            tmp.flush()
            for doc in PyMuPDFLoader(tmp.name).load():
                item_hash = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
                if item_hash not in self.seen_hashes:
                    self.seen_hashes.add(item_hash)
                    doc.metadata.update({"source": response.url, "md5": item_hash})
                    yield {"content": doc.page_content, "metadata": doc.metadata}


class JsonlPipeline:
    def open_spider(self, spider):
        self.fh = OUT_FILE.open("w", encoding="utf-8")

    def close_spider(self, spider):
        self.fh.close()
        print(f"\nЗбережено {len(ContentSpider.seen_hashes)} "
              f"унікальних документів у {OUT_FILE}")

    def process_item(self, item, spider):
        self.fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        return item


if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "USER_AGENT": "KPISpider/1.0 (+https://fiot.kpi.ua)",
    })
    process.crawl(ContentSpider)
    process.start()
