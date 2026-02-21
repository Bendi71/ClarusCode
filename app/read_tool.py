from __future__ import annotations

from pathlib import Path

READ_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "Read",
        "description": "Read and return the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read",
                }
            },
            "required": ["file_path"],
        },
    },
}


def read_file_bytes(file_path: str) -> bytes:
    return Path(file_path).read_bytes()