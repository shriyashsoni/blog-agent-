import httpx
from typing import Optional
from loguru import logger
from config.settings import get_settings

def fetch_google_image(query: str) -> Optional[str]:
    """Fetch an image URL using Google Custom Search API."""
    settings = get_settings()
    if not settings.GOOGLE_CSE_API_KEY or not settings.GOOGLE_CSE_ID:
        logger.warning("Google CSE API keys missing; skipping image search.")
        return None

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query + " India students exam",
        "cx": settings.GOOGLE_CSE_ID,
        "key": settings.GOOGLE_CSE_API_KEY,
        "searchType": "image",
        "num": 3,
        "imgSize": "large",
        "safe": "active",
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            items = data.get("items", [])
            for item in items:
                link = item.get("link")
                if link and (link.endswith(".jpg") or link.endswith(".png") or link.endswith(".jpeg")):
                    return link
            
            if items:
                return items[0].get("link")
                
    except Exception as e:
        logger.error(f"Image search failed for query '{query}': {e}")
        
    return None

def get_best_image(scraped_image: Optional[str], article_title: str) -> Optional[str]:
    """Prefer scraped image, fallback to Google Custom Search."""
    if scraped_image and scraped_image.startswith("http"):
        return scraped_image
    
    return fetch_google_image(article_title)
