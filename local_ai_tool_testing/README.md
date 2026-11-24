# Local AI Chart Studio (Qwen 2.5 + `ai-chart-toolkit`)

Interactive local testing environment pairing **Qwen 2.5 (3B / ~1.9 GB)** with **`ai-chart-toolkit`** for fully offline, zero-API-key AI visual diagram generation.

---

## ⚡ How It Works

```
                                  ┌───────────────────────────┐
                                  │   User Prompt in Web UI   │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Local Qwen 2.5 (3B)     │
                                  │ (Offline via Ollama/GGUF) │
                                  └─────────────┬─────────────┘
                                                │ tool_calls: "generate_chart"
                                                ▼
                                  ┌───────────────────────────┐
                                  │     ai-chart-toolkit      │
                                  │  (Pillow Rendering Engine)│
                                  └─────────────┬─────────────┘
                                                │ exports 16:9 PNG
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Live Inline Diagram &   │
                                  │   Download in Browser     │
                                  └───────────────────────────┘
```

---

## 🚀 Quick Start (1-Click Run)

### On Windows:
Double-click **`run.bat`** (or run `.\run.ps1` in PowerShell).

The automated runner will:
1. Verify Python and install `ai-chart-toolkit`.
2. Check if Ollama is running (auto-installs via winget if missing).
3. Download/verify the **Qwen 2.5 (3B)** model (~1.9 GB).
4. Launch the local web server and open **`http://localhost:8501`** in your browser.

---

## 💻 Manual Setup

If you prefer to start components manually:

### 1. Install Dependencies
```bash
pip install ai-chart-toolkit requests
```

### 2. Pull Qwen 2.5 (3B)
```bash
ollama pull qwen2.5:3b
```

### 3. Launch Web Interface
```bash
python server.py
```
Open **`http://localhost:8501`** in your browser.

### 4. Or Run Terminal CLI Chat Mode
```bash
python chat_cli.py
```

---

## 🎨 Example Prompts to Test with Qwen

Type your visual diagram requests or chat naturally with Qwen:

- **Flowcharts**:  
  *"Generate a pipeline flowchart for an AI Voice Assistant from microphone to TTS speaker"*
- **Precision Gauges**:  
  *"Create a 240-degree radial gauge for server CPU temperature at 74.2 degrees with warning zones"*
- **Donut Charts**:  
  *"Show a donut chart of our cloud infrastructure costs with $14.2k monthly center total"*
- **Concentric Rings**:  
  *"Make concentric activity rings for CPU (85%), RAM (62%), and Disk I/O (40%)"*
- **Hierarchy Trees**:  
  *"Generate a system hierarchy architecture tree for an IoT Smart Campus hub"*

---

## 📁 File Structure

- **`server.py`**: Zero-dependency local HTTP server providing the web chat UI and handling Ollama tool calls.
- **`chat_cli.py`**: Interactive terminal chat interface with live chart generation feedback.
- **`run.bat`**: Windows batch runner that automatically installs and starts everything.
- **`run.ps1`**: PowerShell automated setup script.
- **`generated_charts/`**: Directory where generated 16:9 diagram PNGs (1672 × 941) are saved.
- **`README.md`**: Complete documentation.

---

## 🔒 100% Local & Offline Guarantee

- **No API Keys**: Does not use OpenAI, Claude, Gemini, or Hugging Face API keys.
- **Private**: No data leaves your machine; inference and chart generation run entirely on your local hardware.
