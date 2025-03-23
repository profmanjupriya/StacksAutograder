import os
import importlib.util
import traceback
import csv
import io
import contextlib

SUBMISSIONS_DIR = "submissions"
EXPECTED_OUTPUT_FILE = "expectedoutput.txt"
RESULTS_CSV = "autograder_results.csv"
LOG_FILE = "autograder_errors.log"
POINTS_TOTAL = 20
deductions = {
    "init": 2,
    "push": 4,
    "pop": 4,
    "peek": 3,
    "is_empty": 3,
    "size": 4,
}

# Load expected output
with open(EXPECTED_OUTPUT_FILE, "r") as f:
    expected_output = [line.strip() for line in f if line.strip()]

# Store output
results = [("Student", "Score")]
errors = []

def run_tests_on_stack(Stack):
    score = POINTS_TOTAL
    feedback = []
    buffer = io.StringIO()

    try:
        s = Stack()
    except Exception:
        score -= deductions["init"]
        feedback.append("init failed")
        return score, feedback, []

    try:
        with contextlib.redirect_stdout(buffer):
            print("PUSH: A")
            s.push("A")
            print("PUSH: B")
            s.push("B")
            print("PUSH: C")
            s.push("C")

            print("PEEK:", s.peek())
            print("POP:", s.pop())
            print("POP:", s.pop())
            print("ISEMPTY:", s.is_empty())
            print("SIZE:", s.size())
    except Exception as e:
        feedback.append(f"Runtime error: {str(e)}")
        score -= 5  # Generic deduction

    actual_output = [line.strip() for line in buffer.getvalue().splitlines() if line.strip()]

    # Compare outputs
    for i in range(min(len(expected_output), len(actual_output))):
        if expected_output[i] != actual_output[i]:
            feedback.append(f"Mismatch on line {i+1}")
            score -= 1

    if len(actual_output) < len(expected_output):
        missing = len(expected_output) - len(actual_output)
        score -= missing
        feedback.append(f"Missing {missing} lines of output")

    return max(score, 0), feedback, actual_output

# Run autograder on all submissions
for folder in os.listdir(SUBMISSIONS_DIR):
    path = os.path.join(SUBMISSIONS_DIR, folder)
    stacks_file = os.path.join(path, "Stack.py")
    if not os.path.isfile(stacks_file):
        errors.append(f"{folder}: stacks.py not found")
        results.append((folder, 0))
        continue

    module_name = f"{folder}_stack"
    spec = importlib.util.spec_from_file_location(module_name, stacks_file)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
        if not hasattr(module, "Stack"):
            results.append((folder, 0))
            errors.append(f"{folder}: Stack class not found")
            continue

        score, feedback, actual_output = run_tests_on_stack(module.Stack)
        results.append((folder, score))

        if feedback:
            errors.append(f"{folder} issues:")
            for f in feedback:
                errors.append(f"  - {f}")

    except Exception as e:
        errors.append(f"{folder}: {traceback.format_exc()}")
        results.append((folder, 0))

# Save results
with open(RESULTS_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(results)

with open(LOG_FILE, "w") as f:
    f.write("\n".join(errors))

print("✅ Autograding complete.")
print(f"📄 Results saved to: {RESULTS_CSV}")
print(f"🛠️  Errors saved to: {LOG_FILE}")