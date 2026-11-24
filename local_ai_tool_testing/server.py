# -*- coding: utf-8 -*-
"""
Local AI Tool Testing Server
Pairs local Qwen 2.5 (3B / 1.9GB) with ai-chart-toolkit.
Provides a real-time typewriter output, minimal Neumorphism Light chat interface with Claude-like thinking loader.
Works as a general AI chat assistant, with visual chart generation activated on demand.
Zero external API keys required.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

# Ensure ai_chart_toolkit can be imported locally if not installed globally
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
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "generated_charts"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_active_model() -> str:
    configured = os.environ.get("OLLAMA_MODEL")
    if configured:
        return configured
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", [])]
            for preferred in ["qwen2.5:3b", "qwen2.5:1.5b", "qwen2.5:7b", "qwen2.5:latest"]:
                for m in models:
                    if preferred in m:
                        return m
            for m in models:
                if "qwen" in m.lower():
                    return m
            if models:
                return models[0]
    except Exception:
        pass
    return "qwen2.5:3b"

MODEL_NAME = get_active_model()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qwen 2.5 — Local AI Assistant</title>
  <style>
    :root {
      --bg: #EEF2F6;
      --card-bg: #EEF2F6;
      --text-main: #1E293B;
      --text-sub: #64748B;
      --accent: #2563EB;
      
      /* Neumorphism Dual-Shadow Tokens */
      --neu-shadow: 6px 6px 14px #D0D7E2, -6px -6px 14px #FFFFFF;
      --neu-shadow-sm: 3px 3px 8px #D0D7E2, -3px -3px 8px #FFFFFF;
      --neu-shadow-hover: 8px 8px 18px #C5CEDC, -8px -8px 18px #FFFFFF;
      --neu-inset: inset 4px 4px 8px #D0D7E2, inset -4px -4px 8px #FFFFFF;
      --neu-inset-sm: inset 2px 2px 5px #D0D7E2, inset -2px -2px 5px #FFFFFF;
      --border-soft: 1px solid rgba(255, 255, 255, 0.85);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
      background: var(--bg);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* TOP HEADER */
    header {
      background: var(--bg);
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(208, 215, 226, 0.6);
      box-shadow: 0 4px 14px rgba(208, 215, 226, 0.35);
      z-index: 10;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-icon {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: var(--bg);
      box-shadow: var(--neu-shadow-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      border: var(--border-soft);
    }
    .brand h1 {
      font-size: 1.12rem;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.01em;
    }
    .pill-group {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .neu-pill {
      font-size: 0.78rem;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 999px;
      background: var(--bg);
      box-shadow: var(--neu-shadow-sm);
      color: var(--text-sub);
      border: var(--border-soft);
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }
    .neu-pill.active {
      color: var(--accent);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10B981;
      box-shadow: 0 0 7px #10B981;
    }

    /* CHAT STREAM */
    #chat-box {
      flex: 1;
      overflow-y: auto;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      gap: 22px;
      max-width: 900px;
      width: 100%;
      margin: 0 auto;
      scrollbar-width: thin;
      scrollbar-color: #CBD5E1 transparent;
    }
    #chat-box::-webkit-scrollbar { width: 6px; }
    #chat-box::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 999px; }

    .msg {
      max-width: 82%;
      padding: 16px 22px;
      line-height: 1.65;
      font-size: 0.95rem;
      word-wrap: break-word;
      transition: all 0.2s ease;
    }
    
    /* User Message: Elevated Neumorphic Capsule with soft blue tint */
    .msg-user {
      align-self: flex-end;
      background: linear-gradient(135deg, #2563EB, #1D4ED8);
      color: #FFFFFF;
      border-radius: 20px 20px 4px 20px;
      box-shadow: 4px 6px 14px rgba(37, 99, 235, 0.28), -2px -2px 8px #FFFFFF;
    }
    
    /* Assistant Message: Elegant Neumorphic Extruded Card */
    .msg-ai {
      align-self: flex-start;
      background: var(--card-bg);
      color: var(--text-main);
      border-radius: 20px 20px 20px 4px;
      box-shadow: var(--neu-shadow);
      border: var(--border-soft);
    }

    /* CLAUDE-LIKE THINKING / REASONING LOADER */
    .thinking-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 7px 16px;
      border-radius: 999px;
      background: var(--bg);
      box-shadow: var(--neu-inset-sm);
      border: var(--border-soft);
      color: #64748B;
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 8px;
    }
    .thinking-orb {
      width: 13px;
      height: 13px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3B82F6, #10B981);
      box-shadow: 0 0 8px rgba(37, 99, 235, 0.35);
      animation: pulse-glow 1.4s ease-in-out infinite;
    }
    @keyframes pulse-glow {
      0%, 100% { transform: scale(0.9); opacity: 0.6; }
      50% { transform: scale(1.18); opacity: 1; filter: drop-shadow(0 0 4px #10B981); }
    }
    .thinking-shimmer {
      background: linear-gradient(90deg, #64748B 0%, #1E293B 50%, #64748B 100%);
      background-size: 200% 100%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: shimmer 1.8s linear infinite;
      letter-spacing: 0.01em;
    }
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* STREAMING TYPING CURSOR */
    .typing-cursor {
      display: inline-block;
      width: 2px;
      height: 1.15em;
      background: var(--accent);
      vertical-align: text-bottom;
      margin-left: 2px;
      animation: blink 0.8s infinite;
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    
    .tool-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 999px;
      background: var(--bg);
      box-shadow: var(--neu-inset-sm);
      color: #059669;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      margin-bottom: 10px;
    }

    /* CHART CONTAINER */
    .chart-container {
      margin-top: 14px;
      background: var(--bg);
      border-radius: 16px;
      padding: 10px;
      box-shadow: var(--neu-inset);
      border: 1px solid rgba(255, 255, 255, 0.7);
    }
    .chart-img-wrap {
      border-radius: 12px;
      overflow: hidden;
      background: #FFFFFF;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }
    .chart-container img {
      width: 100%;
      height: auto;
      display: block;
      cursor: zoom-in;
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .chart-container img:hover {
      transform: scale(1.015);
    }
    .chart-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 6px 4px;
      font-size: 0.8rem;
      color: var(--text-sub);
      font-weight: 500;
    }
    .download-btn {
      background: var(--bg);
      color: var(--accent);
      box-shadow: var(--neu-shadow-sm);
      border: var(--border-soft);
      border-radius: 999px;
      padding: 5px 14px;
      font-size: 0.8rem;
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .download-btn:hover {
      box-shadow: var(--neu-shadow-hover);
      transform: translateY(-1px);
    }
    .download-btn:active {
      box-shadow: var(--neu-inset-sm);
      transform: translateY(0);
    }

    /* INPUT SECTION */
    #input-bar {
      background: var(--bg);
      border-top: 1px solid rgba(208, 215, 226, 0.5);
      box-shadow: 0 -4px 16px rgba(208, 215, 226, 0.35);
      padding: 18px 24px 22px;
      z-index: 10;
    }
    #input-container {
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      gap: 14px;
      align-items: center;
    }
    .neu-input-wrap {
      flex: 1;
      position: relative;
    }
    input[type="text"] {
      width: 100%;
      background: var(--bg);
      border: none;
      box-shadow: var(--neu-inset);
      color: var(--text-main);
      padding: 15px 22px;
      border-radius: 16px;
      font-size: 0.95rem;
      outline: none;
      transition: box-shadow 0.2s ease;
    }
    input[type="text"]:focus {
      box-shadow: var(--neu-inset), 0 0 0 2px rgba(37, 99, 235, 0.3);
    }
    input[type="text"]::placeholder {
      color: #94A3B8;
      font-weight: 400;
    }
    .neu-btn {
      background: linear-gradient(135deg, #2563EB, #1D4ED8);
      color: #FFFFFF;
      border: none;
      padding: 15px 26px;
      border-radius: 16px;
      font-size: 0.95rem;
      font-weight: 600;
      box-shadow: 4px 6px 14px rgba(37, 99, 235, 0.3), -3px -3px 8px #FFFFFF;
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
    }
    .neu-btn:hover {
      box-shadow: 6px 8px 18px rgba(37, 99, 235, 0.4), -4px -4px 10px #FFFFFF;
      transform: translateY(-1px);
    }
    .neu-btn:active {
      box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.3);
      transform: translateY(0);
    }
    .neu-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    /* LIGHTBOX MODAL FOR DIAGRAM EXPANSION */
    #lightbox {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(8px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 40px;
      cursor: zoom-out;
    }
    #lightbox img {
      max-width: 95%;
      max-height: 92%;
      border-radius: 12px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-icon">✨</div>
      <div>
        <h1>Qwen 2.5</h1>
      </div>
    </div>
    <div class="pill-group">
      <span class="neu-pill active">
        <span class="status-dot"></span>
        <span id="model-name">3B Offline</span>
      </span>
      <span class="neu-pill">ai-chart-toolkit</span>
      <span class="neu-pill" style="color:#059669;">Zero API Keys</span>
    </div>
  </header>

  <div id="chat-box">
    <div class="msg msg-ai">
      <p style="font-size: 1.05rem; font-weight: 700; color: #1E293B;">
        👋 How can I help you today?
      </p>
      <p style="color: var(--text-sub); margin-top: 4px; font-size: 0.92rem;">
        Ask me anything—writing, code, questions, or request any system architecture visual or chart.
      </p>
    </div>
  </div>

  <div id="input-bar">
    <div id="input-container">
      <div class="neu-input-wrap">
        <input type="text" id="user-input" placeholder="Ask Qwen anything, or request a chart..." onkeydown="if(event.key==='Enter') sendMsg()">
      </div>
      <button class="neu-btn" id="send-btn" onclick="sendMsg()">
        <span>Send</span>
        <span style="font-size: 1.05rem;">↑</span>
      </button>
    </div>
  </div>

  <!-- LIGHTBOX PREVIEW -->
  <div id="lightbox" onclick="this.style.display='none'">
    <img id="lightbox-img" src="" alt="Full Screen Diagram">
  </div>

  <script>
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const messages = [];

    function openLightbox(url) {
      lightboxImg.src = url;
      lightbox.style.display = 'flex';
    }

    // Instant ChatGPT/Gemini-style real-time typewriter effect
    function typeTextInstant(el, cursorEl, text, onComplete) {
      // Split text into word chunks for natural cadence
      const words = text.split(/(\\s+)/);
      let i = 0;
      let rendered = '';

      function tick() {
        if (i < words.length) {
          rendered += words[i];
          el.innerHTML = rendered.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
          i++;
          chatBox.scrollTop = chatBox.scrollHeight;
          const delay = words[i-1].includes('\\n') ? 25 : (Math.random() * 8 + 8);
          setTimeout(tick, delay);
        } else {
          if (cursorEl) cursorEl.remove();
          if (onComplete) onComplete();
        }
      }
      tick();
    }

    async function sendMsg() {
      const text = userInput.value.trim();
      if (!text) return;

      // 1. Append user message
      appendUserMsg(text);
      userInput.value = '';
      sendBtn.disabled = true;

      // 2. Create Assistant message container with Claude-like Thinking Loader
      const aiMsgEl = document.createElement('div');
      aiMsgEl.className = 'msg msg-ai';
      
      const thinkingEl = document.createElement('div');
      thinkingEl.className = 'thinking-pill';
      thinkingEl.innerHTML = '<span class="thinking-orb"></span><span class="thinking-shimmer">Thinking...</span>';
      aiMsgEl.appendChild(thinkingEl);

      const textEl = document.createElement('span');
      textEl.className = 'stream-text';
      aiMsgEl.appendChild(textEl);

      const cursorEl = document.createElement('span');
      cursorEl.className = 'typing-cursor';
      aiMsgEl.appendChild(cursorEl);

      chatBox.appendChild(aiMsgEl);
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: messages })
        });

        const data = await resp.json();

        // Smoothly fade out thinking pill
        thinkingEl.style.display = 'none';

        if (data.success) {
          // If a chart was requested and generated, insert badge & chart container
          if (data.chart_url) {
            const chartType = data.chart_type || 'chart';
            const badge = document.createElement('div');
            badge.className = 'tool-badge';
            badge.innerHTML = `⚡ ${chartType.toUpperCase()} DIAGRAM GENERATED`;
            aiMsgEl.insertBefore(badge, textEl);

            const fullUrl = data.chart_url + (data.chart_url.includes('?') ? '&' : '?') + 't=' + Date.now();
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.innerHTML = `
              <div class="chart-img-wrap">
                <img src="${fullUrl}" alt="Generated Diagram" onclick="openLightbox('${data.chart_url}')" title="Click to view full screen">
              </div>
              <div class="chart-footer">
                <span>Resolution: 1672 × 941 (16:9 Blueprint)</span>
                <a class="download-btn" href="${data.chart_url}" download>⬇️ Download PNG</a>
              </div>
            `;
            aiMsgEl.appendChild(chartDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
          }

          // Real-time typewriter output for text
          const replyText = data.reply || '';
          typeTextInstant(textEl, cursorEl, replyText, () => {
            messages.push({ role: 'user', content: text });
            messages.push({ role: 'assistant', content: replyText });
            sendBtn.disabled = false;
            userInput.focus();
          });

        } else {
          cursorEl.remove();
          textEl.innerHTML = `<span style="color:#EF4444;">⚠️ Error: ${data.error || 'Failed to process request.'}</span>`;
          sendBtn.disabled = false;
          userInput.focus();
        }

      } catch (err) {
        thinkingEl.style.display = 'none';
        cursorEl.remove();
        textEl.innerHTML = `<span style="color:#EF4444;">⚠️ Connection error: ${err.message}</span>`;
        sendBtn.disabled = false;
        userInput.focus();
      }
    }

    function appendUserMsg(text) {
      const div = document.createElement('div');
      div.className = 'msg msg-user';
      div.innerHTML = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  </script>
</body>
</html>
"""

def query_ollama(prompt: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Queries local Ollama using Qwen 2.5 with tool definitions.
    Qwen acts as a normal conversational AI assistant and only invokes
    'generate_chart' when explicitly or implicitly asked for a chart/diagram.
    """
    tools = get_openai_tool_schema()
    msgs = [{"role": "system", "content": (
        "You are Qwen, a helpful, brilliant, and thoughtful AI assistant. "
        "Answer normal questions, conversation, math, writing, and code naturally and conversationally. "
        "You also have access to the 'generate_chart' tool. ONLY invoke 'generate_chart' when the user explicitly or implicitly asks to create, draw, generate, or visualize a chart, diagram, flowchart, gauge, telemetry rings, pie/donut, or architecture visual. "
        "For standard chat, questions, or explanations that do not request a visual chart, answer directly in natural conversational language without using the tool."
    )}]
    if history:
        for h in history[-6:]:
            msgs.append(h)
    msgs.append({"role": "user", "content": prompt})

    req_payload = {
        "model": MODEL_NAME,
        "messages": msgs,
        "tools": tools,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    req_data = json.dumps(req_payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

class ChartStudioHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path.startswith("/charts/"):
            filename = os.path.basename(self.path.split("?")[0])
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8")
            data = json.loads(post_body)
            user_msg = data.get("message", "")
            history = data.get("history", [])

            try:
                ollama_res = query_ollama(user_msg, history)
                msg_obj = ollama_res.get("message", {})
                tool_calls = msg_obj.get("tool_calls", [])

                reply_text = msg_obj.get("content", "")
                chart_url = None
                chart_type = None

                # Execute tool if Qwen decided to generate a chart
                if tool_calls:
                    for call in tool_calls:
                        fn = call.get("function", {})
                        fn_args = fn.get("arguments", {})
                        if isinstance(fn_args, str):
                            fn_args = json.loads(fn_args)

                        chart_type = fn_args.pop("chart_type", "flowchart")
                        fn_args["output_dir"] = OUTPUT_DIR

                        sys.stderr.write(f"Executing tool: {chart_type} for '{fn_args.get('title')}'\\n")
                        tool_result = execute_chart_tool(chart_type, fn_args)

                        if tool_result.get("success"):
                            filename = os.path.basename(tool_result["output_path"])
                            chart_url = f"/charts/{filename}"
                            if not reply_text:
                                reply_text = f"I've generated the **{chart_type}** diagram titled **'{fn_args.get('title', 'Chart')}'** according to your requirements."
                        else:
                            reply_text = f"Tool execution failed: {tool_result.get('error')}"

                if not reply_text:
                    reply_text = "Here is the visualization requested."

                resp_data = {
                    "success": True,
                    "reply": reply_text,
                    "chart_url": chart_url,
                    "chart_type": chart_type
                }
            except Exception as e:
                resp_data = {
                    "success": False,
                    "error": str(e)
                }

            body = json.dumps(resp_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        sys.stderr.write(f"[Server] {format % args}\\n")

def main():
    port = int(os.environ.get("PORT", 8501))
    server = HTTPServer(("0.0.0.0", port), ChartStudioHandler)
    sys.stderr.write(f"\\n=======================================================\\n")
    sys.stderr.write(f" Local Qwen 2.5 AI Assistant Running!\\n")
    sys.stderr.write(f" Open in Browser: http://localhost:{port}\\n")
    sys.stderr.write(f" Model: {MODEL_NAME} on {OLLAMA_HOST}\\n")
    sys.stderr.write(f"=======================================================\\n\\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()
