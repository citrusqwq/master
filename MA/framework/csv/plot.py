import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
from matplotlib import colors as mcolors
from datetime import datetime
import numpy as np

# Example data
"""
itineraries = [
    {
        "name": "Itinerary 1",
        "timestamps": [
            "10:00",
            "11:25",
            "11:45",
            "12:35",
            "13:00",
            "14:30",
            "14:45",
            "15:40",
            "16:00",
            "17:55",
            "18:30",
            "20:30",
        ],
        "valence": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "arousal": [
            "neutral",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
        ],
    },
    {
        "name": "Itinerary 2",
        "timestamps": [
            "10:00",
            "11:20",
            "11:45",
            "12:45",
            "13:00",
            "14:30",
            "14:45",
            "16:45",
            "17:00",
            "19:00",
        ],
        "valence": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "arousal": [
            "neutral",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "neutral",
        ],
    },
    {
        "name": "Itinerary 3",
        "timestamps": [
            "10:00",
            "11:15",
            "11:45",
            "12:35",
            "13:00",
            "14:10",
            "14:45",
            "15:30",
            "16:00",
            "18:00",
            "18:30",
            "21:00",
        ],
        "valence": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "arousal": [
            "neutral",
            "neutral",
            "neutral",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
            "high",
        ],
    },
]
"""

itineraries = [
    {
        "name": "Itinerary 1",
        "timestamps": [
            "10:00",
            "11:25",
            "11:45",
            "12:35",
            "13:00",
            "14:30",
            "14:45",
            "15:40",
            "16:00",
            "17:55",
            "18:30",
            "20:30",
        ],
        "valence": [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        "arousal": [
            "low",
            "low",
            "low",
            "low",
            "low",
            "low",
            "neutral",
            "low",
            "neutral",
            "low",
            "neutral",
            "high",
        ],
    },
    {
        "name": "Itinerary 2",
        "timestamps": [
            "10:00",
            "11:20",
            "11:45",
            "12:45",
            "13:00",
            "14:30",
            "14:45",
            "16:45",
            "17:00",
            "19:00",
        ],
        "valence": [1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        "arousal": [
            "low",
            "low",
            "low",
            "low",
            "neutral",
            "low",
            "low",
            "neutral",
            "low",
            "low",
        ],
    },
    {
        "name": "Itinerary 3",
        "timestamps": [
            "10:00",
            "11:15",
            "11:45",
            "12:35",
            "13:00",
            "14:10",
            "14:45",
            "15:30",
            "16:00",
            "18:00",
            "18:30",
            "21:00",
        ],
        "valence": [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        "arousal": [
            "low",
            "low",
            "low",
            "low",
            "low",
            "low",
            "low",
            "low",
            "neutral",
            "low",
            "neutral",
            "low",
        ],
    },
]

color_map = {
    "low": "#4C72B0",  # muted blue
    "neutral": "#8172B3",  # soft purple
    "high": "#C44E52",  # muted red
}

valence_to_y = {-1: 0, 0: 1, 1: 2}


# -----------------------------
# Helper: gradient line
# -----------------------------
def gradient_line(ax, x, y, color_start, color_end, n_segments=40):
    x_num = mdates.date2num(x)
    xs = np.linspace(x_num[0], x_num[1], n_segments)
    ys = np.linspace(y[0], y[1], n_segments)

    segments = [[(xs[i], ys[i]), (xs[i + 1], ys[i + 1])] for i in range(n_segments - 1)]

    c1 = np.array(mcolors.to_rgba(color_start))
    c2 = np.array(mcolors.to_rgba(color_end))
    colors = np.linspace(c1, c2, n_segments - 1)

    lc = LineCollection(segments, colors=colors, linewidth=2, alpha=0.8)
    ax.add_collection(lc)


# -----------------------------
# Plot
# -----------------------------
fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    figsize=(11, 6),
    sharex=True,
)

for ax, itinerary in zip(axes, itineraries):
    timestamps = itinerary["timestamps"]
    valence = itinerary["valence"]
    arousal = itinerary["arousal"]

    times = [datetime.strptime(t, "%H:%M") for t in timestamps]
    y_positions = [valence_to_y[v] for v in valence]
    colors = [color_map[a] for a in arousal]

    # Scatter points
    ax.scatter(times, y_positions, c=colors, s=60, zorder=3)

    # Connect points in pairs
    for i in range(0, len(times) - 1, 2):
        gradient_line(
            ax,
            [times[i], times[i + 1]],
            [y_positions[i], y_positions[i + 1]],
            colors[i],
            colors[i + 1],
        )

    # Annotate time labels (alternate by pair)
    for i, (t, y, label) in enumerate(zip(times, y_positions, timestamps)):
        pair_index = i // 2
        y_offset = 8 if pair_index % 2 == 0 else -12

        ax.annotate(
            label,
            (t, y),
            textcoords="offset points",
            xytext=(0, y_offset),
            ha="center",
            fontsize=8,
            alpha=0.8,
        )

    # Y-axis formatting
    ax.set_ylim(-0.5, 2.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["-1", "0", "1"])

    # Neutral line
    ax.axhline(1, linestyle="--", color="black", alpha=0.5)

    # Title per itinerary
    ax.set_title(itinerary["name"], loc="left", fontsize=10)

# X-axis formatting (only bottom subplot shows labels)
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate()

# Global labels
fig.supxlabel("Time of day")
fig.supylabel("Emotion valence")

# Global legend
for label, color in color_map.items():
    axes[0].scatter([], [], c=color, label=label)

fig.legend(
    title="Emotion arousal",
    loc="upper center",
    bbox_to_anchor=(0.93, 0.5),
    frameon=True,
)

plt.tight_layout(rect=[0, 0, 0.88, 1])
plt.show()
