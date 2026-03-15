import json
import random

# Optimized simulation for calibration
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

def main():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        all_races = json.load(f)
    
    races = all_races[:10]
    
    best_p = {
        "SOFT": {"offset": -1.2, "grace": 8, "rate": 0.08},
        "MEDIUM": {"offset": 0.0, "grace": 12, "rate": 0.03},
        "HARD": {"offset": 0.8, "grace": 20, "rate": 0.01}
    }
    best_s = 0.01
    
    def get_score(p, s):
        score = 0
        for r in races:
            config = r["race_config"]
            res = []
            for k, strat in r["strategies"].items():
                t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], config["track_temp"], strat, p, s)
                res.append((t, int(k[3:]), strat["driver_id"]))
            
            sim_order = [x[2] for x in sorted(res)]
            act_order = r["finishing_positions"]
            rank = {id: i for i, id in enumerate(act_order)}
            for i in range(20):
                for j in range(i+1, 20):
                    if rank[sim_order[i]] > rank[sim_order[j]]:
                        score += 1
        return score

    best_score = get_score(best_p, best_s)
    print(f"Start: {best_score}")
    
    for i in range(1000):
        # Mutate
        c = random.choice(["SOFT", "MEDIUM", "HARD", "SENS"])
        new_p = {k: v.copy() for k, v in best_p.items()}
        new_s = best_s
        
        if c == "SENS":
            new_s = max(0, best_s + random.uniform(-0.001, 0.001))
        else:
            attr = random.choice(["offset", "grace", "rate"])
            if attr == "offset":
                if c != "MEDIUM": new_p[c][attr] += random.uniform(-0.02, 0.02)
            elif attr == "grace":
                new_p[c][attr] = max(0, best_p[c][attr] + random.choice([-1, 1]))
            elif attr == "rate":
                new_p[c][attr] = max(0, best_p[c][attr] + random.uniform(-0.002, 0.002))
        
        score = get_score(new_p, new_s)
        if score <= best_score:
            best_score = score
            best_p, best_s = new_p, new_s
            if i % 100 == 0: print(f"Iter {i}, Score {score}")

    print(f"Final Score: {best_score}")
    print(json.dumps({"params": best_p, "sens": best_s}))

if __name__ == "__main__":
    main()
