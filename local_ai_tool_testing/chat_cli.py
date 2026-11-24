# -*- coding: utf-8 -*-
"""
Terminal CLI Chat with local Qwen 2.5 + ai-chart-toolkit
"""

import os
import sys
import json
import urllib.request

TOOLKIT_LOCAL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_chart_toolkit"))
if os.path.exists(TOOLKIT_LOCAL) and TOOLKIT_LOCAL not in sys.path:
    sys.path.insert(0, TOOLKIT_LOCAL)

try:
    from ai_chart_toolkit import execute_chart_tool, get_openai_tool_schema
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from chart_tool import execute_chart_tool
    import tool_schemas
    def get_openai_tool_schema():
        return tool_schemas.get_openai_tool_schema()

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "generated_charts"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 65)
    print("  Local Qwen 2.5 + AI Chart Toolkit CLI Tester")
    print(f"  Model: {MODEL_NAME} (Offline & Free)")
    print(f"  Output Directory: {OUTPUT_DIR}")
    print("  Type 'exit' or 'quit' to end.")
    print("=" * 65)

    tools = get_openai_tool_schema()
    history = [
        {"role": "system", "content": (
            "You are an expert visual system designer with access to the 'generate_chart' tool. "
            "When the user asks for a chart, diagram, flowchart, gauge, rings, or architecture, ALWAYS invoke the 'generate_chart' tool."
        )}
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting.")
                break

            history.append({"role": "user", "content": user_input})

            req_payload = {
                "model": MODEL_NAME,
                "messages": history,
                "tools": tools,
                "stream": False,
                "options": {"temperature": 0.2}
            }
            req_data = json.dumps(req_payload).encode("utf-8")
            req = urllib.request.Request(
                f"{OLLAMA_HOST}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )

            print("Thinking and generating chart...", end="", flush=True)
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            print("\r" + " " * 35 + "\r", end="")

            msg = resp_data.get("message", {})
            tool_calls = msg.get("tool_calls", [])

            if tool_calls:
                for call in tool_calls:
                    fn = call.get("function", {})
                    fn_args = fn.get("arguments", {})
                    if isinstance(fn_args, str):
                        fn_args = json.loads(fn_args)

                    chart_type = fn_args.pop("chart_type", "flowchart")
                    fn_args["output_dir"] = OUTPUT_DIR

                    print(f"\n[Tool Execution] Generating {chart_type.upper()} chart...")
                    result = execute_chart_tool(chart_type, fn_args)
                    if result.get("success"):
                        print(f"  -> File saved: {result['output_path']}")
                        print(f"  -> Dimensions: {result['dimensions']['width']}x{result['dimensions']['height']} (16:9)")
                    else:
                        print(f"  -> Error: {result.get('error')}")

            content = msg.get("content", "")
            if content:
                print(f"\nQwen: {content}")
                history.append({"role": "assistant", "content": content})

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
