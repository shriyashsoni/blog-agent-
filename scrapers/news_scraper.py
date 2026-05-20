import time
import httpx
import feedparser
from datetime import datetime
from typing import Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from config.settings import RSS_FEEDS, RELEVANCE_KEYWORDS

ua = UserAgent()


def _score_article(title: str, summary: str) -> int:
    """Score an article by how many relevance keywords it contains."""
    text = f"{title} {summary}".upper()
    return sum(1 for kw in RELEVANCE_KEYWORDS if kw.upper() in text)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_full_text(url: str, delay: int = 3) -> tuple[str, Optional[str]]:
    """
    Scrape full article text and og:image from a URL.
    Returns (text_content, image_url).
    """
    time.sleep(delay)
    headers = {"User-Agent": ua.random}
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        # Extract og:image
        og_image = None
        og_tag = soup.find("meta", property="og:image")
        if og_tag and og_tag.get("content"):
            og_image = og_tag["content"]
        else:
            first_img = soup.find("img", src=True)
            if first_img:
                og_image = first_img["src"]

        # Extract body text
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:5000], og_image

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return "", None


def fetch_news_articles(max_raw: int = 20, delay: int = 3) -> list[dict]:
    """
    Parse all configured RSS feeds, score articles by relevance,
    and return the top `max_raw` unique articles with full text.
    """
    seen_urls: set[str] = set()
    raw_articles: list[dict] = []

    for feed_url in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                url = entry.get("link", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                published = entry.get("published", datetime.utcnow().isoformat())

                score = _score_article(title, summary)
                if score == 0:
                    continue

                raw_articles.append({
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "published": published,
                    "score": score,
                })
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_url}: {e}")

    # Sort by relevance score desc
    raw_articles.sort(key=lambda x: x["score"], reverse=True)
    top_articles = raw_articles[:max_raw]

    logger.info(f"Scraped {len(raw_articles)} raw articles; processing top {len(top_articles)}")

    # Enrich with full text & image
    enriched = []
    for article in top_articles:
        full_text, image_url = fetch_full_text(article["url"], delay=delay)
        article["full_text"] = full_text
        article["scraped_image"] = image_url
        enriched.append(article)

    return enriched
