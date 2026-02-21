from __future__ import annotations

import os
import subprocess

BASH_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "Bash",
        "description": "Execute a shell command",
        "parameters": {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute",
                }
            },
        },
    },
}


def run_bash_command(command: str) -> str:
    completed = subprocess.run(
        command,
        shell=True,
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    if completed.returncode != 0:
        return (
            f"Command failed with exit code {completed.returncode}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )

    # Return combined output (can be empty on success)
    return stdout + stderr
