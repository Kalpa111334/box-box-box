import json
import sys
import os

# Add solution to path
sys.path.append('solution')
from race_simulator import simulate_race

def compare_test_001():
    with open('data/test_cases/inputs/test_001.json', 'r') as f:
        test_case = json.load(f)
    
    actual_pos = simulate_race(test_case)
    
    with open('data/test_cases/expected_outputs/test_001.json', 'r') as f:
        expected = json.load(f)
    expected_pos = expected['finishing_positions']
    
    print("Top 10 Comparison (Actual vs Expected):")
    for i in range(10):
        a = actual_pos[i]
        e = expected_pos[i]
        match = "✓" if a == e else "✗"
        print(f"Pos {i+1}: {a} vs {e} {match}")

if __name__ == "__main__":
    compare_test_001()
