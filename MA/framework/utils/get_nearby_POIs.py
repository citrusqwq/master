import requests
import json

52.4820525, 13.4338995
LAT = 52.4820525
LON = 13.4338995
RADIUS = 150  # meters

query = f"""
[out:json][timeout:25];
(
  node["tourism"~"attraction|museum|gallery|viewpoint|zoo|theme_park"](around:{RADIUS},{LAT},{LON});
  node["amenity"~"restaurant|cafe|bar|pub|fast_food"](around:{RADIUS},{LAT},{LON});
  node["leisure"~"park|garden|playground"](around:{RADIUS},{LAT},{LON});
  node["shop"~"clothes|shoes|fashion"](around:{RADIUS},{LAT},{LON});
);
out;
"""

url = "https://overpass-api.de/api/interpreter"
print("Querying Overpass API...")
response = requests.get(url, params={"data": query})
response.raise_for_status()
data = response.json()

# Parse results
pois = []
for el in data.get("elements", []):
    tags = el.get("tags", {})
    name = tags.get("name")
    if not name:  # skip if there's no name
        continue

    # collect only existing tags of interest
    tag_parts = []
    for key in ["amenity", "cuisine", "tourism", "shop"]:
        if key in tags:
            tag_parts.append(tags[key])

    tag_str = "/".join(tag_parts)
    pois.append(f"{name} - {tag_str}")


def pois_to_string(pois):
    """
    into a single concatenated string suitable for LLM input.
    """
    return "\n".join(pois)


print(pois_to_string(pois))
