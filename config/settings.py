from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini AI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "blog-covers"

    # Google Custom Search (images)
    GOOGLE_CSE_API_KEY: Optional[str] = None
    GOOGLE_CSE_ID: Optional[str] = None

    # Community Links
    WHATSAPP_LINK: str = "https://chat.whatsapp.com/your_link"
    TELEGRAM_CHANNEL: str = "https://t.me/your_channel"
    TELEGRAM_GROUP: str = "https://t.me/your_group"
    WEBSITE_URL: str = "https://www.apnacounsellor.in"
    INSTAGRAM_URL: str = "https://instagram.com/apnacounsellor"
    YOUTUBE_URL: str = "https://youtube.com/@apnacounsellor"
    TWITTER_URL: str = "https://twitter.com/apnacounsellor"

    # Agent Behaviour
    AGENT_RUN_INTERVAL_HOURS: int = 6
    MAX_ARTICLES_PER_RUN: int = 5
    AUTO_PUBLISH: bool = True
    SCRAPE_DELAY_SECONDS: int = 3
    LOG_LEVEL: str = "INFO"

    # API Auth
    PORT: int = 8000
    AGENT_SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


RSS_FEEDS = [
    "https://news.google.com/rss/search?q=JEE+Main+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=NEET+India+students&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=MHT+CET+counselling&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=JOSAA+counselling+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=NTA+exam+notification+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=CAT+MBA+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=college+admissions+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=scholarship+India+students&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=IIT+admission+cutoff+India&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=study+abroad+IELTS+Indian+students&hl=en-IN&gl=IN&ceid=IN:en",
]

RELEVANCE_KEYWORDS = [
    "JEE", "NEET", "MHT-CET", "JOSAA", "NTA", "CAT", "MBA",
    "counselling", "counseling", "cutoff", "rank", "admission",
    "IIT", "NIT", "IIIT", "MBBS", "engineering", "medical",
    "college", "university", "scholarship", "seat allotment",
    "answer key", "result", "merit list", "round", "COEP", "VJTI",
]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
