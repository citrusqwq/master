from openai import OpenAI
import json

client = OpenAI()

system_prompt = f"""
You are a travel assistant that helps users plan urban day trips. 
Your task is to first extract the user's requirements from their request and then recommend an itinerary accordingly.
Your response must contain the **user requirement list** and the **recommended itinerary**. 
Each item in the recommended itinerary should include the following information:
1. Time - Suggested start time for visiting this place.
2. Place - Name of the place. 
3. Address - Output the address of the place only if the place is a specific Point of Interest (POI) and you are sure about the address. Output "-" if this is a non-specific location (e.g., district, neighborhood, city center) or you are unsure about the address.
4. Activity - What can users do, see, or experience at this place.
5. Planned duration - How much time should users spend at this place.
"""

system_prompt_wo = f"""
You are a travel assistant that helps users plan urban day trips. 
Your task is to recommend an itinerary based on the user requirements.
Each item in the recommended itinerary should include the following information:
1. Time - Suggested start time for visiting this place.
2. Place - Name of the place. 
3. Address - Output the address of the place only if the place is a specific Point of Interest (POI) and you are sure about the address. Output "-" if this is a non-specific location (e.g., district, neighborhood, city center) or you are unsure about the address.
4. Activity - What can users do, see, or experience at this place.
5. Planned duration - How much time should users spend at this place.
"""


def generate_itinerary(user_prompt, file_path, model, temperature):
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    completion = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature
    )

    raw_output = completion.choices[0].message.content
    print(raw_output)

    # --- Save to JSON file ---
    data_to_save = {
        "user_prompt": user_prompt,
        "model": model,
        "temperature": temperature,
        "response": raw_output,
    }

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data_to_save, json_file, ensure_ascii=False, indent=4)


# user_prompt = "I plan to fly to Athens from Berlin at 22:00 and I want to use the time to explore the city before that. I could start my travel the earliest at 8:00 from Berlin Central Station. I am interested in cultural activities and I need to have Dinner before the flight as well. I need to be at 20:00 at the airport. Plan the trip with my travel times accordingly."
user_prompt = "Please make an itineray for one day in Potsdam. I like places like museums but I want to spend also time just walking and getting a feeling about the city. Include a stop for breakfast and a stop for an afternoon coffee break but no lunch."

generate_itinerary(user_prompt, "test_itinerary_ex.json", "gpt-4.1-2025-04-14", 0)

# with open("prompts.json", "r", encoding="utf-8") as f:
#     prompts = json.load(f)

# for i, item in enumerate(prompts, start=25):
#     user_prompt = item["Prompt"]
#     out_file = f"Itinerary_{i:02d}.json"
#     generate_itinerary(user_prompt, out_file, "gpt-4.1-2025-04-14")

# for i, item in enumerate(prompts, start=37):
#     user_prompt = item["Prompt"]
#     out_file = f"Itinerary_{i:02d}.json"
#     generate_itinerary(user_prompt, out_file, "gpt-4.1-mini-2025-04-14")
