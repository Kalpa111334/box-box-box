import json

# Current base constants
PARAMS = {
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
        total += base_lap_time + p["offset"] + (max(0, age - p["grace"]) * p["rate"] * temp_m)
        if lap in stops:
            total += pit_penalty
            curr = stops[lap]
            age = 0
    return total

def main():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        races = json.load(f)
    
    temp_30 = [r for r in races if r["race_config"]["track_temp"] == 30]
    print(f"Found {len(temp_30)} races at 30°C")
    
    passed = 0
    for r in temp_30:
        res = []
        config = r["race_config"]
        for k, strat in r["strategies"].items():
            t = simulate_fast(config["total_laps"], config["base_lap_time"], config["pit_lane_time"], 30, strat, PARAMS, 0)
            res.append((t, int(k[3:]), strat["driver_id"]))
        
        sim_order = [x[2] for x in sorted(res)]
        if sim_order == r["finishing_positions"]:
            passed += 1
        else:
            print(f"FAILED: {r['race_id']}")
            
    print(f"Passed: {passed}/{len(temp_30)}")

if __name__ == "__main__":
    main()
