import json

def find_flip_lap():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        races = json.load(f)
    
    # Track: Monaco usually has many Soft starters
    for r in races:
        if r["race_config"]["track_temp"] != 30: continue
        strategies = r["strategies"]
        finishing = r["finishing_positions"]
        
        soft_pitters = []
        for pos, s in strategies.items():
            if s["starting_tire"] == "SOFT" and len(s["pit_stops"]) == 1:
                soft_pitters.append({
                    "id": s["driver_id"],
                    "pit_lap": s["pit_stops"][0]["lap"],
                    "to": s["pit_stops"][0]["to_tire"],
                    "rank": finishing.index(s["driver_id"])
                })
        
        # Group by 'to_tire'
        for to_tire in ["MEDIUM", "HARD"]:
            group = [p for p in soft_pitters if p["to"] == to_tire]
            if len(group) > 1:
                group.sort(key=lambda x: x["pit_lap"])
                print(f"Race {r['race_id']} Soft -> {to_tire}:")
                for p in group:
                    print(f"  Lap {p['pit_lap']}: Rank {p['rank']+1}")

if __name__ == "__main__":
    find_flip_lap()
