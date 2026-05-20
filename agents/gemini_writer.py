import json
import google.generativeai as genai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import get_settings

GEMINI_SYSTEM_PROMPT = """
You are the senior content writer for Apna Counsellor (apnacounsellor.in), India's leading AI-powered college admissions counselling platform for students preparing for JEE, NEET, MHT-CET, MBA, and other competitive exams.

Your writing style is:
- Authoritative but approachable — like a senior IIT/IIM mentor talking to a 17-year-old student
- Uses simple Hindi-English mix where natural (e.g., "Yahan batate hain..." in brackets as flavour ONLY, keep article 95% English)
- Never copies or paraphrases the source article — always rewrites completely in your original voice
- Student-first: always explains WHY this news matters to the student and WHAT they should do next
- Action-oriented: ends every section with a clear next step

IMPORTANT RULES:
1. NEVER copy sentences from the source. Use the source only as a factual reference.
2. Always write from the student's perspective — "What does this mean for you?"
3. Include specific numbers, dates, and official data when available
4. Include a proper FAQ section at the bottom (5 questions minimum)
5. Return ONLY valid JSON. No markdown fences. No preamble. No explanation.
"""

def build_article_prompt(news_title: str, news_summary: str, news_full_text: str, source_url: str) -> str:
    return f"""
Based on the following news, write a complete, original, SEO-optimized blog article for Apna Counsellor.

NEWS TITLE: {news_title}
NEWS SUMMARY: {news_summary}
SOURCE TEXT (use as factual reference only, DO NOT copy): 
{news_full_text[:3000]}
SOURCE URL: {source_url}

Return a single JSON object with EXACTLY these fields:

{{
  "title": "Compelling, keyword-rich blog post title (max 80 chars)",
  "subtitle": "Engaging subtitle that adds context (max 160 chars)",
  "meta_title": "SEO meta title with primary keyword (max 60 chars)",
  "meta_description": "SEO meta description summarizing the article (max 155 chars)",
  "focus_keyword": "single primary keyword phrase (e.g. 'JEE Main 2025 result date')",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "category": "one of: JEE Tips | NEET Prep | MHT-CET | MBA Prep | College Admissions | Scholarship Guides | Study Abroad | Career Advice | News & Updates",
  "exam_types": ["array of: JEE | NEET | MHT-CET | MBA | General"],
  "body_html": "FULL article HTML body — minimum 1200 words — structured as below",
  "faq_items": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ],
  "author_name": "Apna Counsellor Team",
  "author_role": "India's AI-Powered College Admissions Experts",
  "tags": ["tag1", "tag2", "tag3", "tag4"]
}}

ARTICLE STRUCTURE FOR body_html (write full HTML, not markdown):

<h2>What Happened? [News Summary in Student-Friendly Language]</h2>
<p>2-3 paragraphs explaining the news clearly</p>

<h2>Why Does This Matter for You?</h2>
<p>2-3 paragraphs on direct impact for students</p>

<h2>Key Dates & Deadlines You Must Know</h2>
<ul><li>date and what to do</li></ul>

<h2>Step-by-Step: What You Should Do Right Now</h2>
<ol><li>Actionable step</li></ol>

<h2>Expert Tips from Our Counsellors</h2>
<p>2-3 paragraphs of advice</p>

<h2>Frequently Asked Questions</h2>
(render faq_items as <h3>/<p> pairs here too)

DO NOT include the CTA block — it will be appended separately.
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def generate_article(news_title: str, news_summary: str, news_full_text: str, source_url: str) -> dict:
    """Generate article using Gemini and parse JSON response."""
    settings = get_settings()
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # Use generation config for JSON response
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json"
    )
    
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=GEMINI_SYSTEM_PROMPT,
        generation_config=generation_config
    )

    prompt = build_article_prompt(news_title, news_summary, news_full_text, source_url)
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Clean up in case model returns markdown block despite JSON mime type request
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}\nResponse: {response.text}")
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise
