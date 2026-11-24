# -*- coding: utf-8 -*-
"""
ai-chart-toolkit - Universal Blueprint & Visual Diagram Generator for AI Agents
Supports flowcharts, hierarchy architecture trees, donut charts, pie charts,
concentric telemetry rings, and precision radial gauges.
"""

__version__ = "1.0.1"

from .engine import (
    generate_flowchart,
    generate_hierarchy_chart,
    generate_pie_chart,
    generate_circular_rings,
    generate_circular_gauge,
    PALETTES
)
from .tool import execute_chart_tool
from .schemas import (
    UNIFIED_TOOL_SCHEMA,
    get_openai_tool_schema,
    get_claude_tool_schema,
    get_gemini_tool_schema
)

__all__ = [
    "generate_flowchart",
    "generate_hierarchy_chart",
    "generate_pie_chart",
    "generate_circular_rings",
    "generate_circular_gauge",
    "execute_chart_tool",
    "UNIFIED_TOOL_SCHEMA",
    "get_openai_tool_schema",
    "get_claude_tool_schema",
    "get_gemini_tool_schema",
    "PALETTES",
    "__version__"
]
