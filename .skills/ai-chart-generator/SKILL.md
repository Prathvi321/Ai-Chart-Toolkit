---
name: ai-chart-generator
description: Generate high-resolution 16:9 visual diagrams, multi-stage flowcharts, hierarchy architecture trees, donut/pie charts, concentric telemetry activity rings, and precision radial performance gauges. Use whenever an agent or user requests blueprints, architecture visuals, process pipelines, metrics dashboards, or data visualizations.
---

# AI Chart Generator Skill

This skill allows AI models and autonomous agents (such as Antigravity, Claude Code, Codex, Cursor, and local LLMs) to generate high-resolution, presentation-ready 16:9 visual diagrams.

## When to Use This Skill

Activate this skill when:
- The user requests a **flowchart**, **pipeline diagram**, or **workflow architecture**.
- The user requests a **system hierarchy**, **organization tree**, or **microservice dependency map**.
- The user asks for **market share**, **budget allocation**, or **proportional data** as a **pie** or **donut chart**.
- The user asks for **resource utilization**, **telemetry metrics**, or **activity rings** (CPU, RAM, disk, network).
- The user asks for a **gauge**, **dial**, **speedometer**, or **thermal monitor** with threshold zones.

---

## Capabilities & Chart Types

The engine exports crisp 16:9 images (1672 × 941 default) with clean blueprint grid backgrounds, modern typography, and anti-aliased geometry:

| Chart Type | Key Use Cases | Required Input Fields |
| :--- | :--- | :--- |
| `flowchart` | Sequential workflows, AI pipelines, edge IoT stages | `title`, `stages` (`header`, `blocks`) |
| `hierarchy` | Architecture trees, folder trees, org charts | `title`, `root_node` (`name`, `children`) |
| `donut` | Proportions with center KPI (e.g. `"$1.2M"`, `"94%"`) | `title`, `data` (`label`, `value`), `center_text` |
| `pie` | Solid proportional distribution slices | `title`, `data` (`label`, `value`) |
| `rings` | Concentric activity/progress rings (0–100%) | `title`, `metrics` (`label`, `pct`) |
| `gauge` | 240° dial with threshold zones and needle | `title`, `value`, `min_val`, `max_val`, `unit` |

---

## How Agents Should Invoke This Tool

### Method 1: Command Line (CLI)
Any agent with terminal/bash execution capability can run:
```bash
ai-chart '{"chart_type": "gauge", "title": "Server Temperature", "value": 54.2, "unit": "°C"}'
```
Or with Python module syntax:
```bash
python -m ai_chart_toolkit.tool '{"chart_type": "donut", "title": "Budget Breakdown", "center_text": "$84k", "data": [{"label": "Compute", "value": 60}, {"label": "Storage", "value": 40}]}'
```

### Method 2: Python Function Calls
```python
from ai_chart_toolkit import execute_chart_tool

result = execute_chart_tool("flowchart", {
    "title": "Autonomous Edge Agent",
    "subtitle": "Multimodal perception and physical actuation",
    "stages": [
        {"header": "PERCEPTION", "blocks": [{"label": "Camera & Audio", "type": "input"}]},
        {"header": "REASONING", "blocks": [{"label": "Gemma 4 Local", "type": "ai_model"}]},
        {"header": "ACTUATION", "blocks": [{"label": "Relay Switch", "type": "output"}]}
    ],
    "output_path": "output/agent_pipeline.png"
})
print("Chart generated at:", result["absolute_path"])
```

### Method 3: Model Context Protocol (MCP)
Add to your agent's MCP config:
```json
{
  "mcpServers": {
    "ai-chart": {
      "command": "ai-chart-mcp"
    }
  }
}
```

### Method 4: Local HTTP REST API
Start the server with `ai-chart-api` (or `python -m ai_chart_toolkit.api_server`) and send POST requests:
```bash
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{"chart_type": "rings", "title": "Cluster Load", "metrics": [{"label": "CPU", "pct": 78}, {"label": "RAM", "pct": 62}]}'
```

---

## Detailed Payload Specifications

### 1. Flowchart (`chart_type: "flowchart"`)
Semantic block categories for `type`:
- `"input"` (Dark Slate) — Sensors, user voice, webhooks, requests.
- `"ai_model"` (Electric Blue) — LLMs, vision models, classifiers.
- `"tool"` (Teal) — Python scripts, APIs, Home Assistant, relays.
- `"data_store"` (Amber Gold) — SQLite, Vector DB, Redis, JSON files.
- `"output"` (Emerald Green) — Audio reply, motors, dashboard alert.

```json
{
  "chart_type": "flowchart",
  "title": "Voice Assistant Architecture",
  "subtitle": "Local low-latency pipeline",
  "stages": [
    {
      "header": "WAKE & SPEECH",
      "blocks": [
        {"label": "Wake Word Engine", "type": "input"},
        {"label": "Whisper STT", "type": "input"}
      ]
    },
    {
      "header": "CORE BRAIN",
      "blocks": [
        {"label": "Ollama (Llama 3.2)", "type": "ai_model"},
        {"label": "Context Vector Store", "type": "data_store"}
      ]
    },
    {
      "header": "DISPATCH",
      "blocks": [
        {"label": "Home Assistant MCP", "type": "tool"}
      ]
    },
    {
      "header": "FEEDBACK",
      "blocks": [
        {"label": "Piper TTS Speaker", "type": "output"}
      ]
    }
  ]
}
```

### 2. Hierarchy Tree (`chart_type: "hierarchy"`)
```json
{
  "chart_type": "hierarchy",
  "title": "Enterprise Cloud Architecture",
  "subtitle": "Multi-region service topography",
  "root_node": {
    "name": "Global Gateway",
    "desc": "Cloudflare Anycast",
    "children": [
      {
        "name": "US-East Region",
        "desc": "Primary Cluster",
        "children": [
          {"name": "Auth API", "desc": "FastAPI Pods"},
          {"name": "DB Primary", "desc": "Postgres Aurora"}
        ]
      },
      {
        "name": "EU-Central Region",
        "desc": "Read Replica",
        "children": [
          {"name": "Cache Edge", "desc": "Redis Cluster"},
          {"name": "Worker Pool", "desc": "Celery Queues"}
        ]
      }
    ]
  }
}
```

### 3. Donut Chart (`chart_type: "donut"`)
```json
{
  "chart_type": "donut",
  "title": "Monthly Cloud Spend",
  "center_text": "$18,400",
  "center_sub": "Total Run Rate",
  "data": [
    {"label": "GPU Instances", "value": 52},
    {"label": "Object Storage", "value": 24},
    {"label": "Database Engine", "value": 14},
    {"label": "Egress Traffic", "value": 10}
  ]
}
```

### 4. Precision Radial Gauge (`chart_type: "gauge"`)
```json
{
  "chart_type": "gauge",
  "title": "3D Printer Heatbed Temp",
  "subtitle": "Watchdog thermistor telemetry",
  "value": 68.4,
  "min_val": 0,
  "max_val": 120,
  "unit": "°C Temperature",
  "zones": [
    [0.50, "#10B981"],
    [0.75, "#F59E0B"],
    [1.00, "#EF4444"]
  ]
}
```

---

## Best Practices for Agents

1. **Keep Labels Concise**: Use 2 to 4 words per block label for optimal visual balance.
2. **Include Subtitles**: Subtitles provide helpful context and are automatically spaced with clean margins.
3. **Themes**: Default theme is clean blueprint light (`"default"`). Pass `"theme": "dark"` for deep navy presentations.
4. **Output Paths**: If the user didn't specify an output path, omit it; the engine automatically saves to `output/<slugified_title>_<type>.png` and returns the file path.
