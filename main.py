import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Depends, Header
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import uvicorn

from config.settings import get_settings
from api.routes import router as api_router
from scrapers.news_scraper import fetch_news_articles
from scrapers.image_scraper import get_best_image
from agents.gemini_writer import generate_article
from agents.seo_optimizer import optimize_article
from utils.cta_injector import inject_cta
from publishers.supabase_publisher import publish_article
from utils.deduplicator import is_duplicate
from slugify import slugify

settings = get_settings()

def run_agent_pipeline():
    """Main pipeline execution logic."""
    logger.info("🚀 Starting Apna Blog Agent pipeline run...")
    try:
        # Step 1: Scrape
        articles = fetch_news_articles(max_raw=20, delay=settings.SCRAPE_DELAY_SECONDS)
        
        published_count = 0
        for article in articles:
            if published_count >= settings.MAX_ARTICLES_PER_RUN:
                break
                
            logger.info(f"Processing: {article['title']}")
            
            # Pre-deduplication check based on raw title slug
            raw_slug = slugify(article["title"], max_length=100)
            if is_duplicate(raw_slug):
                logger.info(f"Skipping duplicate news (raw slug): {raw_slug}")
                continue

            try:
                # Step 3: AI Generation
                generated_data = generate_article(
                    news_title=article["title"],
                    news_summary=article["summary"],
                    news_full_text=article.get("full_text", ""),
                    source_url=article["url"]
                )
                
                # Step 5: SEO Finalization
                optimized_data = optimize_article(generated_data)
                
                # Final deduplication check using optimized slug
                if is_duplicate(optimized_data["slug"]):
                    logger.info(f"Skipping duplicate article (optimized slug): {optimized_data['slug']}")
                    continue
                
                # Step 4: CTA Injection
                optimized_data["body_html"] = inject_cta(optimized_data["body_html"])
                
                # Step 2: Image Fetch
                best_image_url = get_best_image(article.get("scraped_image"), optimized_data["title"])
                
                # Step 6: Publish
                publish_result = publish_article(optimized_data, best_image_url)
                
                if publish_result.get("success"):
                    published_count += 1
                
            except Exception as e:
                logger.error(f"Error processing article '{article['title']}': {e}")
                
        logger.info(f"✅ Pipeline run complete. Published {published_count} articles.")
        
    except Exception as e:
        logger.error(f"Pipeline run failed: {e}")

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting scheduler...")
    scheduler.add_job(
        run_agent_pipeline,
        trigger=IntervalTrigger(hours=settings.AGENT_RUN_INTERVAL_HOURS),
        id="blog_agent_job",
        replace_existing=True,
        next_run_time=None # Don't run immediately on startup by default, wait for trigger
    )
    scheduler.start()
    yield
    # Shutdown
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()


app = FastAPI(title="Apna Blog Agent", lifespan=lifespan)
app.include_router(api_router, prefix="/api")

@app.post("/api/trigger")
def trigger_pipeline(background_tasks: BackgroundTasks, x_agent_key: str = Header(...)):
    if x_agent_key != settings.AGENT_SECRET_KEY:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    background_tasks.add_task(run_agent_pipeline)
    return {"message": "Pipeline run triggered in background"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=False)
