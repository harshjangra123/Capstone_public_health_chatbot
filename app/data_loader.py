# fetch + process JSON
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_API")

def fetch_dataset_by_id(resource_id: str, limit: int = 200):
    """
    Fetch dataset from data.gov.in using resource_id.

    Args:
        resource_id (str): Unique dataset ID
        limit (int): Number of records to fetch

    Returns:
        dict: JSON response OR error message
    """

    # 🔗 build URL
    url = f"https://api.data.gov.in/resource/{resource_id}"

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit
    }

    try:
        res = requests.get(url, params=params, timeout=10)

        print("STATUS:", res.status_code)  # debug

        if res.status_code != 200:
            return {"error": res.text}

        data = res.json()
        return data

    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    
    except Exception as e:
        return {"error": str(e)}
    

# data = fetch_dataset_by_id("9a362ec2-2cfc-4e08-8c74-7926b2159a69")

def json_to_text(data: dict):
    documents = []
    records = data.get("records", [])

    for item in records[:50]:

        # 1. Get main entity (state/location)
        state = item.get("states_uts") or item.get("state") or "Unknown"

        cleaned_parts = []

        for k, v in item.items():

            # 2. Skip useless fields
            if v in ["NA", "", None]:
                continue

            if k in ["_id", "index", "states_uts"]:
                continue

            # 3. Clean key
            clean_key = k.replace("_", " ")

            cleaned_parts.append(f"{clean_key} {v}")

        # 4. Skip empty rows
        if not cleaned_parts:
            continue

        # 5. Build sentence
        sentence = f"{state}: " + ", ".join(cleaned_parts)

        documents.append(sentence)

    return documents

# print("\n#####################################################################################################\n")
# print(json_to_text(data))