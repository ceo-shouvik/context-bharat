"""Web crawler using Crawl4AI — handles JS-rendered pages, auth portals, and doc sites."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RawDocument:
    url: str
    content: str
    content_type: str  # "markdown" | "html" | "pdf"
    metadata: dict = field(default_factory=dict)
    library_id: str = ""


class WebCrawler:
    """
    Crawl4AI-based web crawler.
    Handles: JS SPAs (ABDM sandbox), auth portals, regular doc sites.
    Outputs: clean LLM-ready Markdown.
    """

    def __init__(self, rate_limit_per_sec: float = 2.0):
        self.rate_limit = rate_limit_per_sec

    async def crawl(self, urls: list[str], config: dict) -> list[RawDocument]:
        """
        Crawl a list of URLs and return RawDocuments.

        Config keys:
          crawl_depth: int — how many link levels to follow
          css_selector: str — focus on specific content area
          auth: dict — optional session auth config
        """
        try:
            from crawl4ai import AsyncWebCrawler as C4AI
            from crawl4ai import BrowserConfig, CrawlerRunConfig
        except ImportError:
            logger.error("crawl4ai not installed — run: pip install crawl4ai")
            raise

        browser_cfg = BrowserConfig(
            headless=True,
            browser_type="chromium",
            verbose=False,
        )

        run_cfg = CrawlerRunConfig(
            word_count_threshold=50,
            exclude_external_links=True,
            exclude_social_media_links=True,
            remove_overlay_elements=True,
            process_iframes=False,
            css_selector=config.get("css_selector", "main, article, .content, .docs-content"),
        )

        docs = []
        async with C4AI(config=browser_cfg) as crawler:
            for url in urls:
                try:
                    result = await crawler.arun(url=url, config=run_cfg)
                    if result.success and result.markdown:
                        docs.append(RawDocument(
                            url=url,
                            content=result.markdown,
                            content_type="markdown",
                            metadata={
                                "title": result.metadata.get("title", ""),
                                "crawled_links": len(result.links.get("internal", [])),
                            },
                            library_id=config.get("library_id", ""),
                        ))
                        logger.info(f"Crawled: {url} ({len(result.markdown)} chars)")

                        # Follow internal links if depth > 1
                        depth = config.get("crawl_depth", 1)
                        if depth > 1:
                            sub_urls = [
                                link["href"]
                                for link in result.links.get("internal", [])
                                if link.get("href", "").startswith("http")
                            ][:50]  # Cap to 50 sub-pages
                            if sub_urls:
                                sub_cfg = {**config, "crawl_depth": depth - 1}
                                sub_docs = await self.crawl(sub_urls, sub_cfg)
                                docs.extend(sub_docs)
                except Exception as e:
                    logger.warning(f"Failed to crawl {url}: {e}")

        return docs
