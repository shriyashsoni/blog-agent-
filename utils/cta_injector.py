from config.settings import get_settings

def build_cta_block() -> str:
    settings = get_settings()
    return f"""
<hr/>
<div class="apna-counsellor-cta">

  <h2>🎯 Need Personalised Guidance for Your Admission?</h2>
  <p>
    Thousands of students across India trust <strong>Apna Counsellor</strong> for expert, 
    AI-powered college admissions counselling. Don't navigate this alone — 
    <a href="{settings.WEBSITE_URL}/courses" target="_blank">explore our counselling programs</a> 
    and get matched with a mentor who cracked the same exam.
  </p>

  <h3>📲 Join Our Free Student Communities</h3>
  <ul>
    <li>
      <strong>WhatsApp Group</strong> — Daily exam updates, rank predictors, and peer support<br/>
      👉 <a href="{settings.WHATSAPP_LINK}" target="_blank">Join Our WhatsApp Group</a>
    </li>
    <li>
      <strong>Telegram Channel</strong> — Instant notifications for results, answer keys, cutoffs<br/>
      👉 <a href="{settings.TELEGRAM_CHANNEL}" target="_blank">Join Telegram Channel</a>
    </li>
    <li>
      <strong>Telegram Discussion Group</strong> — Ask doubts, share rank cards, get counselling tips<br/>
      👉 <a href="{settings.TELEGRAM_GROUP}" target="_blank">Join Telegram Group</a>
    </li>
  </ul>

  <h3>📌 Follow Us for Daily Updates</h3>
  <ul>
    <li>Instagram: <a href="{settings.INSTAGRAM_URL}" target="_blank">@apnacounsellor</a></li>
    <li>YouTube: <a href="{settings.YOUTUBE_URL}" target="_blank">Apna Counsellor</a></li>
    <li>Twitter/X: <a href="{settings.TWITTER_URL}" target="_blank">@apnacounsellor</a></li>
  </ul>

  <h3>💬 Have Questions?</h3>
  <p>
    Drop your doubts in the comments below, or 
    <a href="{settings.WEBSITE_URL}/mentorship" target="_blank">book a free discovery call</a> 
    with one of our expert mentors. We respond to every comment. 🙌
  </p>

  <p><em>
    ⭐ If this article helped you, share it with one friend who needs it — 
    you might just change their college journey.
  </em></p>

</div>
<hr/>
"""

def inject_cta(body_html: str) -> str:
    """Appends the CTA block to the article body."""
    cta_block = build_cta_block()
    return f"{body_html}\n\n{cta_block}"
