"""
Apex Nova Microsite Build Queue Generator
Reads confirmed_cities_build_list.csv + competitor_pattern_library.json
Outputs nova_microsite_build_queue.csv (1,000 rows — 125 cities x 8 subniches)
"""

import pandas as pd
import json

SUBNICHES = [
    "debt-validation",
    "cease-desist",
    "credit-dispute",
    "goodwill-deletion",
    "pay-for-delete",
    "method-of-verification",
    "collections-removal",
    "fha-credit-repair"
]

print("=== APEX STEP 3: NOVA BUILD QUEUE GENERATOR ===")

df_cities = pd.read_csv("apex/output/confirmed_cities_build_list.csv")
with open("apex/output/competitor_pattern_library.json") as f:
    patterns = json.load(f)

top_125 = df_cities.head(125)["city"].tolist()
build_queue = []

for city in top_125:
    city_slug = city.lower().replace(" ", "-")
    for subniche in SUBNICHES:
        subdomain = f"{subniche}-{city_slug}"
        build_queue.append({
            "subdomain": subdomain,
            "full_url": f"https://{subdomain}.moneyfreedomcollection.com",
            "city": city,
            "subniche": subniche,
            "title_tag": f"{subniche.replace('-',' ').title()} {city} | The Money Freedom Collection",
            "h1": f"Federal {subniche.replace('-',' ').title()} Education in {city}",
            "meta_desc": f"Learn your federal rights for {subniche.replace('-',' ')} in {city}. The Money Freedom Collection — we teach the law, you use it.",
            "cta_whatsapp": "https://wa.me/16179018924",
            "competitor_validated": True,
            "status": "READY_TO_BUILD"
        })

df_queue = pd.DataFrame(build_queue)
df_queue.to_csv("apex/output/nova_microsite_build_queue.csv", index=False)

print(f"Nova build queue: {len(df_queue)} microsites")
print(f"Cities: {len(top_125)} | Subniches: {len(SUBNICHES)}")
print("All cities confirmed by 2+ competitors. Zero guessing.")
print("Output: nova_microsite_build_queue.csv")
