import argparse
import json
import os
import sys

from app.read_tool import READ_TOOL_SPEC, read_file_bytes

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
        tools=[READ_TOOL_SPEC],
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    message = chat.choices[0].message

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        tool_call = tool_calls[0]
        function = tool_call.function
        function_name = function.name
        function_args = json.loads(function.arguments or "{}")

        if function_name != "Read":
            raise RuntimeError(f"unsupported tool: {function_name}")

        file_path = function_args["file_path"]
        sys.stdout.buffer.write(read_file_bytes(file_path))
        return

    print(message.content)


if __name__ == "__main__":
    main()
