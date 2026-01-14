import re
import json
from openai import OpenAI
import time

client = OpenAI()

pass_one_system_prompt = f"""
You are an impartial evaluation judge for a travel-planning task.

## You will be given:
1) a user query (natural language), and
2) a numbered list of extracted requirements produced by a planner model.
The text might be in English or German. 

## Your job is to:
1) assess each extracted requirement as VALID or INVALID, and explain why;
2) identify any explicitly stated requirements in the user query that are missing from the extracted list.

## Rules:
1) An extracted requirement is VALID only if ALL of the following hold:
a) It is not a misinterpretation of the user query. (e.g. The user might be only asking for an itinerary in city A, but the planner model thought they are asking for city B just because the user also mentions B in the query.)
b) It is directly relevant to planning the itinerary requested by the user. 
c) It is either:
   - explicitly stated in the user query, OR
   - a reasonable and direct implication of the user query.

2) Missing requirements: 
You should try to identify requirements that are EXPLICITLY STATED in the user query but missing from the extracted list.
- Do NOT infer anything.  
- Do NOT add irrelevant information that is not about user's preference or constraint on the itinerary. 
- Do NOT add “one-day/day trip” or "plan an itinerary" as missing if it is absent, because the system prompt already fixes the task as recommend an itinerary for day trips.

3) Output constraints
- You must follow the required output format exactly.
- In the JSON Output:
  - "extracted_requirement_num" is the length of the numbered requirement list produced by the planner model.
  - "valid_requirements" must contain ONLY the original text of the valid extracted requirements.
  - "missing_requirements" must be a list of missing explicit requirements in text, or null if none are missing.

## Output format: 

Analysis:
Analyze each extracted requirement in order:
1. ....
2. ....

Missing requirements:
1. ...
2. ...
(or "none")

Output:
{{
  "extracted_requirement_num": integer,
  "valid_requirements": ["...", "..."],
  "missing_requirements": ["...", "..."] or null
}}

"""

pass_two_system_prompt = f"""
You are an impartial evaluation judge for a travel-planning task.

## You will be given:
1) a list of requirements (each is a short text requirement), and
2) a recommended itinerary (free-form text) produced by a planner model.
The text might be in English or German.

## Your job is to:
For each requirement, decide whether it is CLEARLY SATISFIED by the recommended itinerary, and explain why.

## Rules:
1) A requirement is SATISFIED only if at least one activity in itinerary clearly satisfy it or makes it possible.
2) Use ONLY the provided itinerary text as evidence.
   - Do NOT add external knowledge.
   - Do NOT infer unstated details.
3) Output constraints:
- You must follow the required output format exactly.
- In the JSON Output:
  - "satisfied_requirements" must contain ONLY the original text of requirements that are satisfied.
  - "satisfied_requirements_num" must equal the length of "satisfied_requirements".

## Output format:

Analysis:
Analyze each requirement in order:
1. ...
2. ...

Output:
{{
  "satisfied_requirements": ["...", "..."],
  "satisfied_requirements_num": <integer>
}}

"""

MAX_RETRIES = 2


def extract_json_from_output(text: str):
    """
    Extract JSON that appears after 'Output:'.
    Returns parsed dict or raises ValueError.
    """
    match = re.search(r"Output:\s*(\{.*\})", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found after 'Output:'")

    json_str = match.group(1)
    return json.loads(json_str)


def pass_one(user_query, extracted_requirement_list):
    messages = [
        {"role": "system", "content": pass_one_system_prompt},
        {
            "role": "user",
            "content": f"User Query:\n{user_query} \n The requirement list produced by the planner model:\n{extracted_requirement_list} ",
        },
    ]
    for attempt in range(MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model="gpt-5-2025-08-07",  # "gpt-4.1-2025-04-14",
            messages=messages,
        )

        msg = response.choices[0].message.content
        print(msg)

        try:
            extracted_json = extract_json_from_output(msg)
            messages.append({"role": "assistant", "content": msg})
            return extracted_json, messages  # ✅ success

        except Exception:
            if attempt == MAX_RETRIES:
                raise RuntimeError("Failed to obtain valid JSON after maximum retries")

            messages.append({"role": "assistant", "content": msg})
            messages.append(
                {
                    "role": "user",
                    "content": "Please output valid JSON after 'Output:'.",
                }
            )


def pass_two(numbered_requirements, recommended_itinerary):
    messages = [
        {"role": "system", "content": pass_two_system_prompt},
        {
            "role": "user",
            "content": f"The requirement list:\n{numbered_requirements} \n The recommended itinerary produced by the planner model:\n{recommended_itinerary} ",
        },
    ]
    for attempt in range(MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model="gpt-5-2025-08-07",  # "gpt-4.1-2025-04-14",
            messages=messages,
        )

        msg = response.choices[0].message.content
        print(msg)

        try:
            extracted_json = extract_json_from_output(msg)
            messages.append({"role": "assistant", "content": msg})
            return extracted_json, messages  # ✅ success

        except Exception:
            if attempt == MAX_RETRIES:
                raise RuntimeError("Failed to obtain valid JSON after maximum retries")

            messages.append({"role": "assistant", "content": msg})
            messages.append(
                {
                    "role": "user",
                    "content": "Please output valid JSON after 'Output:'.",
                }
            )


def align_itinerary(itinerary_id):
    input_file = f"raw_itineraries/{itinerary_id}.json"
    out_file_alignment_analysis = f"alignment_analysis_{itinerary_id}.json"
    out_file_alignment_result = f"alignment_result_{itinerary_id}.json"

    alignment_analysis_list = []
    alignment_result_list = []

    with open(input_file, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    user_query = data["user_prompt"]
    response = data["response"]

    # parts = re.split(r"\*\*Recommended Itinerary:\*\*", response, flags=re.IGNORECASE, maxsplit=1)
    parts = re.split(
        r"Recommended Itinerary", response, flags=re.IGNORECASE, maxsplit=1
    )

    if len(parts) != 2:
        raise ValueError("Recommended Itinerary section not found")

    extracted_requirement_list, recommended_itinerary = parts

    pass_one_extracted_json, pass_one_messages = pass_one(
        user_query, extracted_requirement_list
    )

    alignment_analysis_list.append(pass_one_messages)
    alignment_result_list.append(pass_one_extracted_json)

    valid_requirements_list = pass_one_extracted_json["valid_requirements"]
    if len(valid_requirements_list) > 0:
        numbered_requirements = "\n".join(
            f"{i+1}. {req}" for i, req in enumerate(valid_requirements_list)
        )

        pass_two_extracted_json, pass_two_messages = pass_two(
            numbered_requirements, recommended_itinerary
        )

        alignment_analysis_list.append(pass_two_messages)
        alignment_result_list.append(pass_two_extracted_json)
    else:
        alignment_result_list.append({"satisfied_requirements_num": 0})

    with open(out_file_alignment_analysis, "w", encoding="utf-8") as f:
        json.dump(alignment_analysis_list, f, ensure_ascii=False, indent=2)

    with open(out_file_alignment_result, "w", encoding="utf-8") as f:
        json.dump(alignment_result_list, f, ensure_ascii=False, indent=2)


# for i in range(44, 49):
#    itinerary_id = f"Itinerary_{i:02d}"
#    align_itinerary(itinerary_id)
#    time.sleep(5)
align_itinerary("Itinerary_43")
