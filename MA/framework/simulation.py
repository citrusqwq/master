from datetime import datetime, time, timedelta
from openai import OpenAI
import json
import re

client = OpenAI()

itinerary_id = "33"

MAX_RETRIES = 2

neural_valence = "neural"
neural_arousal = "neural"


input_file_simulation_itinerary = (
    f"simulation_itineraries/simulation_itinerary_{itinerary_id}.json"
)

itinerary_list = []

simulation_analysis_list = []

with open(input_file_simulation_itinerary, "r", encoding="utf-8") as json_file:
    loaded_data = json.load(json_file)

itinerary_list.extend(loaded_data)


def extract_json(text: str):
    """
    Extract the first JSON object from text.
    Raises ValueError if parsing fails.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))


def call_llm_and_parse_json(
    messages: str,
):
    for attempt in range(MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=0.0,
        )

        msg = response.choices[0].message.content
        print("-----------------------------")
        print(msg)
        print("-----------------------------")

        try:
            extracted_json = extract_json(msg)
            messages.append({"role": "assistant", "content": msg})
            simulation_analysis_list.append(messages)
            return extracted_json  # ✅ success

        except Exception:
            if attempt == MAX_RETRIES:
                return {"Error": "Failed to obtain valid JSON after maximum retries"}

            # ❌ retry
            messages.append({"role": "assistant", "content": msg})
            messages.append(
                {
                    "role": "user",
                    "content": "Please output valid JSON only.",
                }
            )


# persona = """
# Travel & Leisure Preferences:
# - Enjoys exploring unique or independent bookstores and cultural venues
# - Values diverse and international dining experiences, with a specific interest in South American cuisine
# - Prefers social, interactive group activities (e.g., arcades, karaoke bars)
# - Seeks a balance between intellectually stimulating and playful, energetic activities

# Personality Traits:
# - Social, curious, open-minded, playful, analytical, adventurous

# Additional information:
# Traveling with friends
# """

persona = """
Travel & Leisure Preferences:
- Prioritizes comfort, relaxation, and low-effort experiences over exploration
- Enjoys scenic spots, cafés with good seating, and calm environments rather than busy or loud places
- Prefers familiar or highly rated food options instead of experimental or niche cuisine

Personality Traits:
- Laid-back, reflective, cautious, pragmatic, observant

Additional information:
Traveling with friends
"""


def anticipate(
    current_visiting_plan,
    emotion_valence,
    emotion_arousal,
    experienced_activity_list=None,
):
    additional_system_prompt = ""
    previous_activity_line = ""
    if experienced_activity_list:
        activities = "\n".join(experienced_activity_list)
        previous_activity_line = f"\nPrevious activities:\n{activities}\n\n"
        additional_system_prompt = "\n- A list of previously experienced activities (it may be empty if there are no prior activities)\n"

    system_prompt = f"""
You are a psychology expert specializing in understanding traveler's expectations.

## You will be given:
- A traveler persona{additional_system_prompt}
- The traveler's current emotional state, defined by:
   - emotion_valence: positive / neutral / negative
   - emotion_arousal: high / neutral / low
- A short description of the next recommended activity in the itinerary.

## Your task:
1) Analyze the traveler's likely thoughts, expectations and emotion when reading about the upcoming activity.
2) Ground your analysis in:
   - The traveler persona,
   - The current emotional state,
   - The nature of the upcoming activity.

## Constraints:
- Do NOT invent new facts about the traveler.
- Emotional valence and arousal in the output should reflect the *anticipated change or continuation* given the upcoming activity.

## Output format:

Analysis:
Briefly explain the traveler's likely thoughts and feelings about the upcoming activity, referencing signals from the persona, current emotional state, and activity description.

Output:
{{
  "expectation": "<One concise sentence describing what the traveler expects from the upcoming experience>",
  "emotion_valence": "positive | neutral | negative",
  "emotion_arousal": "high | neutral | low"
}}
"""

    user_prompt = f"""
Traveler persona:
{persona}
{previous_activity_line}

Current emotion state:
 - emotion_valence: {emotion_valence}
 - emotion_arousal: {emotion_arousal}

Upcoming activity:
{current_visiting_plan}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print("----user_prompt: anticipate----")
    print(user_prompt)
    print("-------------------------------")

    return call_llm_and_parse_json(messages)


def predictBehavior(
    original_visiting_plan,
    expectation,
    twist,
    twist_appraisal_results,
    possible_duration,
):

    twist_line = ""
    if twist_appraisal_results:
        twist_line = f"\nTwist: {twist}\nAdapted plan: {twist_appraisal_results['adapted_visiting_plan']}\n"

    system_prompt = """
You are a psychology expert specializing in travel behavior, time perception, and on-site activity patterns.
You specialize in estimating visit durations, predicting traveler behaviors, and assessing subjective time satisfaction during travel.
Base your reasoning on realistic human behavior, time constraints, and the traveler's persona.

## You will be given:
1) A traveler persona,
2) An initial visiting plan,
3) The traveler's initial expectation,
4) An adapted visiting plan (only if a prior “twist” occurred)
5) A possible visiting duration:
   - Either a fixed number of minutes, OR
   - A range of minutes (e.g., 45–90 minutes).

## Your task:
1) Infer what the traveler likely does during that time:
   - This should be based on the visiting plan and their expectation. If an adapted plan is given, refer to the adapted plan.
   - All activities and decisions mentioned in the plan are assumed to be intended for the given possible visiting duration.
2) Predict how long the traveler actually spends on these activities:
   - If a fixed number is given, you MUST use that exact number, as it indicates the traveler is scheduled to spend that amount of time.
   - If a range is given, choose a realistic value within the range, justified by the persona and the plan.
3) Assess how the traveler feels about the time spent:
   - Whether the time felt insufficient, adequate, or excessive for the planned activities.

### Output Format

Analysis:
Analyze how the traveler likely behaves, how they spend their time on the activities, and how they evaluate the sufficiency of the time.

Output:
{
  "predicted_duration": "<integer> min",
  "predicted_behavior": "<1–3 sentences in past tense describing what the traveler did and how they spent the time>",
  "time_adequacy_assessment": "insufficient | adequate | excessive"
}
"""

    user_prompt = f"""
Traveler persona:
{persona} 

The initial visiting plan: 
{original_visiting_plan}

The travler's initial expectation: 
{expectation}
{twist_line}

Possible visiting duration: 
{possible_duration}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    print("----user_prompt: predictBehavior----")
    print(user_prompt)
    print("------------------------------------")

    return call_llm_and_parse_json(messages)


def reflect(
    original_visiting_plan,
    expectation,
    twist,
    twist_appraisal_results,
    emotion_valence,
    emotion_arousal,
    predicted_behavior,
):

    twist_line = ""
    if twist_appraisal_results:
        twist_line = f"\nTwist: {twist}\nAdapted plan: {twist_appraisal_results['adapted_visiting_plan']}\n"

    system_prompt = """
You are a psychology expert specializing in travel experience reflection and emotional appraisal.

## You will be given:
1) A traveler persona,
2) An initial visiring plan,
3) The traveler's expectation before the activity,
4) Any twist that occurred (if applicable; otherwise this may be absent),
5) The traveler's emotion state before the activity:
   - emotion_valence: positive / neutral / negative
   - emotion_arousal: high / neutral / low
6) A description of what the traveler actually did.

## Your task:
1) Analyze how the traveler likely reflects on the experience after it is over:
   - How they compare the actual experience with their prior expectation,
   - How they interpret any twist (e.g., disappointment, acceptance, reframing, pleasant surprise).
2) Infer the traveler's updated emotional state after reflection.

### Output Format

Analysis:
Analyze the traveler's likely reflections on the experience and how they feel now.

Output:
{
  "emotion_valence": "positive | neutral | negative",
  "emotion_arousal": "high | neutral | low"
}
"""

    user_prompt = f"""
Traveler persona:
{persona}

Initial visiting plan: 
{original_visiting_plan}

Initial expectation:
{expectation}
{twist_line}

Traveler's emotion state before the activity: 
 - emotion_valence: {emotion_valence}
 - emotion_arousal: {emotion_arousal}

Actual activity:
{predicted_behavior}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print("----user_prompt: reflect----")
    print(user_prompt)
    print("-----------------------------")

    return call_llm_and_parse_json(messages)


def twist(
    situation,
    emotion_valence,
    emotion_arousal,
    current_visiting_plan,
    expectation,
    alternatives,
):
    alternatives_text = "\n".join(alternatives)
    system_prompt = """
You are a psychology expert specializing in travel experiences and how travelers cognitively and emotionally respond to unexpected situations during a trip.

Your task is to infer how a traveler is likely to interpret an unexpected situation upon arrival, what they decide to do next, and how their emotions update.

## You will be given:
1) Traveler persona 
2) The traveler's current emotional state, defined by:
   - emotion_valence: positive / neutral / negative
   - emotion_arousal: high / neutral / low
3) Initial visiting plan 
4) Their expectation before arrival
5) Encountered situation upon arrival 
6) A list of alternative nearby POIs 

## Your task:
1) Infer how the traveler is likely to interpret this situation.
2) Analyze the traveler's likely next action and how their emotion might change.

## Constraints:
1) Assume that the traveler cannot leave the area and may only wait, visit the current place, or choose among the provided nearby alternatives. 
2) If a place has a time constraint, it must be respected. If there is still time left after the traveler visits one place, also infer what they might plan to do next.

## Output format:

Analysis:
Explain how the traveler most likely interprets the situation, what they do next, and how they feel. 

Output:
{
  "adapted_visiting_plan": "<2-3 sentences describing the situation, their decision, and their new expectation>",
  "emotion_valence": "positive | neutral | negative",
  "emotion_arousal": "high | neutral | low"
}
"""

    user_prompt = f"""
Traveler persona:
{persona}

Current emotion state:
 - emotion_valence: {emotion_valence}
 - emotion_arousal: {emotion_arousal}

Initial visiting plan:
{current_visiting_plan}

Traveler's expectation before arrival:
{expectation}

Situation upon arrival:
{situation}

Possible alternative POIs nearby (POI_name - description):
{alternatives_text}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print("----user_prompt: twist----")
    print(user_prompt)
    print("--------------------------")

    return call_llm_and_parse_json(messages)


def summarize_activity(
    start_time,
    visiting_plan,
    twist,
    twist_appraisal_results,
    predicted_duration,
    predicted_behavior,
):
    twist_line = ""
    if twist_appraisal_results:
        twist_line = f"\nTwist: {twist}\nAdapted plan: {twist_appraisal_results['adapted_visiting_plan']}\n"

    system_prompt = """
You are an assistant responsible for summarizing a completed travel activity.

## You will be given:
1) The start time of the activity,
2) The initial visiting plan,
3) An adapted visiting plan (if a twist occurred; otherwise it may be unchanged),
4) The actual time spent at the activity,
5) A description of what the traveler actually did.

## Your task:
1) Determine the activity end time based on the start time and the actual time spent.
2) Identify the final place and activity the traveler engaged in (based on the adapted plan and actual activity).
3) Produce a single concise sentence summarizing:
   - the time range (start–end),
   - where the traveler was,
   - and what they did.

## Output format:
Output ONLY valid JSON in the following format:

{
  "summary": "<xx:xx - yy:yy: one concise sentence summarizing what the traveler did at which place>"
}
"""
    user_prompt = f"""
Start time: 
{start_time}

The initial visiting plan: 
{visiting_plan}
{twist_line}

Time spent: 
{predicted_duration}

Actual activity:
{predicted_behavior}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return call_llm_and_parse_json(messages)


# -------------------------------------------------------------------------
# -------------------------- Simulation loop ------------------------------
# -------------------------------------------------------------------------

itinerary_evaluation_list = []
experienced_activity_list = []

current_emotion_valence = "neural"
current_emotion_arousal = "neural"

include_previous_activities = True

for i, step in enumerate(itinerary_list):
    visiting_plan = step["place"] + "\n" + step["activity"]

    # initialize the evaluation result dict
    current_step_evaluation = {
        "start_time": step["start_time"],
        "planned_activity": visiting_plan,
        "expectation": None,
        "twist_happened": False,
        "twist_appraisal_results": None,
        "predicted_duration": None,
        "predicted_behavior": None,
        "time_adequacy_assessment": None,
        "final_emotion_assessment": None,
        "summary": None,
    }

    # anticipate
    if include_previous_activities:
        anticipate_results = anticipate(
            visiting_plan,
            current_emotion_valence,
            current_emotion_arousal,
            experienced_activity_list,
        )
    else:
        anticipate_results = anticipate(visiting_plan, neural_valence, neural_arousal)
    current_emotion_valence = anticipate_results["emotion_valence"]
    current_emotion_arousal = anticipate_results["emotion_arousal"]
    current_step_evaluation["expectation"] = anticipate_results["expectation"]

    # twist appraisal
    if step["twist"]:
        current_step_evaluation["twist_appraisal_results"] = twist(
            step["twist"],
            current_emotion_valence,
            current_emotion_arousal,
            visiting_plan,
            current_step_evaluation["expectation"],
            step["alternatives"],
        )
        current_step_evaluation["twist_happened"] = True
        current_emotion_valence = current_step_evaluation["twist_appraisal_results"][
            "emotion_valence"
        ]
        current_emotion_arousal = current_step_evaluation["twist_appraisal_results"][
            "emotion_arousal"
        ]

    # predict visiting behavior
    predicted_behavior_results = predictBehavior(
        visiting_plan,
        current_step_evaluation["expectation"],
        step["twist"],
        current_step_evaluation["twist_appraisal_results"],
        step["possible_duration"],
    )

    current_step_evaluation.update(predicted_behavior_results)

    # reflect the experience
    current_step_evaluation["final_emotion_assessment"] = reflect(
        visiting_plan,
        anticipate_results["expectation"],
        step["twist"],
        current_step_evaluation["twist_appraisal_results"],
        current_emotion_valence,
        current_emotion_arousal,
        predicted_behavior_results["predicted_behavior"],
    )
    current_emotion_valence = current_step_evaluation["final_emotion_assessment"][
        "emotion_valence"
    ]
    current_emotion_arousal = current_step_evaluation["final_emotion_assessment"][
        "emotion_arousal"
    ]

    # summarize the activity
    summary_result = summarize_activity(
        step["start_time"],
        visiting_plan,
        step["twist"],
        current_step_evaluation["twist_appraisal_results"],
        predicted_behavior_results["predicted_duration"],
        predicted_behavior_results["predicted_behavior"],
    )
    current_step_evaluation.update(summary_result)
    experienced_activity_list.append(summary_result["summary"])

    # save the evaluation of the current step
    itinerary_evaluation_list.append(current_step_evaluation)

# output simulation results
output_llm_evaluation_itinerary = f"alt_v2_evaluation_itinerary_{itinerary_id}.json"
output_simulation_analysis = f"alt_v2_simulation_analysis_itinerary_{itinerary_id}.json"

with open(output_llm_evaluation_itinerary, "w", encoding="utf-8") as f:
    json.dump(itinerary_evaluation_list, f, ensure_ascii=False, indent=2)

with open(output_simulation_analysis, "w", encoding="utf-8") as f:
    json.dump(simulation_analysis_list, f, ensure_ascii=False, indent=2)


print("\n".join(experienced_activity_list))
