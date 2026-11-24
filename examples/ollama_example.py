# -*- coding: utf-8 -*-
"""
Example: Local LLM tool calling using Ollama and ai-chart-toolkit
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import requests
from ai_chart_toolkit import execute_chart_tool, get_openai_tool_schema

def run_local_ollama_example():
    # 1. Fetch OpenAI-compatible function schema
    tools = get_openai_tool_schema()

    # 2. Send prompt to local Ollama instance (default port 11434)
    print("Sending prompt to Ollama...")
    try:
        resp = requests.post("http://localhost:11434/api/chat", json={
            "model": "qwen2.5:latest", # or llama3.2, mistral
            "messages": [
                {"role": "user", "content": "Generate a visual gauge chart showing server CPU temperature at 73.4 degrees Celsius with warning zones."}
            ],
            "tools": tools,
            "stream": False
        }, timeout=30)
        resp_data = resp.json()
    except Exception as e:
        print(f"Could not connect to Ollama: {e}")
        print("Falling back to simulated tool call payload:")
        resp_data = {
            "message": {
                "tool_calls": [
                    {
                        "function": {
                            "name": "generate_chart",
                            "arguments": {
                                "chart_type": "gauge",
                                "title": "Server CPU Temperature",
                                "value": 73.4,
                                "min_val": 0,
                                "max_val": 100,
                                "unit": "°C Temp"
                            }
                        }
                    }
                ]
            }
        }

    tool_calls = resp_data.get("message", {}).get("tool_calls", [])
    for call in tool_calls:
        fn = call.get("function", {})
        args = fn.get("arguments", {})
        if isinstance(args, str):
            args = json.loads(args)

        chart_type = args.pop("chart_type", "gauge")
        print(f"Executing tool call: {chart_type} with arguments: {args}")
        result = execute_chart_tool(chart_type, args)
        print("Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    run_local_ollama_example()
