import json
import sys
sys.path.append('solution')
from race_simulator import simulate_race
from constants import TIRE_PARAMS, TEMP_REF, TEMP_SENSITIVITY

def compare_two():
    with open('data/test_cases/inputs/test_001.json', 'r') as f:
        test_case = json.load(f)
    
    # We'll use a modified simulate_race that returns times
    def get_times(race_data):
        race_config = race_data["race_config"]
        total_laps = race_config["total_laps"]
        base_lap_time = race_config["base_lap_time"]
        pit_lane_time = race_config["pit_lane_time"]
        track_temp = race_config["track_temp"]
        times = {}
        for pos_key, strategy in race_data["strategies"].items():
            driver_id = strategy["driver_id"]
            current_tire = strategy["starting_tire"]
            pit_stops = {stop["lap"]: stop["to_tire"] for stop in strategy["pit_stops"]}
            total_time = 0.0
            tire_age = 0
            for lap in range(1, total_laps + 1):
                tire_age += 1
                p = TIRE_PARAMS[current_tire]
                degrad = max(0, tire_age - p["grace"]) * p["rate"]
                temp_m = 1.0 + TEMP_SENSITIVITY * (track_temp - TEMP_REF)
                lap_time = base_lap_time + p["offset"] + (degrad * temp_m)
                total_time += lap_time
                if lap in pit_stops:
                    total_time += pit_lane_time
                    current_tire = pit_stops[lap]
                    tire_age = 0
            times[driver_id] = total_time
        return times

    times = get_times(test_case)
    print(f"D009 (M18->H): {times['D009']:.6f}")
    print(f"D019 (S8->H): {times['D019']:.6f}")
    print(f"Diff (D009 - D019): {times['D009'] - times['D019']:.6f}")

if __name__ == "__main__":
    compare_two()
