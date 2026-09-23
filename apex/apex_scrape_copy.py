"""
Apex Competitor Copy Scraper
Scrapes H1, pain hooks, title tags, meta descriptions, CTAs from Lexington Law top city pages
Output: competitor_copy_patterns.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Load confirmed cities from Step 1 and build URL list
try:
    with open("apex/output/city_summary.json") as f:
        summary = json.load(f)
    top_cities = summary["top_cities"][:20]
except:
    top_cities = [
        "houston", "los-angeles", "miami", "atlanta", "dallas",
        "chicago", "phoenix", "charlotte", "columbus", "las-vegas",
        "new-york-city", "philadelphia", "san-antonio", "san-diego",
        "austin", "jacksonville", "orlando", "nashville", "detroit", "denver"
    ]

STATE_MAP = {
    "houston": "texas", "los-angeles": "california", "miami": "florida",
    "atlanta": "georgia", "dallas": "texas", "chicago": "illinois",
    "phoenix": "arizona", "charlotte": "north-carolina", "columbus": "ohio",
    "las-vegas": "nevada", "new-york-city": "new-york", "philadelphia": "pennsylvania",
    "san-antonio": "texas", "san-diego": "california", "austin": "texas",
    "jacksonville": "florida", "orlando": "florida", "nashville": "tennessee",
    "detroit": "michigan", "denver": "colorado"
}

print("=== APEX STEP 2: COMPETITOR COPY SCRAPER ===")
copy_data = []

for city_raw in top_cities:
    city_slug = city_raw.lower().replace(" ", "-")
    state = STATE_MAP.get(city_slug, "")
    if not state:
        continue
    url = f"https://www.lexingtonlaw.com/credit-repair/{state}/{city_slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            print(f"  {city_slug}: {r.status_code} skip")
            continue
        soup = BeautifulSoup(r.content, "html.parser")
        h1 = soup.find("h1")
        paras = soup.find_all("p")
        title = soup.find("title")
        meta = soup.find("meta", attrs={"name": "description"})
        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
        copy_data.append({
            "city": city_slug.replace("-", " ").title(),
            "state": state.replace("-", " ").title(),
            "url": url,
            "title_tag": title.get_text(strip=True) if title else "",
            "meta_description": meta["content"] if meta and meta.get("content") else "",
            "h1": h1.get_text(strip=True) if h1 else "",
            "h2s": " | ".join(h2s[:5]),
            "pain_hook_p1": paras[0].get_text(strip=True)[:300] if paras else "",
            "pain_hook_p2": paras[1].get_text(strip=True)[:300] if len(paras) > 1 else ""
        })
        print(f"  Scraped: {city_slug}")
        time.sleep(3)
    except Exception as e:
        print(f"  {city_slug} error: {e}")

df = pd.DataFrame(copy_data)
df.to_csv("apex/output/competitor_copy_patterns.csv", index=False)

# Build pattern library JSON for Blaze + Apex
patterns = {
    "h1_patterns": df["h1"].dropna().tolist(),
    "title_patterns": df["title_tag"].dropna().tolist(),
    "meta_patterns": df["meta_description"].dropna().tolist(),
    "pain_hooks": df["pain_hook_p1"].dropna().tolist(),
    "h2_patterns": df["h2s"].dropna().tolist()
}
with open("apex/output/competitor_pattern_library.json", "w") as f:
    json.dump(patterns, f, indent=2)

print(f"\nCopy scraped from {len(copy_data)} city pages")
print("Pattern library saved -> competitor_pattern_library.json")
