from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os

app = FastAPI()


# Define the data model for the request
class ScriptRequest(BaseModel):
    code: str


@app.post("/execute")
def execute_script(request: ScriptRequest):
    """
    Receives Python code, saves it, executes it, and returns the output.
    """
    filename = "generated_test_script.py"

    try:
        # 1. Save the code to a file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(request.code)

        # 2. Run the file as a subprocess
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=60
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

# To run this: uvicorn backend:app --reload