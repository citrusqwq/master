import os
import requests
from utils.cache import load_cache, save_cache

API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
CSE_ID = os.getenv("CSE_ID")
GOOGLE_SEARCH_CACHE_NAME = "google_search"
GOOGLE_DISTANCE_MATRIX_CACHE_NAME = "google_distance_matrix"


def google_search(query: str, num: int = 5):
    cache = load_cache(GOOGLE_SEARCH_CACHE_NAME)
    if query in cache:
        print(f"✅ Loading cache for: {query}")
        return cache[query]

    print(f"🔍 Searching Google for: {query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": API_KEY, "cx": CSE_ID, "num": num}

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        results.append(
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
            }
        )

    cache[query] = results
    save_cache(GOOGLE_SEARCH_CACHE_NAME, cache)

    return results


def get_travel_distance_and_duration(origin: str, destination: str, mode: str):
    # Normalize key (origin|destination|mode)
    key = f"{origin.strip().lower()}|{destination.strip().lower()}|{mode.lower()}"

    # Load cache
    cache = load_cache(GOOGLE_DISTANCE_MATRIX_CACHE_NAME)

    # If in cache, use cached response
    if key in cache:
        print(f"✅ Loading cache for: {key}")
        data = cache[key]
    else:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": API_KEY,
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "OK":
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                cache[key] = data
                save_cache(GOOGLE_DISTANCE_MATRIX_CACHE_NAME, cache)
            else:
                return f"Element error: {element['status']}"
        else:
            return f"API error: {data['status']}"

    element = data["rows"][0]["elements"][0]
    result = {
        "distance": element["distance"]["text"],
        "duration": element["duration"]["text"],
        "mode": mode,
    }

    return result
