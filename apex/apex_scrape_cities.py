"""
Apex Competitor City Scraper
Repo: moneyfreedomcollection/agent-visibility-template
Fires via GitHub Actions Oct 3 at 12:05 AM ET
Output: confirmed_cities_build_list.csv, all_competitor_city_pages.csv, city_summary.json
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import time
import json
import re

COMPETITORS = {
    "LexingtonLaw": "https://www.lexingtonlaw.com/sitemap.xml",
    "CreditRepair": "https://www.creditrepair.com/sitemap.xml",
    "SkyBlueCredit": "https://www.skybluecredit.com/sitemap.xml",
    "CreditSaint": "https://www.creditsaint.com/sitemap.xml",
    "TheCreditPeople": "https://www.thecreditpeople.com/sitemap.xml"
}

CITY_PATTERNS = [
    "/credit-repair/", "/dispute/", "/collections/",
    "/city/", "/location/", "/local/", "-credit-repair",
    "-dispute", "-collections", "-credit-help", "/states/", "/cities/"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_sitemap(name, url, depth=0):
    if depth > 2:
        return []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.content, "xml")
        sitemap_locs = soup.find_all("sitemap")
        if sitemap_locs:
            all_urls = []
            for s in sitemap_locs[:10]:
                loc = s.find("loc")
                if loc:
                    all_urls.extend(fetch_sitemap(name, loc.text, depth+1))
                    time.sleep(1)
            return all_urls
        return [loc.text for loc in soup.find_all("loc")]
    except Exception as e:
        print(f"  {name} error: {e}")
        return []

def extract_city(url):
    parts = url.rstrip("/").split("/")
    raw = parts[-1]
    raw = re.sub(r'-(credit-repair|dispute|help|lawyer|attorney)$', '', raw)
    return raw.replace("-", " ").title()

def extract_state(url):
    parts = url.rstrip("/").split("/")
    return parts[-2].replace("-", " ").title() if len(parts) >= 2 else ""

print("=== APEX STEP 1: COMPETITOR CITY SCRAPER ===")
all_records = []

for name, url in COMPETITORS.items():
    print(f"Scraping {name}...")
    urls = fetch_sitemap(name, url)
    city_urls = [u for u in urls if any(p in u.lower() for p in CITY_PATTERNS)]
    print(f"  {len(city_urls)} city pages found")
    for u in city_urls:
        city = extract_city(u)
        if 2 < len(city) < 50:
            all_records.append({"competitor": name, "city": city, "state": extract_state(u), "url": u})
    time.sleep(3)

df = pd.DataFrame(all_records)
df.to_csv("apex/output/all_competitor_city_pages.csv", index=False)

city_counts = Counter(df["city"])
confirmed = sorted([(c, n) for c, n in city_counts.items() if n >= 2], key=lambda x: x[1], reverse=True)
watchlist = [(c, n) for c, n in city_counts.items() if n == 1]

pd.DataFrame([{"city": c, "competitor_count": n} for c, n in confirmed]).to_csv("apex/output/confirmed_cities_build_list.csv", index=False)
pd.DataFrame([{"city": c, "competitor_count": 1} for c, _ in watchlist]).to_csv("apex/output/watchlist_cities.csv", index=False)

summary = {"confirmed_count": len(confirmed), "watchlist_count": len(watchlist), "top_cities": [c for c, _ in confirmed[:125]]}
with open("apex/output/city_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nCONFIRMED: {len(confirmed)} cities | WATCHLIST: {len(watchlist)} cities")
print("Top 10:", [c for c, _ in confirmed[:10]])
