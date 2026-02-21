import argparse
import json
import os
import sys

from app.read_tool import READ_TOOL_SPEC, read_file_bytes
from app.write_tool import WRITE_TOOL_SPEC, write_file_text

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

    messages: list[dict] = [{"role": "user", "content": args.p}]

    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[READ_TOOL_SPEC, WRITE_TOOL_SPEC],
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        choice = chat.choices[0]
        message = choice.message

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!", file=sys.stderr)

        assistant_msg: dict = {
            "role": "assistant",
            "content": message.content,
        }

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ]

        messages.append(assistant_msg)

        if not tool_calls:
            # Either finish_reason is "stop" or the model returned a plain message.
            if message.content is not None:
                print(message.content)
            return

        for tool_call in tool_calls:
            function = tool_call.function
            function_name = function.name
            function_args = json.loads(function.arguments or "{}")

            if function_name == "Read":
                file_path = function_args["file_path"]
                tool_output_bytes = read_file_bytes(file_path)
                tool_output_text = tool_output_bytes.decode("utf-8", errors="replace")
            elif function_name == "Write":
                file_path = function_args["file_path"]
                content = function_args["content"]
                write_file_text(file_path, content)
                tool_output_text = "OK"
            else:
                raise RuntimeError(f"unsupported tool: {function_name}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output_text,
                }
            )


if __name__ == "__main__":
    main()
