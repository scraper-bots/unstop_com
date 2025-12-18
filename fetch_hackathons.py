import requests
import csv
import json

url = "https://unstop.com/api/public/opportunity/search-result"
params = {
    "opportunity": "hackathons",
    "page": 1,
    "per_page": 100,  # Get more results
    "oppstatus": "open"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://unstop.com/hackathons?oppstatus=open"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

# Save raw JSON for reference
with open("hackathons_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Status: {response.status_code}")
print(f"Keys in response: {data.keys() if isinstance(data, dict) else 'list'}")

# Extract hackathons data
hackathons = []
if isinstance(data, dict):
    if "data" in data:
        if "data" in data["data"]:
            hackathons = data["data"]["data"]
        else:
            hackathons = data["data"]
    print(f"Found {len(hackathons)} hackathons")

# Determine all unique fields
all_fields = set()
for h in hackathons:
    if isinstance(h, dict):
        all_fields.update(h.keys())

print(f"Fields found: {sorted(all_fields)}")

# Write to CSV
if hackathons:
    # Define key fields to extract
    key_fields = [
        "id", "title", "seo_url", "type", "organisation_name",
        "start_date", "end_date", "regnRequirements_end_date",
        "registerCount", "viewsCount", "festival_name",
        "public_url", "banner_mobile", "banner_desktop"
    ]

    # Use all available fields
    fieldnames = sorted(all_fields)

    with open("hackathons.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for h in hackathons:
            if isinstance(h, dict):
                # Flatten nested objects to strings
                row = {}
                for k, v in h.items():
                    if isinstance(v, (dict, list)):
                        row[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        row[k] = v
                writer.writerow(row)

    print(f"Saved {len(hackathons)} hackathons to hackathons.csv")
else:
    print("No hackathons found in response")
