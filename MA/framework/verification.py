import json
import re
from openai import OpenAI
import time
from tools.google import google_search

client = OpenAI()

system_prompt = f"""
You are a POI Address Verification Agent that follows the ReAct pattern.

You may use the following steps:
- Think: (optional)
- Action: (required when calling a function)
- Output: (required final response)

## Goal:
Given a single itinerary snippet, decide whether the provided address matches the claimed place (Point of Interest). You MUST use the provided function search(query) only when verification is required, and you MUST obey the 2-search maximum.

## Input:
You will receive an itinerary snippet (may be in German or English) containing fields such as:
- Place: ...
- Address: ...
(Other fields may exist but are not relevant.)

## Core rules:
1) If Place or Address is missing in the snippet, directly set all the field in the output JSON to null. 
2) Extract exactly the original Place text and Address text as they appear in the snippet.
3) Determine:
   - address_provided:
       true if an Address field exists and contains a non-empty address that is more than a placeholder (e.g., not "-", "TBD", "unknown").
       false otherwise.
   - non-specific_location:
       true if the Place refers to a non-specific location (e.g., district, neighborhood, city center).
       false otherwise.
4) Verification decision:
   - If address_provided is false OR non-specific_location is true:
       Do NOT call search().
       Set address_match_place to null.
   - Otherwise (address_provided is true AND non-specific_location is false):
       You MUST perform verification with search() to the 2-search maximum described below.

## Search procedure (max 2 searches total):
A) First search (required when verification is needed):
   - Call search() with ONLY the exact provided address string.
   - Analyze results to see what place/business/POI is associated with that address.
   - If results clearly indicate the address corresponds to the claimed Place (same venue name or clearly the same POI), set address_match_place = true.
   - If results clearly indicate the address corresponds to a different place and not the claimed Place, set address_match_place = false.
   - If results are inconclusive, proceed to B.

B) Second search (only if still unsure after A):
   - Call search() with the query: "<place name> impressum" (concatenate the mentioned place name and the word "impressum").
   - Use all the search results to decide address_match_place:
       true if you can confidently link the claimed Place to that address,
       false if strong evidence the place has another address,
       null if still not sure.

## Output Format: 

Output:
{{
  "place": string,
  "address_provided": boolean,
  "non-specific_location": boolean,
  "address_match_place": boolean | null
}}

## Function available:
- search(query): returns web search results for the query.

"""


def verify_address(itinerary_snippet):
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Here is the itinerary snippet for verification:\n{itinerary_snippet}",
        },
    ]

    for _ in range(5):  # safety limit
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=0.0,
        )
        msg = response.choices[0].message.content.strip()
        print("--------Agent--------")
        print(msg)

        # Detect "Action: search(...)"
        action_match = re.search(r'Action:\s*search\("(.*?)"\)', msg)
        if action_match:
            query = action_match.group(1)
            print(f"🔍 Model requested search for: {query}")
            search_results = google_search(query)
            print("--------User--------")
            observation_text = f"Observation: {json.dumps(search_results, indent=2, ensure_ascii=False)}"
            print(observation_text)
            messages.append({"role": "assistant", "content": msg})
            messages.append({"role": "user", "content": observation_text})
            continue

        # Detect "Output:" and extract final JSON
        output_match = re.search(r"Output:\s*(\{.*\})", msg, re.DOTALL)
        if output_match:
            json_text = output_match.group(1).strip()
            try:
                parsed = json.loads(json_text)
                messages.append({"role": "assistant", "content": msg})
                return parsed, messages
            except json.JSONDecodeError:
                print("❌ Invalid JSON format in Output, retrying...")
                messages.append({"role": "assistant", "content": msg})
                messages.append(
                    {
                        "role": "user",
                        "content": "Please output valid JSON after 'Output:'.",
                    }
                )
                continue

        # Default — add model's reasoning to the dialogue
        messages.append({"role": "assistant", "content": msg})

    return {"error": "No valid Output within 5 turns."}, messages


def verify_itinerary(itinerary_id):
    input_file = f"raw_itineraries/{itinerary_id}.json"
    out_file_agent_reasoning = f"agent_reasoning_{itinerary_id}.json"
    out_file_verification_result = f"verification_result_{itinerary_id}.json"
    with open(input_file, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    text = data["response"]
    pattern = r"Place:.*?(?=Planned duration:)"
    # pattern = r"(?<=Uhr).*?(?=Planned duration:)"
    # pattern = r"Place:.*?(?=Geplante Dauer:)"

    # pattern = r"\b\d{2}:\d{2}\b\s*(.*?)(?=Planned duration:)"

    itinerary_snippets = re.findall(pattern, text, flags=re.DOTALL)

    verification_result_list = []
    agent_reasoning_list = []

    for itinerary_snippet in itinerary_snippets:
        verification_output, messages = verify_address(itinerary_snippet)
        verification_output["snippet"] = itinerary_snippet
        verification_result_list.append(verification_output)
        agent_reasoning_list.append(messages)

    with open(out_file_verification_result, "w", encoding="utf-8") as f:
        json.dump(verification_result_list, f, ensure_ascii=False, indent=2)

    with open(out_file_agent_reasoning, "w", encoding="utf-8") as f:
        json.dump(agent_reasoning_list, f, ensure_ascii=False, indent=2)


# for i in range(41, 49):
#    itinerary_id = f"Itinerary_{i:02d}"
#    verify_itinerary(itinerary_id)
#    time.sleep(5)

# verify_itinerary("Itinerary_29")
