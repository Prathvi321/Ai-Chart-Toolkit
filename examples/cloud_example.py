# -*- coding: utf-8 -*-
"""
Example: Cloud LLMs (OpenAI, Anthropic Claude, Google Gemini) calling ai-chart-toolkit
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from ai_chart_toolkit import (
    execute_chart_tool,
    get_openai_tool_schema,
    get_claude_tool_schema,
    get_gemini_tool_schema
)

def demo_schema_exports():
    print("=== 1. OpenAI / Ollama Tool Schema ===")
    print(json.dumps(get_openai_tool_schema(), indent=2)[:300] + "...\n")

    print("=== 2. Claude Tool Schema ===")
    print(json.dumps(get_claude_tool_schema(), indent=2)[:300] + "...\n")

    print("=== 3. Gemini Function Declaration ===")
    print(json.dumps(get_gemini_tool_schema(), indent=2)[:300] + "...\n")

def demo_dispatch():
    sample_call = {
        "chart_type": "donut",
        "title": "Cloud Infrastructure Cost Breakdown",
        "center_text": "$14.2k",
        "center_sub": "Monthly Spend",
        "data": [
            {"label": "Compute (vCPU/GPU)", "value": 55},
            {"label": "NVMe Storage", "value": 25},
            {"label": "Networking & CDN", "value": 20}
        ]
    }
    chart_type = sample_call.pop("chart_type")
    res = execute_chart_tool(chart_type, sample_call)
    print("Generated Chart via Tool Call:", res["output_path"])

if __name__ == "__main__":
    demo_schema_exports()
    demo_dispatch()
