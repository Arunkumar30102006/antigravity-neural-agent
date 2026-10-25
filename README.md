# Antigravity Neural Agent (NVIDIA NIM + Real-Time Search & Vision)

> An autonomous AI agent runtime combining NVIDIA NIM inference, real-time DuckDuckGo ground-truth search, and Pollinations.ai vision generation — packaged with both an interactive CLI and an editorial, anti-slop web interface.

---

## Overview

**Antigravity Neural Agent** provides a direct execution loop designed to eliminate AI slop, hallucinations, and context bloat. Built on Python with the Phi agent framework and NVIDIA NIM endpoints, it dynamically routes natural language instructions into:

- 🧠 **Direct Neural Reasoning**: High-throughput language reasoning via NVIDIA NIM API (`minimaxai/minimax-m3.1-flash` / `meta/llama-3.2-11b-vision-instruct`).
- 🔍 **Live Ground-Truth Web Search**: Zero-tracking real-time web retrieval via DuckDuckGo (`ddgs`) with automated source extraction.
- 🎨 **Generative Vision Synthesis**: High-resolution image synthesis directly via Pollinations.ai, saved locally and displayed in the runtime console.
- 🏛️ **Award-Level Anti-Slop Web UI**: Crafted under the strict `taste-skill` editorial design direction (*Borrowed Category* archetype, Panchang 700 / Switzer typefaces, Charcoal & Sage palette).

---

## Repository Metadata

- **Suggested Repository Title**: `antigravity-neural-agent`
- **Short Tagline**: `Autonomous AI agent runtime with NVIDIA NIM inference, real-time DuckDuckGo search, and vision generation.`
- **Topics**: `ai-agent`, `nvidia-nim`, `python`, `duckduckgo-search`, `image-generation`, `phidata`, `web-ui`, `anti-slop`

---

## Architecture

```
User Prompt (Web UI / Terminal CLI)
               │
               ▼
   [Intent Router & Guardian]
    ├── Image Generation Intent ──► Pollinations.ai API ──► Save local .png & Render
    ├── Real-Time Search Intent ──► DuckDuckGo (ddgs)   ──► Grounded Sources Extracted
    └── Direct Technical/Chat   ──► NVIDIA NIM Gateway  ──► Structured Markdown Output
```

---

## Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/antigravity-neural-agent.git
cd antigravity-neural-agent
```

### 2. Set Up Virtual Environment & Dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Your NVIDIA API Key

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
NVIDIA_API_KEY=nvapi-your_key_here
```
*(Get a free API key at [build.nvidia.com](https://build.nvidia.com/))*

### 4. Run the Project

#### Option A: Web Console (Recommended)

```bash
python server.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to access the live interactive agent console and showcase dossier.

#### Option B: Terminal Interactive Mode

```bash
python agent.py
```
Interact directly via standard input stream in your terminal.

---

## Project Structure

```
├── agent.py               # Core Phi agent definition, tools & CLI interactive loop
├── server.py              # HTTP server routing API requests to NVIDIA & tools
├── index.html             # High-aesthetic web UI built to taste-skill guidelines
├── index.css              # Custom design system (Panchang / Switzer / Charcoal & Sage)
├── app.js                 # Frontend interaction logic & API bridge
├── requirements.txt       # Python project dependencies
├── .env.example           # Example environment template
└── .gitignore             # Git ignore rules protecting API keys and generated files
```

---

## License

MIT License. Built with NVIDIA NIM, DuckDuckGo, and Pollinations.ai.
