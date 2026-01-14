from datetime import datetime
import csv
import json
import re

itinerary_id = "33"

input_file_evaluation_itinerary = (
    f"simulation_results/alt_v2_evaluation_itinerary_{itinerary_id}.json"
)
csv_path = f"simulation_results/sim_eval_itinerary_{itinerary_id}_alt.csv"
txt_path = f"simulation_results/sim_eval_itinerary_{itinerary_id}_alt.txt"

# regex to extract two times (ignores AM/PM)
time_pattern = re.compile(
    r"(\d{1,2}:\d{2})\s*(?:AM|PM)?\s*-\s*(\d{1,2}:\d{2})\s*(?:AM|PM)?",
    re.IGNORECASE,
)

# emotion valence mapping
valence_map = {"negative": -1, "neutral": 0, "positive": 1}

with open(input_file_evaluation_itinerary, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

rows = []

# -------- First pass: collect rows --------
for i, item in enumerate(data, start=1):
    summary = item["summary"]
    start_time, end_time = time_pattern.search(summary).groups()

    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")

    duration = int(re.search(r"\d+", item["predicted_duration"]).group())

    # twist emotion values
    twist_emotion_valence = None
    twist_emotion_arousal = None
    if item["twist_happened"]:
        twist_emotion = item["twist_appraisal_results"]
        twist_emotion_valence = valence_map[twist_emotion["emotion_valence"]]
        twist_emotion_arousal = twist_emotion["emotion_arousal"]

    # final emotion values
    final_emotion = item["final_emotion_assessment"]
    final_emotion_valence = valence_map[final_emotion["emotion_valence"]]
    final_emotion_arousal = final_emotion["emotion_arousal"]

    time_adequacy = 1 if item["time_adequacy_assessment"] == "adequate" else -1

    # IAES score
    iaes = 0.5 * time_adequacy + 0.5 * final_emotion_valence

    rows.append(
        {
            "step": i,
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "duration": duration,
            "twist_emotion_valence": twist_emotion_valence,
            "twist_emotion_arousal": twist_emotion_arousal,
            "final_emotion_valence": final_emotion_valence,
            "final_emotion_arousal": final_emotion_arousal,
            "time_adequacy": time_adequacy,
            "iaes": iaes,
        }
    )

# total duration (first start → last end), in minutes
total_duration_minutes = (rows[-1]["end_dt"] - rows[0]["start_dt"]).total_seconds() / 60

final_score = 0.0

# -------- Write CSV --------
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow(
        [
            "step",
            "start_time",
            "end_time",
            "duration",
            "twist_emotion_valence",
            "twist_emotion_arousal",
            "final_emotion_valence",
            "final_emotion_arousal",
            "time_adequacy",
            "IAES",
            "weight",
        ]
    )

    for row in rows:
        step_duration_minutes = (row["end_dt"] - row["start_dt"]).total_seconds() / 60

        weight = step_duration_minutes / total_duration_minutes
        final_score += weight * row["iaes"]

        writer.writerow(
            [
                row["step"],
                row["start_time"],
                row["end_time"],
                row["duration"],
                row["twist_emotion_valence"],
                row["twist_emotion_arousal"],
                row["final_emotion_valence"],
                row["final_emotion_arousal"],
                row["time_adequacy"],
                row["iaes"],
                weight,
            ]
        )

# -------- Write TXT summary --------
with open(txt_path, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(f"Step {row['step']}:\n")
        f.write(f"{row['summary']}\n\n")

    f.write(f"Final score: {final_score}\n")
