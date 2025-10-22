import re

def route(cmd: str) -> dict:
    s = cmd.lower()
    m = "ai_product_build"
    p = {"run_id": f"RUN_PROMPT"}
    if (m_amt:=re.findall(r'(\d{3,})\s*(sek|kr|\$|eur)?', s)):
        p["amount"] = float(m_amt[0][0])
    if "usa" in s or "us" in s: p["jurisdiction"]="US"
    elif "eu" in s: p["jurisdiction"]="EU"
    else: p["jurisdiction"]="SE"
    if any(k in s for k in ["produkt","sälj","shop","etsy","lemon","butik"]): m="ai_product_build"
    if any(k in s for k in ["sammanfatta","pdf","rapport"]): m="search_summarize"
    if any(k in s for k in ["seo","affiliate","blogg"]): m="seo_affiliate"
    if any(k in s for k in ["bild","gallery","poster","wallpaper"]): m="gen_image_pack"
    return {"goal": cmd.strip(), "mission_code": m, "params": p}
