import json
import os
import random

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
        in_path = f"data/test_cases/inputs/test_{i:03d}.json"
        out_path = f"data/test_cases/expected_outputs/test_{i:03d}.json"
        if os.path.exists(in_path) and os.path.exists(out_path):
            with open(in_path, "r") as f: in_data = json.load(f)
            with open(out_path, "r") as f: out_data = json.load(f)
            tests.append((in_data, out_data["finishing_positions"]))
    
    print(f"Loaded {len(tests)} test cases")
    
    # Grid search for grace periods first (integers)
    # SOFT: 5-8, MEDIUM: 8-15, HARD: 15-30
    best_p = {
        "SOFT": {"offset": -1.3118, "grace": 6, "rate": 0.1084},
        "MEDIUM": {"offset": 0.0, "grace": 11, "rate": 0.0313},
        "HARD": {"offset": 1.0601, "grace": 21, "rate": 0.0098}
    }
    best_sens = 0.0132
    best_score = get_total_score(tests, best_p, best_sens)
    
    print(f"Initial Score: {best_score}")
    
    for _ in range(2000):
        tp = {k: v.copy() for k, v in best_p.items()}
        ts = best_sens
        
        r = random.random()
        if r < 0.2:
            ts = max(0, best_sens + random.uniform(-0.001, 0.001))
        elif r < 0.5:
            c = random.choice(["SOFT", "MEDIUM", "HARD"])
            tp[c]["grace"] = max(1, tp[c]["grace"] + random.choice([-1, 1]))
        elif r < 0.8:
            c = random.choice(["SOFT", "MEDIUM", "HARD"])
            if c != "MEDIUM": tp[c]["offset"] += random.uniform(-0.01, 0.01)
        else:
            c = random.choice(["SOFT", "MEDIUM", "HARD"])
            tp[c]["rate"] = max(0, tp[c]["rate"] + random.uniform(-0.001, 0.001))
            
        score = get_total_score(tests, tp, ts)
        if score < best_score:
            best_score = score
            best_p = tp
            best_sens = ts
            print(f"Score {score}, Sens {best_sens:.4f}, P: {json.dumps(best_p)}")
            if score == 0: break

if __name__ == "__main__":
    main()
