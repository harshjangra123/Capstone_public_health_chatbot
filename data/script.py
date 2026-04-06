import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_API")

BASE_URL = "https://api.data.gov.in/resource/{}"

# Your target folder
SAVE_FOLDER = r"C:\Users\harsh\Desktop\capstone_implementation\data"


def fetch_dataset(resource_id, limit=1000):
    url = BASE_URL.format(resource_id)

    params = {
        "api-key": API_KEY,
        "format": "csv",
        "limit": limit
    }

    try:
        res = requests.get(url, params=params, timeout=15)

        print(f"STATUS ({resource_id}):", res.status_code)

        if res.status_code != 200:
            print("❌ Failed:", res.text)
            return None

        return res.text  # raw CSV text

    except Exception as e:
        print("❌ Error:", str(e))
        return None


def save_csv(csv_text, file_name):
    if not csv_text:
        print("⚠️ Empty response")
        return

    # Sometimes API returns HTML instead of CSV
    if "html" in csv_text.lower():
        print("⚠️ Invalid response (HTML), skipping...")
        return

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    file_path = os.path.join(SAVE_FOLDER, f"{file_name}.csv")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_text)

    print(f"✅ Saved: {file_name}.csv")


def clean_filename(title):
    return (
        title.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
        .replace("/", "_")   # 🔥 THIS FIX
        .replace("\\", "_")  # 🔥 extra safety
    )


def download_all():
    registry_path = r"C:\Users\harsh\Desktop\capstone_implementation\data\registry.json"

    with open(registry_path, "r") as f:
        datasets = json.load(f)

    for dataset in datasets:
        title = dataset["title"]
        resource_id = dataset["resource_id"]

        print(f"\n📥 Downloading: {title}")

        csv_text = fetch_dataset(resource_id)

        if not csv_text:
            continue

        file_name = clean_filename(title)

        save_csv(csv_text, file_name)


if __name__ == "__main__":
    download_all()