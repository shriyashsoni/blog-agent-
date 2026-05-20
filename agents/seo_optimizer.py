from slugify import slugify

def optimize_article(article_data: dict) -> dict:
    """
    Perform final SEO and formatting operations on the generated article data.
    """
    # Generate slug from title
    title = article_data.get("title", "")
    slug = slugify(title, max_length=100)
    article_data["slug"] = slug
    
    # Calculate read time (avg 200 wpm)
    body_html = article_data.get("body_html", "")
    word_count = len(body_html.split())
    read_time = max(1, word_count // 200)
    article_data["read_time_minutes"] = read_time
    
    # Ensure arrays are properly formatted
    if isinstance(article_data.get("keywords"), str):
        article_data["keywords"] = [k.strip() for k in article_data["keywords"].split(",") if k.strip()]
        
    if isinstance(article_data.get("tags"), str):
        article_data["tags"] = [t.strip() for t in article_data["tags"].split(",") if t.strip()]
        
    if isinstance(article_data.get("exam_types"), str):
        article_data["exam_types"] = [e.strip() for e in article_data["exam_types"].split(",") if e.strip()]
        
    return article_data
