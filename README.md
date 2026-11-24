# AI Chart Toolkit (`ai-chart-toolkit`)

Universal visual diagram and blueprint chart generator engineered for AI agents, local LLMs, and cloud APIs.

Generates high-resolution 16:9 images (1672 × 941) with blueprint grid styling, anti-aliased geometry, and dynamic typography.

Free for everyone to use, modify, and build upon.

---

## Supported Chart Types

1. **Dynamic Flowcharts**: Multi-stage pipelines, semantic block categories (`input`, `ai_model`, `tool`, `data_store`, `output`), and connector arrows.
2. **Hierarchy Architecture Trees**: Recursive multi-tier system tree maps with parent-child links.
3. **Precision Donut Charts**: Radial proportional distribution with large center KPI metrics (e.g., `"$12.4k"`, `"94%"`).
4. **Solid Pie Charts**: Proportional slices and automated legend percentage cards.
5. **Concentric Activity Rings**: Multi-tier telemetry progress rings (0–100%) with rounded caps.
6. **Precision Radial Gauges**: 240-degree dial gauge with threshold zones, status needle, and unit readout.

---

## Installation

Install directly via PyPI:
```bash
pip install ai-chart-toolkit
```

Or clone from GitHub:
```bash
git clone https://github.com/Prathvi321/Ai-Chart-Toolkit.git
cd Ai-Chart-Toolkit
pip install -e .
```

---

## 4 Ways to Use This Tool

### 1. Terminal / CLI for Autonomous Agents
```bash
ai-chart '{"chart_type": "gauge", "title": "GPU Temperature", "value": 67.5, "unit": "°C"}'
```

### 2. Native MCP Tool (Model Context Protocol)
Run the built-in MCP server for Claude Desktop, Cursor, or Antigravity:
```bash
ai-chart-mcp
```
Configuration in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ai-chart": {
      "command": "ai-chart-mcp"
    }
  }
}
```

### 3. Local REST API Server
```bash
ai-chart-api
```
Send requests:
```bash
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{"chart_type": "donut", "title": "Memory", "center_text": "16 GB", "data": [{"label": "Used", "value": 70}, {"label": "Free", "value": 30}]}'
```

### 4. Direct Python Import
```python
from ai_chart_toolkit import execute_chart_tool

res = execute_chart_tool("rings", {
    "title": "Node Health",
    "metrics": [
        {"label": "CPU", "pct": 74},
        {"label": "RAM", "pct": 58}
    ]
})
print("Saved to:", res["output_path"])
```

---

## Agent Skill File (`SKILL.md`)

This repository includes a standard `SKILL.md` compliant with Antigravity, Claude Code, and OpenAI Codex agent specifications. Agents automatically detect this file and understand when and how to generate diagrams.
