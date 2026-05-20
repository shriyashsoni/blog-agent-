from supabase import create_client, Client
from config.settings import get_settings
from loguru import logger
import traceback

def get_supabase_client() -> Client:
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def is_duplicate(slug: str) -> bool:
    """Check if an article with this slug already exists in Supabase."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("blogs").select("id").eq("slug", slug).limit(1).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error checking duplicate slug '{slug}': {e}")
        return False # Assume not duplicate on error to allow retry, or fail safe.

