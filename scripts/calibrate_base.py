import json
import random

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
        res = []
        for k, strat in r["strategies"].items():
            t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], strat, params)
            res.append((round(t, 8), int(k[3:]), strat["driver_id"]))
        
        sim_order = [x[2] for x in sorted(res)]
        act_order = r["finishing_positions"]
        if sim_order != act_order:
            # Count rank inversions for a smoother gradient
            rank = {id: i for i, id in enumerate(act_order)}
            for i in range(20):
                for j in range(i+1, 20):
                    if rank[sim_order[i]] > rank[sim_order[j]]:
                        score += 1
    return score

def main():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        all_races = json.load(f)
    races = [r for r in all_races if r["race_config"]["track_temp"] == 30]
    print(f"Calibrating on {len(races)} races")
    
    # Starting values (informed by typical F1 sim patterns)
    best_p = {
        "SOFT": {"offset": -1.3, "grace": 6, "rate": 0.1},
        "MEDIUM": {"offset": 0.0, "grace": 12, "rate": 0.03},
        "HARD": {"offset": 1.1, "grace": 24, "rate": 0.01}
    }
    
    best_score = get_score(races, best_p)
    print(f"Start Score: {best_score}")
    
    for i in range(1000):
        c = random.choice(["SOFT", "MEDIUM", "HARD"])
        attr = random.choice(["offset", "grace", "rate"])
        new_p = {k: v.copy() for k, v in best_p.items()}
        
        if attr == "offset":
            if c != "MEDIUM": new_p[c][attr] += random.uniform(-0.02, 0.02)
        elif attr == "grace":
            new_p[c][attr] = max(0, best_p[c][attr] + random.choice([-1, 1]))
        elif attr == "rate":
            new_p[c][attr] = max(0, best_p[c][attr] + random.uniform(-0.002, 0.002))
            
        score = get_score(races, new_p)
        if score < best_score:
            best_score = score
            best_p = new_p
            print(f"Iter {i}, Score {score}")
            if score == 0: break

    print(f"Final Params: {json.dumps(best_p)}")
    print(f"Final Score: {best_score}")

if __name__ == "__main__":
    main()
