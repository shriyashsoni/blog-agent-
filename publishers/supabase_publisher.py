from datetime import datetime
from loguru import logger
from config.settings import get_settings
from utils.deduplicator import get_supabase_client, is_duplicate

def publish_article(article_data: dict, image_url: str = None) -> dict:
    """
    Inserts the finalized article into the Supabase 'blogs' table.
    """
    settings = get_settings()
    supabase = get_supabase_client()
    
    slug = article_data.get("slug")
    if not slug:
        logger.error("Missing slug in article data, cannot publish.")
        return {"success": False, "error": "Missing slug"}
        
    if is_duplicate(slug):
        logger.info(f"DUPLICATE SKIPPED: Article with slug '{slug}' already exists.")
        return {"success": False, "error": "Duplicate slug", "skipped": True}

    status = "published" if settings.AUTO_PUBLISH else "draft"
    published_at = datetime.utcnow().isoformat() if settings.AUTO_PUBLISH else None

    # Construct payload matching the Supabase table schema
    payload = {
        "title": article_data.get("title"),
        "slug": slug,
        "subtitle": article_data.get("subtitle"),
        "body_html": article_data.get("body_html"),
        "category": article_data.get("category"),
        "tags": article_data.get("tags", []),
        "exam_types": article_data.get("exam_types", []),
        "author_name": article_data.get("author_name", "Apna Counsellor Team"),
        "author_role": article_data.get("author_role", "Admission Expert"),
        "cover_image_url": image_url,
        "og_image_url": image_url,
        "meta_title": article_data.get("meta_title"),
        "meta_description": article_data.get("meta_description"),
        "focus_keyword": article_data.get("focus_keyword"),
        "keywords": article_data.get("keywords", []),
        "schema_type": "Article",
        "faq_items": article_data.get("faq_items", []),
        "read_time_minutes": article_data.get("read_time_minutes", 5),
        "status": status,
        "published_at": published_at,
        "is_featured": False,
        "allow_comments": True,
        "newsletter_push": False,
        "views": 0
    }

    try:
        result = supabase.table("blogs").insert(payload).execute()
        
        if result.data:
            inserted_id = result.data[0].get("id")
            logger.info(f"✅ PUBLISHED: '{payload['title']}' (ID: {inserted_id})")
            return {"success": True, "id": inserted_id, "slug": slug}
        else:
            logger.error(f"Failed to insert article: No data returned.")
            return {"success": False, "error": "No data returned from insert"}
            
    except Exception as e:
        logger.error(f"Error publishing article '{slug}': {e}")
        return {"success": False, "error": str(e)}
