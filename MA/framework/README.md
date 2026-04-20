# Overview

This repo contains the following important components: 

- Several scripts supporting the entire workflow. (**Note**: this is **not an automated pipeline**. I personally executed each step/script seprarately as needed during my master thesis. But **it is possible to write a a top-level orchestrator calling functions from the first three scripts to build a pipeline for these steps. While the last step simulation would first require an manual verification and itineray data augmentation.**  )
  - **Itineray generation** (*generation.py*): Call an LLM to generate a list of extracted user requirement the recommended itinerary given user prompt. The recommended itinerary is a list of activities. **(Examples for such itineraries can be found in folder *raw_itineraries.*) **
  - **Address verification** (*verification.py*): Call an LLM agent (with a web search tool) to verify all the provided addresses in the itinerary snippet. 
  - **User requirement validation** (*alignment.py*): Call an LLM to judge whether each extracted user requirement is valid (compared against the original user query) and satisfied (compared against the recommended itinerary).  
  - **Travel experience prediction** (*simulation.py*): Call an LLM to predict user's travel experience when attempting to execute a given itinerary. **To run the simulation, a human annotator needs to verify the itinerary and augment the original itinerary with some extra fields. Examples for such itineraries can be found in folder *simulation_itineraries*.**
- Tools: This folder contains the functions that can be called by an LLM agent. 
  - **Only the *google_search()* tool was used in my final master thesis**. This tool is implemented with Custom Search JSON API from Google Programmable Search Engine and would require an API key. (Note: [The Custom Search JSON API is closed to new customers and Vertex AI Search is suggested as a favorable alternative.](https://developers.google.com/custom-search/v1/overview) ) 
- Utils: This folder contains util functions. 
  - **Only the *cache.py* is relevant** which contains functions for saving the search result in Cache folder and loading from the Cache. 
- Cache: This folder contains the cached tool-calling results. 



# generation.py

``````python
def generate_itinerary(user_prompt, file_path, model, temperature):
    """
    Generates an itinerary using an LLM and saves the result to a JSON file.

    Args:
        user_prompt (str):    The user's travel request.
        file_path (str):      Destination path for the output JSON file
                              (e.g. "output/itinerary.json").
        model (str):          The model identifier to use.
        temperature (float):  Sampling temperature.

    Returns:
        None

    Side effects:
        - Prints the raw model response to stdout.
        - Writes a JSON file to `file_path` containing:
            {
                "user_prompt":  <str>,
                "model":        <str>,
                "temperature":  <float>,
                "response":     <str>
            }

    Example:
        generate_itinerary(
            user_prompt="Plan a 5-day trip to Tokyo for two people.",
            file_path="output/tokyo_trip.json",
            model="gpt-4o",
            temperature=0.7,
        )
    """
``````

**Notes**: 

- For my master thesis, I prepared a *prompts.json* that contains all the user queries needed for my experiment and wrote a loop to iterate through the prompts to generate the itineraries. I saved each generated ititnerary to a different JSON file as I was doing a qualitative analysis and often needed to inspect each itinerary in details.



# verification.py

``````python
def verify_address(itinerary_snippet):
    """
    Verifies the address details of a single itinerary snippet using a
    ReAct-style agentic loop.

    The model may iteratively request Google searches via a structured
    `Action: search("...")` pattern. Once confident, it emits a final
    `Output: {...}` JSON block. The loop runs for a maximum of 5 turns
    to prevent infinite iteration.

    Args:
        itinerary_snippet (str): A plain-text excerpt from an itinerary
                                 describing a single place/stop
                                 (e.g. name, address, scheduled time).

    Returns:
        tuple[dict, list[dict]]:
            - parsed (dict):    The model's structured verification result
                                extracted from the `Output:` block, or
                                `{"error": "No valid Output within 5 turns."}`
                                if the loop exhausted its limit.
            - messages (list):  The full conversation history, useful for
                                analyzing agent reasoning.

    Side effects:
        - Prints agent and observation turns to stdout.
        - May trigger one or more Google Search API calls.

    Example:
        result, history = verify_address(
            "Place:** Landungsbrücken  \n**Address:** Bei den St. Pauli-Landungsbrücken, 20359 Hamburg, Germany  \n**Activity:** Start your day at the iconic Landungsbrücken piers.... "
        )
    """


def verify_itinerary(itinerary_id):
    """
    Orchestrates address verification for all recommended activities from a saved
    itinerary file.

    Reads a raw itinerary JSON file, extracts individual activity snippets
    using a regex pattern, calls `verify_address()` on each, and writes
    both the structured verification results and the full agent reasoning
    traces to two JSON output files.

    Args:
        itinerary_id (str): Unique identifier for the itinerary. Used to
                            locate the input file and name the output files:
                            - Input:  raw_itineraries/<itinerary_id>.json
                            - Output: verification_result_<itinerary_id>.json
                            - Output: agent_reasoning_<itinerary_id>.json

    Returns:
        None

    Side effects:
        - Reads from  `raw_itineraries/<itinerary_id>.json`.
        - Writes structured verification results to
          `verification_result_<itinerary_id>.json`.
        - Writes full agent conversation traces to
          `agent_reasoning_<itinerary_id>.json`.
        - Triggers one `verify_address()` call (and potentially multiple
          Google searches) per extracted snippet.

    Example:
        verify_itinerary("itinerary_02")
        # Reads  raw_itineraries/itinerary_02.json
        # Writes verification_result_itinerary_02.json
        # Writes agent_reasoning_itinerary_02.json
    """

``````

**Notes**: 

- I didn't force the planner model to output in a structured JSON format but allowed response in plain text, so I was using regex pattern to extract each single activity snippet and adjusted the pattern as needed. (So if you force the recommended itinerary to be output in JSON then the parsing would become much easier.) The current active regex pattern in the script is `pattern = r"Place:.*?(?=Planned duration:)"`  which: 
  - **Starts** with the literal word `Place:`
  - **Captures everything** after it 
  - **Stops just before** the text `Planned duration:` (lookahead, so that phrase is not included in the match)
- Examples of verification results and the reasoning traces can be found in the folder *verification_results* and the folder *agent_reasoning*. 



# alignment.py

``````python
def extract_json_from_output(text: str):
    """
    A helper function. Extracts and parses a JSON object from a model response containing an
    `Output:` block.

    Args:
        text (str): Raw model response text expected to contain a pattern
                    of the form `Output: {...}`.

    Returns:
        dict: The parsed JSON object following `Output:`.

    Raises:
        ValueError:         If no `Output: {...}` pattern is found in the text.
        json.JSONDecodeError: If the matched block is not valid JSON.

    Example:
        result = extract_json_from_output(
            "Some reasoning...\\nOutput: {\\"status\\": \\"ok\\"}"
        )
        # returns {"status": "ok"}
    """


def pass_one(user_query, extracted_requirement_list):
    """
    First evaluation pass: validates the planner's extracted requirements
    against the original user query and returns a structured JSON assessment.

    Args:
        user_query (str):                The original user travel request.
        extracted_requirement_list (str): The requirement list extracted by
                                          the planner model from the user query.

    Returns:
        tuple[dict, list[dict]]:
            - extracted_json (dict):  Parsed JSON from the model's `Output:`
                                      block. 
            - messages (list[dict]):  Full conversation history for this pass,
                                      useful for analysis.

    Raises:
        RuntimeError: If a valid JSON `Output:` block is not produced within
                      MAX_RETRIES attempts.

    """


def pass_two(numbered_requirements, recommended_itinerary):
    """
    Second evaluation pass: checks whether the recommended itinerary
    satisfies each validated requirement from pass one.

    Args:
        numbered_requirements (str):   Newline-separated, numbered list of
                                       valid requirements produced by pass one
                                       (e.g. "1. No museums\\n2. 3 days").
        recommended_itinerary (str):   The recommended itinerary section
                                       extracted from the raw model response.

    Returns:
        tuple[dict, list[dict]]:
            - extracted_json (dict):  Parsed JSON from the model's `Output:`
                                      block. 
            - messages (list[dict]):  Full conversation history for this pass,
                                      useful for analysis.

    Raises:
        RuntimeError: If a valid JSON `Output:` block is not produced within
                      MAX_RETRIES attempts.

    """


def align_itinerary(itinerary_id):
    """
    Orchestrates the two-pass alignment evaluation for a saved itinerary file
    and writes the results to two JSON output files.

    Reads a raw itinerary JSON file, splits the response into a requirement
    list and a recommended itinerary section, then runs `pass_one` to
    validate requirements and (if any are valid) `pass_two` to assess whether
  	the itinerary satisfies them.

    Args:
        itinerary_id (str): Unique identifier for the itinerary. Used to
                            locate the input file and name the output files:
                            - Input:  raw_itineraries/<itinerary_id>.json
                            - Output: alignment_analysis_<itinerary_id>.json
                            - Output: alignment_result_<itinerary_id>.json

    Returns:
        None

    Raises:
        ValueError:    If the `Recommended Itinerary` section is not found
                       in the raw response.
        RuntimeError:  Propagated from `pass_one` or `pass_two` if valid
                       JSON is not obtained within MAX_RETRIES.

    Side effects:
        - Reads from  `raw_itineraries/<itinerary_id>.json`.
        - Writes per-pass conversation traces to
          `alignment_analysis_<itinerary_id>.json`.
        - Writes per-pass structured results to
          `alignment_result_<itinerary_id>.json`.

    Example:
        align_itinerary("itinerary_02")
        # Reads  raw_itineraries/itinerary_02.json
        # Writes alignment_analysis_itinerary_02.json
        # Writes alignment_result_itinerary_02.json
    """

``````



# simulation.py

**Notes**: 

- Essentially, it is **a cognitive simulation of a traveller's emotional arc across the entire trip**. Below is a high-level explanation for the simulation loop.  
- Examples of simulation results and the reasoning and analysis generated by LLM can be found in the folder *simulation_results* and the folder *simulation_analysis*. 

``````python
# -------------------------------------------------------------------------
# -------------------------- Simulation loop ------------------------------
# -------------------------------------------------------------------------
#
# Simulates a traveller's emotional and behavioural experience as they
# progress through each step of a planned itinerary.
#
# For every stop/activity, the loop runs four sequential
# LLM-driven stages that mirror a real person's cognitive journey:
#
#   1. ANTICIPATE  — The traveller forms expectations and an emotional
#                    state (valence + arousal) before arriving at the
#                    next stop.
#
#   2. TWIST       — If an unexpected event is recorded for this stop,
#                    the model appraises how the surprise
#                    affects the traveller's emotion, given their prior
#                    expectations and any available alternatives.
#
#   3. PREDICT     — Given the plan, expectations, and any twist, the model
#                    predicts the traveller's actual visiting behaviour and
#                    how long they are likely to stay.
#
#   4. REFLECT     — After the visit, the model updates the traveller's
#                    emotional state to reflect the full experience.
#                    This final emotion is carried forward as the starting
#                    state for the next step.
#
# After all four stages, the activity is summarised and appended to a 
# `experienced_activity_list`, which grows throughout the loop and
# provides episodic memory for subsequent anticipation steps.
#
# Emotion state is tracked across the entire loop via two variables:
#   - current_emotion_valence  (e.g. "positive" / "negative" / "neutral")
#   - current_emotion_arousal  (e.g. "high" / "low" / "neutral")
# Both are initialised to "neutral" and updated after every stage that
# produces a new emotional outcome.
#
# Outputs written to disk after the loop completes:
#   - alt_v2_evaluation_itinerary_<itinerary_id>.json
#       Per-step evaluation dicts.
#   - alt_v2_simulation_analysis_itinerary_<itinerary_id>.json
#       Reasoning and analysis generated by LLM during the loop.
``````

