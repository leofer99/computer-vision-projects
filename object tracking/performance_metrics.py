import json
import os
import numpy as np

def analyze_operations(events):

    pick_ups = events.get("pick_up", [])
    places = events.get("place_in_box", [])
    probes = events.get("probe_pass", [])
    markings = events.get("marking", [])

    num_ops = min(len(pick_ups), len(places))
    durations = []
    ops_with_probe = 0
    ops_with_mark = 0

    for i in range(num_ops):
        start = pick_ups[i]
        end = places[i]
        durations.append(end - start)

        # Check if a probe happened between pick_up and place_in_box
        if any(start < p < end for p in probes):
            ops_with_probe += 1

        # Check if a marking happened between pick_up and place_in_box
        if any(start < m < end for m in markings):
            ops_with_mark += 1

    avg_duration = np.mean(durations) if durations else 0
    percent_probe = (ops_with_probe / num_ops) * 100 if num_ops > 0 else 0
    percent_mark = (ops_with_mark / num_ops) * 100 if num_ops > 0 else 0

    print("\n--- Operation Analysis ---")
    print(f"Total operations: {num_ops}")
    print(f"Average operation duration: {avg_duration:.2f} s")
    print(f"Operations with probe pass: {ops_with_probe}/{num_ops} ({percent_probe:.1f}%)")
    print(f"Operations with marking: {ops_with_mark}/{num_ops} ({percent_mark:.1f}%)")


folder_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
events_path = os.path.join(folder_dir, "detected_events.json")

with open(events_path, "r") as f:
    events = json.load(f)

# Example usage:

# events = {
# "pick_up": [5.63, 9.90, 13.9, 17.9, 22.77, 27.07, 31.9, 35.83, 40.87, 46.43, 50.23],
# "probe_pass": [6.53, 10.5, 14.3, 23.63, 26.8, 31.67, 36.7, 43.23, 47.2, 51.73],
# "marking": [7.57, 11.37, 16.13, 25.53, 29.33, 33.27, 36.67, 39.43, 44.9, 48.77, 51.17, 53.43],
# "place_in_box": [8.97, 12.8, 16.77, 19.2, 26.83, 31.7, 34.77, 39.97, 45.53, 49.37, 53.97],
# }

analyze_operations(events)
