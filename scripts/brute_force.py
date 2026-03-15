import json
import os

def simulate_fast(total_laps, base_lap_time, pit_penalty, temp, strategy, params, s_sens):
    curr = strategy["starting_tire"]
    stops = {s["lap"]: s["to_tire"] for s in strategy["pit_stops"]}
    total = 0.0
    age = 0
    temp_m = 1.0 + s_sens * (temp - 30.0)
    for lap in range(1, total_laps + 1):
        age += 1
        p = params[curr]
        total += base_lap_time + p["offset"] + (max(0, age - p["grace"]) * p["rate"] * temp_m)
        if lap in stops:
            total += pit_penalty
            curr = stops[lap]
            age = 0
    return total

def check_test(id_num, params, s_sens):
    in_p = f"data/test_cases/inputs/test_{id_num:03d}.json"
    out_p = f"data/test_cases/expected_outputs/test_{id_num:03d}.json"
    with open(in_p) as f: test_case = json.load(f)
    with open(out_p) as f: expected_pos = json.load(f)["finishing_positions"]
    config = test_case["race_config"]
    results = []
    for k, strat in test_case["strategies"].items():
        t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], config["track_temp"], strat, params, s_sens)
        results.append((round(t, 8), int(k[3:]), strat["driver_id"]))
    results.sort()
    sim_order = [x[2] for x in results]
    return sim_order == expected_pos

def main():
    # Ranges centered around promising values
    s_offs = [-1.4, -1.35, -1.3, -1.25]
    h_offs = [1.1, 1.15, 1.2, 1.25]
    s_sens = [0.015, 0.0132, 0.01]
    
    for so in s_offs:
        for ho in h_offs:
            for s in s_sens:
                p = {
                    "SOFT": {"offset": so, "grace": 6, "rate": 0.12},
                    "MEDIUM": {"offset": 0.0, "grace": 11, "rate": 0.06},
                    "HARD": {"offset": ho, "grace": 22, "rate": 0.012}
                }
                if check_test(1, p, s) and check_test(2, p, s):
                    print(f"FOUND 100%! P: {json.dumps(p)}, Sens: {s}")
                    return
    print("Not found in small grid")

if __name__ == "__main__":
    main()
