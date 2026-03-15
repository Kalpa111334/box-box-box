import json
import subprocess
import os
import glob
import sys

def run_test(test_input_path, expected_output_path, run_command):
    try:
        with open(test_input_path, 'r') as f:
            input_data = f.read()
            
        process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        stdout, stderr = process.communicate(input=input_data)
        
        if process.returncode != 0:
            return False, f"Execution Error: {stderr.strip()}"
            
        try:
            actual_output = json.loads(stdout)
        except json.JSONDecodeError:
            return False, f"Invalid JSON Output: {stdout[:100]}..."
            
        with open(expected_output_path, 'r') as f:
            expected_output = json.load(f)
            
        actual_pos = actual_output.get("finishing_positions", [])
        expected_pos = expected_output.get("finishing_positions", [])
        
        if actual_pos == expected_pos:
            return True, "Passed"
        else:
            return False, "Incorrect Prediction"
            
    except Exception as e:
        return False, str(e)

def main():
    input_dir = "data/test_cases/inputs"
    expected_dir = "data/test_cases/expected_outputs"
    
    # Read run command
    with open("solution/run_command.txt", 'r') as f:
        run_command = f.read().strip()
        
    test_files = sorted(glob.glob(os.path.join(input_dir, "test_*.json")))
    
    if not test_files:
        print("No test files found.")
        return

    passed_count = 0
    failed_tests = []
    
    print(f"Running {len(test_files)} tests...")
    
    for test_file in test_files:
        test_name = os.path.basename(test_file)
        expected_file = os.path.join(expected_dir, test_name)
        
        if not os.path.exists(expected_file):
            print(f"Skipping {test_name}: Expected output not found.")
            continue
            
        success, message = run_test(test_file, expected_file, run_command)
        
        if success:
            passed_count += 1
            print(f"✓ {test_name}")
        else:
            failed_tests.append((test_name, message))
            print(f"✗ {test_name} - {message}")
            
    print("\n" + "="*40)
    print(f"Results: {passed_count}/{len(test_files)} passed")
    print(f"Accuracy: {(passed_count/len(test_files))*100:.1f}%")
    print("="*40)
    
    if failed_tests:
        print("\nFailed Tests:")
        for name, msg in failed_tests:
            print(f"- {name}: {msg}")
        sys.exit(1)
    else:
        print("\nAll tests passed successfully! 🏆")
        sys.exit(0)

if __name__ == "__main__":
    main()
