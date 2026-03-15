import json

def find_patterns():
    with open("data/historical_races/races_00000-00999.json", "r") as f:
        races = json.load(f)
    
    temp_30 = [r for r in races if r["race_config"]["track_temp"] == 30]
    
    for r in temp_30:
        strategies = r["strategies"]
        finishing = r["finishing_positions"]
        
        # Group drivers who stayed on their starting tire for at least X laps and didn't pit yet
        # Actually, let's just look at their Rank vs Pit Lap
        groups = {} # (starting_tire, to_tire) -> list of (pit_lap, rank)
        
        for pos, s in strategies.items():
            if len(s["pit_stops"]) >= 1:
                key = (s["starting_tire"], s["pit_stops"][0]["to_tire"])
                if key not in groups: groups[key] = []
                groups[key].append((s["pit_stops"][0]["lap"], finishing.index(s["driver_id"]), s["driver_id"]))
        
        for key, members in groups.items():
            if len(members) >= 3:
                members.sort()
                # Check if ranks are monotonically increasing with pit lap
                # This suggests no degradation yet
                # If they start decreasing, degradation hit!
                print(f"Race {r['race_id']} {key}:")
                for pit_lap, rank, dr in members:
                    print(f"  Lap {pit_lap}: Rank {rank+1} ({dr})")

if __name__ == "__main__":
    find_patterns()
