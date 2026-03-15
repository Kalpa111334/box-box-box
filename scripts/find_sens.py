import json
import os

# Original Calibrated constants
BASE_PARAMS = {
    "SOFT": {"offset": -1.3118, "grace": 6, "rate": 0.1084},
    "MEDIUM": {"offset": 0.0, "grace": 9, "rate": 0.0313},
    "HARD": {"offset": 1.0601, "grace": 18, "rate": 0.0098}
}

def simulate_fast(total_laps, base_lap_time, pit_penalty, temp, strategy, params, s_sens):
    curr = strategy["starting_tire"]
    stops = {s["lap"]: s["to_tire"] for s in strategy["pit_stops"]}
    total = 0.0
    age = 0
    temp_m = 1.0 + s_sens * (temp - 30.0)
    for lap in range(1, total_laps + 1):
        age += 1
        p = params[curr]
        lap_time = base_lap_time + p["offset"] + (max(0, age - p["grace"]) * p["rate"] * temp_m)
        total += lap_time
        if lap in stops:
            total += pit_penalty
            curr = stops[lap]
            age = 0
    return total

def check_pos(params, s_sens, test_case, expected):
    config = test_case["race_config"]
    res = []
    for k, strat in test_case["strategies"].items():
        t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], config["track_temp"], strat, params, s_sens)
        res.append((t, int(k[3:]), strat["driver_id"]))
    sim_pos = [x[2] for x in sorted(res)]
    return sim_pos == expected

def main():
    with open('data/test_cases/inputs/test_001.json', 'r') as f:
        test_case = json.load(f)
    with open('data/test_cases/expected_outputs/test_001.json', 'r') as f:
        expected = json.load(f)["finishing_positions"]
        
    for sens_int in range(0, 300): # 0.000 to 0.030
        sens = sens_int / 10000.0
        if check_pos(BASE_PARAMS, sens, test_case, expected):
            print(f"FOUND SENS: {sens}")
            return
    print("Not found in 0.000-0.030 range with step 0.0001")

if __name__ == "__main__":
    main()
