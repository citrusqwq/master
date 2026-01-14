from openai import OpenAI
import json

client = OpenAI()

system_prompt = f"""
You are an expert in behavioral analysis and travel psychology.

Your role is to infer a tentative traveler persona based on limited information, using careful, evidence-based reasoning similar to how a psychologist or behavioral researcher would analyze stated preferences.

## You will be given:
1) A user query (natural language), and
2) The user's occupation.

## Your job is to:
1) Analyze linguistic cues, stated preferences, constraints, and priorities in the user query, as well as signals implied by the occupation.
2) Infer a plausible traveler persona grounded strictly in the provided information.

## Important constraints:
- The user is instructed to write a query asking for planing a one-day trip. So you analysis should avoid this point.
- The persona is an informed inference, not a factual profile.
- Do NOT infer sensitive characteristics (e.g., health status, political views, religion, ethnicity).
- If evidence is weak or ambiguous, keep the persona high-level and conservative.

## Output format:

Analysis:
Briefly explain which elements of the user query and occupation informed your inferences.


Travel & Leisure Preferences:
- (3-5 bullet points describing most likely travel and leisure preferences)

Personality Traits:
- (4-6 comma-separated descriptive keywords)

Additional information:
- If the traveler explicitly mentioned traveling with someone else (e.g., with friends or family), specify that here; otherwise write "traveling alone".
"""


def create_persona(user_query, occupation):
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"User Query:\n{user_query}\nUser Occupation:\n{occupation}\n",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14", messages=messages, temperature=0.0
    )

    msg = response.choices[0].message.content
    print(msg)


user_query = "I plan to fly to Athens from Berlin at 22:00 and I want to use the time to explore the city before that. I could start my travel the earliest at 8:00 from Berlin Central Station. I am interested in cultural activities and I need to have Dinner before the flight as well. I need to be at 20:00 at the airport. Plan the trip with my travel times accordingly."
occupation = "Graduate Student in Computer Science"

create_persona(user_query, occupation)
