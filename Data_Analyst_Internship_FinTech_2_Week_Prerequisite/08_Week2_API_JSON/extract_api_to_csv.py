import json
import csv
from urllib.request import urlopen

ENDPOINT = "https://jsonplaceholder.typicode.com/posts?userId=1"
OUTPUT = "api_posts.csv"

with urlopen(ENDPOINT, timeout=15) as response:
    data = json.loads(response.read().decode("utf-8"))

if not isinstance(data, list) or not data:
    raise ValueError("Unexpected API response")

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print(f"Saved {len(data)} records to {OUTPUT}")
