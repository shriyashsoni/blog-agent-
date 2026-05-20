def map_category(keywords: list[str]) -> str:
    """Fallback category mapping logic if Gemini doesn't provide a good one."""
    text = " ".join(keywords).lower()
    
    if "jee" in text or "iit" in text or "nit" in text or "josaa" in text or "csab" in text:
        return "JEE Tips"
    elif "neet" in text or "mbbs" in text or "medical" in text or "mcc" in text:
        return "NEET Prep"
    elif "mht" in text or "cet" in text or "coep" in text or "vjti" in text:
        return "MHT-CET"
    elif "mba" in text or "cat" in text or "iim" in text:
        return "MBA Prep"
    elif "scholarship" in text:
        return "Scholarship Guides"
    elif "abroad" in text or "ielts" in text or "gre" in text:
        return "Study Abroad"
    else:
        return "News & Updates"
