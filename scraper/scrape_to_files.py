import hashlib
import json
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urldefrag

import scrapy
import trafilatura
from langchain_community.document_loaders import PyMuPDFLoader
from scrapy.crawler import CrawlerProcess

START_URLS = [
    "https://fiot.kpi.ua/",
    "https://ist.kpi.ua/",
    "https://comsys.kpi.ua/",
    "https://ipi.kpi.ua/",
    "https://pk.kpi.ua/"
]
RAW_PATH = Path("data")
RAW_PATH.mkdir(parents=True, exist_ok=True)
OUT_FILE = RAW_PATH / "raw_docs.jsonl"
MAX_DEPTH = 2
FOLLOW_FILETYPES = (".html", ".php", ".pdf", "/")


class ContentSpider(scrapy.Spider):
    name = "content"
    start_urls = START_URLS
    allowed_domains = [url.split("/")[2] for url in START_URLS]
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
            full = urljoin(url, href)
            full, _ = urldefrag(full)
            if (
                    full.startswith(tuple(self.start_urls))
                    and full.lower().endswith(FOLLOW_FILETYPES)
            ):
                yield response.follow(full, callback=self.parse)

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
