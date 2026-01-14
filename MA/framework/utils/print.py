import json
import re

with open("raw_itineraries/Itinerary_33.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# print(data["response"])
text = data["response"]
# pattern = r"Place:.*?(?=Planned duration:)"
# pattern = r"(?<=Uhr).*?(?=Planned duration:)"

# pattern = r"\b\d{2}:\d{2}\b\s*(.*?)(?=Planned duration:)"

# matches = re.findall(pattern, text, flags=re.DOTALL)


# print(matches)
print(text)
