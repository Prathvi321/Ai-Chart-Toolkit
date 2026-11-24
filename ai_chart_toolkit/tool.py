# -*- coding: utf-8 -*-
"""
ai_chart_toolkit.tool
Unified tool calling dispatcher and CLI runner.
"""

import os
import sys
import json
import re
from typing import Dict, Any, Union

from .engine import (
    generate_flowchart,
    generate_hierarchy_chart,
    generate_pie_chart,
    generate_circular_rings,
    generate_circular_gauge,
    PALETTES
)

def slugify(title: str) -> str:
    """Generates a clean filesystem-friendly slug from title."""
    s = title.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')[:40] or "chart"

def execute_chart_tool(chart_type: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified entry point for AI Tool Calling.
    
    Args:
        chart_type: One of 'flowchart', 'hierarchy', 'donut', 'pie', 'rings', 'gauge'.
        arguments: Dictionary of parameters corresponding to the chart type.
        
    Returns:
        Structured dictionary indicating status, generated file path, and metadata.
    """
    chart_type = chart_type.lower().strip()
    title = arguments.get("title", "Generated Chart")
    subtitle = arguments.get("subtitle")
    theme = arguments.get("theme", "default")
    bg = arguments.get("background_path")
    width = arguments.get("width", 1672)
    height = arguments.get("height", 941)

    # Determine output path
    output_dir = arguments.get("output_dir", "output")
    os.makedirs(output_dir, exist_ok=True)

    explicit_path = arguments.get("output_path")
    if explicit_path:
        output_path = explicit_path
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    else:
        output_path = os.path.join(output_dir, f"{slugify(title)}_{chart_type}.png")

    try:
        if chart_type in ["flowchart", "workflow", "pipeline"]:
            stages = arguments.get("stages")
            if not stages:
                return {"success": False, "error": "Missing required 'stages' list for flowchart."}
            show_legend = arguments.get("show_legend", True)
            generate_flowchart(
                title=title,
                subtitle=subtitle,
                stages=stages,
                output_path=output_path,
                background_path=bg,
                theme=theme,
                width=width,
                height=height,
                show_legend=show_legend
            )

        elif chart_type in ["hierarchy", "tree", "org"]:
            root_node = arguments.get("root_node")
            if not root_node:
                return {"success": False, "error": "Missing required 'root_node' object for hierarchy chart."}
            generate_hierarchy_chart(
                title=title,
                subtitle=subtitle,
                root_node=root_node,
                output_path=output_path,
                background_path=bg,
                theme=theme,
                width=width,
                height=height
            )

        elif chart_type in ["donut", "pie"]:
            data = arguments.get("data")
            if not data:
                return {"success": False, "error": "Missing required 'data' list for pie/donut chart."}
            is_donut = (chart_type == "donut") or arguments.get("is_donut", True)
            center_text = arguments.get("center_text")
            center_sub = arguments.get("center_sub")
            generate_pie_chart(
                title=title,
                subtitle=subtitle,
                data=data,
                output_path=output_path,
                is_donut=is_donut,
                center_text=center_text,
                center_sub=center_sub,
                background_path=bg,
                theme=theme,
                width=width,
                height=height
            )

        elif chart_type in ["rings", "circular_rings", "activity_rings"]:
            metrics = arguments.get("metrics")
            if not metrics:
                return {"success": False, "error": "Missing required 'metrics' list for circular rings."}
            generate_circular_rings(
                title=title,
                subtitle=subtitle,
                metrics=metrics,
                output_path=output_path,
                background_path=bg,
                theme=theme,
                width=width,
                height=height
            )

        elif chart_type in ["gauge", "radial_gauge", "meter"]:
            if "value" not in arguments:
                return {"success": False, "error": "Missing required 'value' for radial gauge."}
            value = float(arguments["value"])
            min_val = float(arguments.get("min_val", 0))
            max_val = float(arguments.get("max_val", 100))
            unit = str(arguments.get("unit", "%"))
            zones = arguments.get("zones")
            generate_circular_gauge(
                title=title,
                subtitle=subtitle,
                value=value,
                min_val=min_val,
                max_val=max_val,
                unit=unit,
                zones=zones,
                output_path=output_path,
                background_path=bg,
                theme=theme,
                width=width,
                height=height
            )

        else:
            return {
                "success": False,
                "error": f"Unknown chart_type '{chart_type}'. Choose from: 'flowchart', 'hierarchy', 'donut', 'pie', 'rings', 'gauge'."
            }

        abs_path = os.path.abspath(output_path)
        file_size = os.path.getsize(abs_path) if os.path.exists(abs_path) else 0

        return {
            "success": True,
            "chart_type": chart_type,
            "title": title,
            "output_path": output_path,
            "absolute_path": abs_path,
            "file_size_bytes": file_size,
            "dimensions": {"width": width, "height": height},
            "message": f"Successfully generated {chart_type} chart saved to: {output_path}"
        }

    except Exception as e:
        return {
            "success": False,
            "chart_type": chart_type,
            "error": str(e),
            "error_type": type(e).__name__
        }

def main():
    """CLI runner for terminal agents, local LLMs, and bash tool calls."""
    raw_input = None

    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ["--help", "-h"]:
            print("ai-chart - Universal Visual Diagram Tool for AI Agents")
            print("\nUsage:")
            print("  ai-chart '{\"chart_type\": \"gauge\", \"title\": \"CPU Temp\", \"value\": 72.5, \"unit\": \"°C\"}'")
            print("  ai-chart --file spec.json")
            print("  cat spec.json | ai-chart")
            sys.exit(0)
        elif arg in ["--file", "-f"] and len(sys.argv) > 2:
            with open(sys.argv[2], "r", encoding="utf-8-sig") as f:
                raw_input = f.read()
        elif arg.startswith("{") or arg.startswith("'") or arg.startswith('"'):
            raw_input = arg

    if not raw_input and not sys.stdin.isatty():
        raw_input = sys.stdin.read().strip()

    if raw_input:
        raw_input = raw_input.lstrip("\ufeff").strip()

    if not raw_input:
        print(json.dumps({
            "success": False,
            "error": "No input JSON provided. Pass JSON as argument, via --file, or via stdin.",
            "usage": "ai-chart '{\"chart_type\": \"donut\", \"title\": \"Cost\", \"data\": [{\"label\": \"A\", \"value\": 10}]}'"
        }, indent=2))
        sys.exit(1)

    try:
        spec = json.loads(raw_input)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    chart_type = spec.pop("chart_type", spec.pop("type", "flowchart"))
    result = execute_chart_tool(chart_type, spec)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)

if __name__ == "__main__":
    main()
