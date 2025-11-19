import subprocess
import sys
import os


def execute_selenium_code(code_string):
    """
    Saves the generated code to a temporary file and executes it.
    Returns a dictionary with:
    - success: Boolean
    - output: Captured stdout
    - error: Captured stderr
    """
    filename = "generated_test_script.py"

    try:
        # 1. Save the code to a file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_string)

        # 2. Run the file as a subprocess
        # We use sys.executable to ensure we use the same Python environment (and dependencies) as the app
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=60  # Safety timeout (1 minute)
        )

        # 3. Return the results
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Error: The test timed out (took longer than 60 seconds)."
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"System Error: {str(e)}"
        }