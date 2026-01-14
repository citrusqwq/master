import csv
import numpy as np
from sklearn.metrics import cohen_kappa_score

input_csv = "Sim_eval_results.csv"

# Read CSV
with open(input_csv, newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

# Extract annotator rows (skip header)
annotator1 = np.array(rows[1], dtype=int)
annotator2 = np.array(rows[2], dtype=int)

# Mask out any item where either annotator gave -1
valid_mask = (annotator1 != -1) & (annotator2 != -1)

a1_clean = annotator1[valid_mask]
a2_clean = annotator2[valid_mask]

if len(a1_clean) == 0:
    raise ValueError("No valid ratings left after removing -1s.")

# Compute weighted Cohen’s kappa (quadratic)
kappa = cohen_kappa_score(a1_clean, a2_clean, weights="quadratic")

# Compute overall mean rating
overall_mean = np.mean(np.concatenate([a1_clean, a2_clean]))
mad = np.mean(np.abs(a1_clean - a2_clean))


print(f"Number of evaluated items: {len(a1_clean)}")
print(f"Weighted Cohen’s κ (quadratic): {kappa:.3f}")
print(f"Overall mean rating: {overall_mean:.3f}")
print(f"Mean absolute difference: {mad:.3f}")
