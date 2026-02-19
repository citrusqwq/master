import requests
from utils.cache import load_cache, save_cache

email = ""
SEARCH_PLACE_CACHE_NAME = "osm_search_place"
OPENING_HOUR_CACHE_NAME = "osm_place_tags"


# ---------- Search Place via Nominatim ----------
def search_place(query: str):
    cache = load_cache(SEARCH_PLACE_CACHE_NAME)

    if query in cache:
        print(f"... Loading cache for: {query}")
        return cache[query]

    print(f"🔍 Searching OpenStreetMap for: {query}")
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "email": email,
    }
    response = requests.get(url, params=params)
    data = response.json()

    cache[query] = data
    save_cache(SEARCH_PLACE_CACHE_NAME, cache)

    return data


# ---------- Get Opening Hours via Overpass ----------
def get_opening_hours(osm_type: str, osm_id: str):
    # Create a unique key to cache based on type and ID
    key = f"{osm_type}_{osm_id}"

    cache = load_cache(OPENING_HOUR_CACHE_NAME)

    if key in cache:
        print(f"✅ Loading cache for: {key}")
        tags = cache[key]
        return {"opening_hours": tags.get("opening_hours")}

    print(f"🕒 Querying Overpass API for opening hours of {key}")
    query = f"""
    [out:json];
    {osm_type}({osm_id});
    out tags;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})

    if response.status_code != 200:
        return "Failed to fetch from OpenStreetMap"

    elements = response.json().get("elements", [])
    if not elements:
        return "No data found from OpenStreetMap"

    tags = elements[0].get("tags", {})
    cache[key] = tags
    save_cache(OPENING_HOUR_CACHE_NAME, cache)

    return {"opening_hours": tags.get("opening_hours")}
