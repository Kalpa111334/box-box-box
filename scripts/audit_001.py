import json
import sys
sys.path.append('solution')
from constants import TIRE_PARAMS, TEMP_REF, TEMP_SENSITIVITY

def debug_all():
    with open('data/test_cases/inputs/test_001.json', 'r') as f:
        test_case = json.load(f)
    with open('data/test_cases/expected_outputs/test_001.json', 'r') as f:
        expected = json.load(f)
    expected_pos = expected['finishing_positions']
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
    print(f"{'Pos':<3} {'ID':<5} {'Time':<12} {'Match'}")
    for i in range(20):
        res = results[i]
        match = "✓" if res["id"] == expected_pos[i] else f"✗ exp:{expected_pos[i]}"
        print(f"{i+1:<3} {res['id']:<5} {res['time']:<12.6f} {match}")

if __name__ == "__main__":
    debug_all()
