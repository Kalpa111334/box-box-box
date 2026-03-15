import json
import random
import os

STATE_FILE = "tmp_calibration_state.json"

def simulate_fast(total_laps, base_lap_time, pit_penalty, strategy, params):
    curr = strategy["starting_tire"]
    stops = {s["lap"]: s["to_tire"] for s in strategy["pit_stops"]}
    total = 0.0
    age = 0
    for lap in range(1, total_laps + 1):
        age += 1
        p = params[curr]
        total += base_lap_time + p["offset"] + (max(0, age - p["grace"]) * p["rate"])
        if lap in stops:
            total += pit_penalty
            curr = stops[lap]
            age = 0
    return total

def get_score(races, params):
    score = 0
    for r in races:
        config = r["race_config"]
        act_order = r["finishing_positions"]
        act_rank = {id: i for i, id in enumerate(act_order)}
        
        sim_times = []
        for k, strat in r["strategies"].items():
            t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], strat, params)
            sim_times.append((round(t, 8), int(k[3:]), strat["driver_id"]))
        
        sim_order = [x[2] for x in sorted(sim_times)]
        
        for i in range(20):
            for j in range(i+1, 20):
                if act_rank[sim_order[i]] > act_rank[sim_order[j]]:
                    score += 1
    return score

def main():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        all_races = json.load(f)
    races = [r for r in all_races if r["race_config"]["track_temp"] == 30]
    
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            best_p = state["params"]
            best_score = state["score"]
    else:
        best_p = {
            "SOFT": {"offset": -1.3, "grace": 6, "rate": 0.11},
            "MEDIUM": {"offset": 0.0, "grace": 10, "rate": 0.03},
            "HARD": {"offset": 1.1, "grace": 20, "rate": 0.01}
        }
        best_score = get_score(races, best_p)
    
    print(f"Start Score: {best_score}")
    
    for i in range(500): # Do small batches
        c = random.choice(["SOFT", "MEDIUM", "HARD"])
        attr = random.choice(["offset", "grace", "rate"])
        new_p = {k: v.copy() for k, v in best_p.items()}
        
        if attr == "offset":
            if c != "MEDIUM": new_p[c][attr] += random.choice([-0.01, 0.01])
        elif attr == "grace":
            new_p[c][attr] = max(0, best_p[c][attr] + random.choice([-1, 1]))
        elif attr == "rate":
            new_p[c][attr] = max(0, round(best_p[c][attr] + random.choice([-0.001, 0.001]), 4))
            
        score = get_score(races, new_p)
        if score < best_score:
            best_score = score
            best_p = new_p
            print(f"Improvement: {score}")
            with open(STATE_FILE, "w") as f:
                json.dump({"params": best_p, "score": best_score}, f)
            if score == 0: break

    print(f"Batch Done. Best Score: {best_score}")

if __name__ == "__main__":
    main()
