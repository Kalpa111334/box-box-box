import json
import os
import random

STATE_FILE = "tmp_calibration_tests.json"

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

def get_total_score(tests, params, s_sens):
    total_inversions = 0
    for test_case, expected_pos in tests:
        config = test_case["race_config"]
        exp_rank = {id: i for i, id in enumerate(expected_pos)}
        sim_times = []
        for k, strat in test_case["strategies"].items():
            t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], config["track_temp"], strat, params, s_sens)
            # Tie break by grid position
            sim_times.append((round(t, 8), int(k[3:]), strat["driver_id"]))
        sim_order = [x[2] for x in sorted(sim_times)]
        for i in range(20):
            for j in range(i+1, 20):
                if exp_rank[sim_order[i]] > exp_rank[sim_order[j]]:
                    total_inversions += 1
    return total_inversions

def main():
    tests = []
    for i in range(1, 11):
        in_p, out_p = f"data/test_cases/inputs/test_{i:03d}.json", f"data/test_cases/expected_outputs/test_{i:03d}.json"
        if os.path.exists(in_p):
            with open(in_p) as f: in_d = json.load(f)
            with open(out_p) as f: out_d = json.load(f)["finishing_positions"]
            tests.append((in_d, out_d))
            
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            s = json.load(f)
            best_p, best_sens, best_score = s["params"], s["sens"], s["score"]
    else:
        best_p = {"SOFT": {"offset": -1.3, "grace": 7, "rate": 0.12}, "MEDIUM": {"offset": 0.0, "grace": 12, "rate": 0.04}, "HARD": {"offset": 1.2, "grace": 20, "rate": 0.012}}
        best_sens, best_score = 0.015, 1000000
    
    for _ in range(2000): # Do small batches
        tp, ts = {k: v.copy() for k, v in best_p.items()}, best_sens
        r = random.random()
        if r < 0.2: ts = max(0, ts + random.uniform(-0.002, 0.002))
        elif r < 0.5:
            c = random.choice(["SOFT", "MEDIUM", "HARD"])
            if random.random() < 0.3: tp[c]["grace"] = max(1, tp[c]["grace"] + random.choice([-1, 1]))
            else: tp[c]["rate"] = max(0.001, round(tp[c]["rate"] + random.uniform(-0.005, 0.005), 4))
        else:
            c = random.choice(["SOFT", "MEDIUM", "HARD"])
            if c != "MEDIUM": tp[c]["offset"] = round(tp[c]["offset"] + random.uniform(-0.02, 0.02), 4)

        score = get_total_score(tests, tp, ts)
        if score < best_score:
            best_score, best_p, best_sens = score, tp, ts
            print(f"Score {score}, Sens {best_sens:.4f}")
            with open(STATE_FILE, "w") as f: json.dump({"params": best_p, "sens": best_sens, "score": best_score}, f)
            if score == 0: break

if __name__ == "__main__":
    main()
