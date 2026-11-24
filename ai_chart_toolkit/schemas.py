# -*- coding: utf-8 -*-
"""
ai_chart_toolkit.schemas
Pre-built JSON function schemas for:
- OpenAI, Ollama, vLLM, LM Studio (tools parameter)
- Anthropic Claude (tools / input_schema parameter)
- Google Gemini (function_declarations parameter)
"""

import json
from typing import Dict, Any, List

UNIFIED_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "generate_chart",
    "description": "Generates high-resolution 16:9 visual diagrams and charts including workflows/flowcharts, hierarchy architecture trees, donut/pie charts, concentric telemetry rings, and radial gauges. Saves image to disk and returns the file path.",
    "parameters": {
        "type": "object",
        "properties": {
            "chart_type": {
                "type": "string",
                "enum": ["flowchart", "hierarchy", "donut", "pie", "rings", "gauge"],
                "description": "The type of visual diagram to generate."
            },
            "title": {
                "type": "string",
                "description": "Main heading text displayed prominently at the top."
            },
            "subtitle": {
                "type": "string",
                "description": "Optional secondary descriptive subtitle beneath the heading."
            },
            "theme": {
                "type": "string",
                "enum": ["default", "dark"],
                "description": "Color theme for canvas and cards ('default' for clean blueprint/light, 'dark' for deep navy)."
            },
            "output_path": {
                "type": "string",
                "description": "Optional explicit output PNG path (e.g., 'output/my_diagram.png')."
            },
            "stages": {
                "type": "array",
                "description": "Used when chart_type is 'flowchart'. List of stages, each containing a 'header' and 'blocks' list.",
                "items": {
                    "type": "object",
                    "properties": {
                        "header": {"type": "string", "description": "Column header name (e.g., 'INGESTION', 'AI BRAIN', 'ACTUATION')."},
                        "blocks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string", "description": "Text label inside the block."},
                                    "type": {
                                        "type": "string",
                                        "enum": ["input", "ai_model", "tool", "data_store", "output"],
                                        "description": "Block category determining its semantic color."
                                    }
                                },
                                "required": ["label"]
                            }
                        }
                    },
                    "required": ["header", "blocks"]
                }
            },
            "root_node": {
                "type": "object",
                "description": "Used when chart_type is 'hierarchy'. Root node of the tree with recursive 'children' array.",
                "properties": {
                    "name": {"type": "string", "description": "Node title."},
                    "desc": {"type": "string", "description": "Node subtitle or description."},
                    "color": {"type": "string", "description": "Hex background color (optional)."},
                    "text_color": {"type": "string", "description": "Hex text color (optional)."},
                    "children": {
                        "type": "array",
                        "description": "List of child nodes with identical structure."
                    }
                },
                "required": ["name"]
            },
            "data": {
                "type": "array",
                "description": "Used when chart_type is 'donut' or 'pie'. List of data slices.",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "description": "Slice label (e.g., 'Compute', 'Sensors')."},
                        "value": {"type": "number", "description": "Numeric value for slice proportion."},
                        "color": {"type": "string", "description": "Optional hex color."}
                    },
                    "required": ["label", "value"]
                }
            },
            "center_text": {
                "type": "string",
                "description": "Used when chart_type is 'donut'. Hero KPI text inside center hole (e.g., '94.2%', '$1.2M')."
            },
            "center_sub": {
                "type": "string",
                "description": "Used when chart_type is 'donut'. Small label underneath center_text (e.g., 'Efficiency', 'Total Budget')."
            },
            "metrics": {
                "type": "array",
                "description": "Used when chart_type is 'rings'. List of circular progress rings (0-100%).",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "description": "Metric name (e.g., 'CPU Load', 'RAM Usage')."},
                        "pct": {"type": "number", "description": "Percentage value between 0 and 100."},
                        "color": {"type": "string", "description": "Optional hex color."}
                    },
                    "required": ["label", "pct"]
                }
            },
            "value": {
                "type": "number",
                "description": "Used when chart_type is 'gauge'. Current needle value."
            },
            "min_val": {
                "type": "number",
                "description": "Used when chart_type is 'gauge'. Minimum gauge scale tick (default: 0)."
            },
            "max_val": {
                "type": "number",
                "description": "Used when chart_type is 'gauge'. Maximum gauge scale tick (default: 100)."
            },
            "unit": {
                "type": "string",
                "description": "Used when chart_type is 'gauge'. Unit text (e.g., '°C Temp', 'km/h', '%')."
            }
        },
        "required": ["chart_type", "title"]
    }
}

def get_openai_tool_schema() -> List[Dict[str, Any]]:
    """Returns OpenAI / Ollama compatible tools list."""
    return [
        {
            "type": "function",
            "function": UNIFIED_TOOL_SCHEMA
        }
    ]

def get_claude_tool_schema() -> List[Dict[str, Any]]:
    """Returns Anthropic Claude tools list."""
    return [
        {
            "name": UNIFIED_TOOL_SCHEMA["name"],
            "description": UNIFIED_TOOL_SCHEMA["description"],
            "input_schema": UNIFIED_TOOL_SCHEMA["parameters"]
        }
    ]

def get_gemini_tool_schema() -> List[Dict[str, Any]]:
    """Returns Google Gemini function declarations list."""
    return [
        {
            "name": UNIFIED_TOOL_SCHEMA["name"],
            "description": UNIFIED_TOOL_SCHEMA["description"],
            "parameters": UNIFIED_TOOL_SCHEMA["parameters"]
        }
    ]
