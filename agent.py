import os
import sys
import time

# Force UTF-8 mode for the entire process so emoji/Unicode prints never crash
# on Windows cp1252 consoles. Must be set before any I/O happens.
os.environ.setdefault("PYTHONUTF8", "1")

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass  # Reconfigure not supported on this terminal — PYTHONUTF8 covers it

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# --- API key setup ---
try:
    from kaggle_secrets import UserSecretsClient
    NVIDIA_API_KEY = UserSecretsClient().get_secret("NVIDIA_API_KEY")
    os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY
    print("✅ Nvidia API key setup complete (from Kaggle Secrets).")

except ModuleNotFoundError:
    from dotenv import load_dotenv
    load_dotenv()
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    if NVIDIA_API_KEY:
        print("✅ Nvidia API key setup complete (from .env or system env).")
    else:
        print("⚠️ NVIDIA_API_KEY not found. Add it to your .env file or system variables.")

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- DuckDuckGo Search Function ---
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo for the given query and return the top text results. Use this ONLY when you need up-to-date or real-time information.
    
    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to fetch.
    """
    try:
        with DDGS(timeout=5) as search:
            results = list(search.text(query, max_results=max_results))
            summaries = [r.get("body", "") for r in results if "body" in r]
            return "\n".join(summaries) if summaries else "No results found."
    except Exception as e:
        return f"Search error: {e}"

# --- Image Generation Function ---
import urllib.parse
import urllib.request

# Save images next to this script, regardless of the working directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_image(prompt: str) -> str:
    """Generate an image based on a text prompt. Use this ONLY when the user explicitly asks to generate, draw, or create an image.
    
    Args:
        prompt (str): A detailed description of the image to generate.
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        filename = f"generated_image_{int(time.time())}.png"
        filepath = os.path.join(_SCRIPT_DIR, filename)

        # Use urlopen so we can detect HTTP error responses (urlretrieve silently saves error bodies)
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                return f"Image generation error: server returned HTTP {response.status}"
            with open(filepath, "wb") as f:
                f.write(response.read())

        return f"Image generated successfully and saved to: {filepath}"
    except Exception as e:
        return f"Image generation error: {e}"

# --- Nvidia Agent ---
from phi.agent import Agent
from phi.model.openai import OpenAIChat

# Bug 6 fix: Fail early with a clear message if the API key is missing
if not NVIDIA_API_KEY:
    print("❌ NVIDIA_API_KEY is missing. Add it to your .env file and restart.")
    sys.exit(1)

root_agent = Agent(
    name="helpful_assistant",
    description="A smart, conversational AI assistant with access to real-time web search.",
    instructions=[
        "You are a helpful, intelligent, and professional AI assistant.",
        "CRITICAL: For greetings (like 'hi', 'hello', 'hey'), casual chat, or general knowledge questions, reply directly using conversational text. NEVER call any tools for greetings or simple conversation.",
        "ONLY use duckduckgo_search when the user explicitly asks for real-time information, latest news, current events, or live data.",
        "ONLY use generate_image when the user explicitly asks you to generate, draw, or create an image.",
        "Never run tools in a recursive loop. If a tool completes or reports an error, provide your final response immediately.",
        "Format your answers clearly using Markdown.",
    ],
    model=OpenAIChat(
        id="minimaxai/minimax-m3.1-flash",
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    ),
    tools=[duckduckgo_search, generate_image],
    tool_call_limit=2,
    show_tool_calls=True,
    add_history_to_messages=True,
    num_history_responses=10,   # Bug 4 fix: cap history to avoid context window overflow
    markdown=True,
)

print("✅ Root Agent defined.")
if __name__ == "__main__":
    print("\n💬 Interactive mode — type your question or 'exit' to quit.\n")

    # --- Interactive Chat Loop ---
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break
            if not user_input:
                continue
                
            print("\n", end="")
            root_agent.print_response(user_input, stream=True)
            print("\n")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

