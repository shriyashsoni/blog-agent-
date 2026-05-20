from fastapi import APIRouter, Depends, HTTPException, Header
from loguru import logger
from utils.deduplicator import get_supabase_client
from config.settings import get_settings

router = APIRouter()

def verify_agent_key(x_agent_key: str = Header(...)):
    settings = get_settings()
    if x_agent_key != settings.AGENT_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_agent_key

@router.get("/")
def read_root():
    return {"message": "Apna Counsellor Blog Agent is running."}

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/articles")
def get_recent_articles():
    """Fetch the latest 20 published articles."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("blogs").select("id, title, slug, status, published_at").order("created_at", desc=True).limit(20).execute()
        return {"articles": result.data}
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/articles/{slug}", dependencies=[Depends(verify_agent_key)])
def unpublish_article(slug: str):
    """Set an article to draft."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("blogs").update({"status": "draft"}).eq("slug", slug).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Article not found")
        return {"success": True, "message": f"Article '{slug}' set to draft"}
    except Exception as e:
        logger.error(f"Error unpublishing article '{slug}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
