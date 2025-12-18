import asyncio
import aiohttp
import csv
import json
from typing import List, Dict, Any

BASE_URL = "https://unstop.com/api/public/opportunity/search-result"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://unstop.com/competitions?oppstatus=open"
}
PER_PAGE = 50  # Fetch more per request to reduce total requests


async def fetch_page(session: aiohttp.ClientSession, page: int) -> Dict[str, Any]:
    """Fetch a single page of competitions."""
    params = {
        "opportunity": "competitions",
        "page": page,
        "per_page": PER_PAGE,
        "oppstatus": "open"
    }

    async with session.get(BASE_URL, params=params, headers=HEADERS) as response:
        data = await response.json()
        print(f"Fetched page {page} - Status: {response.status}")
        return data


async def get_total_pages(session: aiohttp.ClientSession) -> int:
    """Get total number of pages available."""
    params = {
        "opportunity": "competitions",
        "page": 1,
        "per_page": PER_PAGE,
        "oppstatus": "open"
    }

    async with session.get(BASE_URL, params=params, headers=HEADERS) as response:
        data = await response.json()
        total = data.get("data", {}).get("total", 0)
        total_pages = (total + PER_PAGE - 1) // PER_PAGE
        print(f"Total competitions: {total}, Total pages: {total_pages}")
        return total_pages, data


async def fetch_all_competitions() -> List[Dict[str, Any]]:
    """Fetch all competitions concurrently."""
    all_competitions = []

    async with aiohttp.ClientSession() as session:
        # First get total pages and first page data
        total_pages, first_page_data = await get_total_pages(session)

        # Extract first page competitions
        first_page_competitions = first_page_data.get("data", {}).get("data", [])
        all_competitions.extend(first_page_competitions)

        # Fetch remaining pages concurrently
        if total_pages > 1:
            tasks = [fetch_page(session, page) for page in range(2, total_pages + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    print(f"Error fetching page: {result}")
                    continue
                competitions = result.get("data", {}).get("data", [])
                all_competitions.extend(competitions)

    return all_competitions


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionaries."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))
    return dict(items)


def save_to_csv(competitions: List[Dict[str, Any]], filename: str = "competitions.csv"):
    """Save competitions to CSV file."""
    if not competitions:
        print("No competitions to save")
        return

    # Flatten all competitions
    flattened = [flatten_dict(c) for c in competitions]

    # Get all unique keys
    all_keys = set()
    for comp in flattened:
        all_keys.update(comp.keys())

    # Sort keys for consistent column order, prioritizing important fields
    priority_fields = ['id', 'title', 'seo_url', 'public_url', 'type', 'subtype',
                       'status', 'registerCount', 'viewsCount', 'end_date']
    sorted_keys = [k for k in priority_fields if k in all_keys]
    sorted_keys += sorted([k for k in all_keys if k not in priority_fields])

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(flattened)

    print(f"Saved {len(competitions)} competitions to {filename}")


def save_to_json(competitions: List[Dict[str, Any]], filename: str = "competitions.json"):
    """Save raw competitions data to JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(competitions, f, indent=2, ensure_ascii=False)
    print(f"Saved raw data to {filename}")


async def main():
    print("Starting async scrape of unstop.com competitions...")
    print("-" * 50)

    competitions = await fetch_all_competitions()

    print("-" * 50)
    print(f"Total competitions fetched: {len(competitions)}")

    # Save to both CSV and JSON
    save_to_csv(competitions)
    save_to_json(competitions)

    # Print sample of fields found
    if competitions:
        sample = competitions[0]
        print(f"\nSample competition: {sample.get('title', 'N/A')}")
        print(f"Fields available: {len(sample.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
