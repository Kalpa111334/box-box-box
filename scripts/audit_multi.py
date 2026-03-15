import json
import os
import sys
sys.path.append('solution')
from constants import TIRE_PARAMS, TEMP_REF, TEMP_SENSITIVITY

def debug_test(id_num):
    in_p = f"data/test_cases/inputs/test_{id_num:03d}.json"
    out_p = f"data/test_cases/expected_outputs/test_{id_num:03d}.json"
    with open(in_p) as f: test_case = json.load(f)
    with open(out_p) as f: expected_pos = json.load(f)["finishing_positions"]
    config = test_case["race_config"]
    results = []
    for k, strat in test_case["strategies"].items():
        curr = strat["starting_tire"]
        stops = {s["lap"]: s["to_tire"] for s in strat["pit_stops"]}
        total = 0.0
        age = 0
        temp_m = 1.0 + TEMP_SENSITIVITY * (config["track_temp"] - TEMP_REF)
        for lap in range(1, config["total_laps"] + 1):
            age += 1
            p = TIRE_PARAMS[curr]
            total += config["base_lap_time"] + p["offset"] + (max(0, age - p["grace"]) * p["rate"] * temp_m)
            if lap in stops:
                total += config["pit_lane_time"]
                curr = stops[lap]
                age = 0
        results.append({"id": strat["driver_id"], "time": total, "grid": int(k[3:])})
    results.sort(key=lambda x: (round(x["time"], 8), x["grid"]))
    print(f"--- TEST {id_num:03d} ({config['track_temp']}C) ---")
    correct = 0
    for i in range(20):
        res = results[i]
        match = "✓" if res["id"] == expected_pos[i] else f"✗ exp:{expected_pos[i]}"
        if res["id"] == expected_pos[i]: correct += 1
        if i < 10: print(f"{i+1:2d}. {res['id']:5s} {res['time']:12.6f} {match}")
    print(f"Total Correct: {correct}/20")

if __name__ == "__main__":
    debug_test(1)
    debug_test(2)
