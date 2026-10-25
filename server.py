import os
import sys
import json
import time
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv
from openai import OpenAI

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

from agent import duckduckgo_search, generate_image

# Direct OpenAI client targeting NVIDIA's working inference endpoint with timeout
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
    timeout=15.0
)

MODEL_ID = "minimaxai/minimax-m3.1-flash"
FALLBACK_MODEL = "meta/llama-3.2-11b-vision-instruct"

# Keep conversational history for interactive chat context
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful, intelligent, and professional AI assistant. "
            "Reply directly with clear, concise, well-structured Markdown. "
            "Never hallucinate dates or facts. If real-time ground truth is provided in the context, cite it accurately."
        )
    }
]

def process_agent_message(user_message: str) -> dict:
    lower_msg = user_message.lower().strip()

    # 1. Image Generation Intent
    image_keywords = ["generate image", "create image", "draw an image", "draw a ", "generate a picture", "make an image", "create a picture"]
    if any(k in lower_msg for k in image_keywords) or (lower_msg.startswith("draw ") or lower_msg.startswith("generate ")):
        prompt = user_message
        for kw in ["generate an image of", "generate image of", "create an image of", "draw an image of", "draw a", "draw", "generate"]:
            if lower_msg.startswith(kw):
                prompt = user_message[len(kw):].strip()
                break
        
        result_str = generate_image(prompt)
        # Find if a file was created
        filename = ""
        if "saved to:" in result_str:
            filepath = result_str.split("saved to:")[-1].strip()
            filename = os.path.basename(filepath)

        return {
            "type": "vision",
            "title": "Vision Synthesis Artifact",
            "reply": result_str,
            "image_url": f"/{filename}" if filename else None
        }

    # 2. Live Search Intent
    search_keywords = ["latest", "news", "current", "today", "who is", "weather", "recent", "price of", "release date"]
    needs_search = any(k in lower_msg for k in search_keywords)

    search_context = ""
    if needs_search:
        search_results = duckduckgo_search(user_message, max_results=4)
        if search_results and "No results found" not in search_results:
            search_context = f"\n\n[Verified DuckDuckGo Real-Time Ground Truth]:\n{search_results}\n"

    # 3. LLM Reasoning Call
    prompt_payload = user_message
    if search_context:
        prompt_payload += search_context

    conversation_history.append({"role": "user", "content": prompt_payload})
    # Keep history bounded to avoid context overflow
    if len(conversation_history) > 12:
        conversation_history[:] = [conversation_history[0]] + conversation_history[-10:]

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=conversation_history,
            max_tokens=1024,
            temperature=0.3
        )
        reply = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})

        return {
            "type": "search" if search_context else "general",
            "title": "Verified Ground Truth Response" if search_context else "Neural Response (NVIDIA)",
            "reply": reply,
            "search_used": bool(search_context)
        }
    except Exception as e:
        # Try fallback model if needed
        try:
            completion = client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=conversation_history,
                max_tokens=1024,
                temperature=0.3
            )
            reply = completion.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": reply})
            return {
                "type": "general",
                "title": "Neural Response (NVIDIA Fallback)",
                "reply": reply
            }
        except Exception as e2:
            return {
                "type": "error",
                "title": "Execution Error",
                "reply": f"Inference error: {e2}"
            }


class AgentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable aggressive caching for API/assets
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    res_payload = {"error": "Empty message"}
                else:
                    res_payload = process_agent_message(user_msg)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res_payload).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    PORT = 8080
    server_address = ("", PORT)
    httpd = ThreadingHTTPServer(server_address, AgentHTTPRequestHandler)
    print(f"🚀 Real Agent Server running on http://localhost:{PORT}")
    print(f"📡 Model: {MODEL_ID} connected via NVIDIA NIM API")
    httpd.serve_forever()
