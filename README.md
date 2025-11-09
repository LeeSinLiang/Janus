**✨ Overview**\n
Janus is an AI-native, multi-agent GTM OS that automates strategy, content, posting, and feedback loops. It visualizes campaigns as graphs, adapts creatives from real-time metrics, and keeps a human in the loop for approvals, essentially following this workflow: \n
Strategize and Plan → Create Content (text, images, videos) → Post Content (X, ProductHunt, Instagram, etc) → Measure Metrics (likes, retweets, comments, shares, etc) → Adapt Strategy — on autopilot, with your sign-off.\n\n

**🧠 Why**\n
Marketing isn’t blocked by content creation, it’s blocked by iteration speed. Janus accelerates learning cycles across channels (X, Instagram, ProductHunt, and more soon) and routes the next best action automatically.\n\n

**🧩 Features**\n
1. Canvas OS: node-based campaign builder (phases, posts, A/B arms, triggers)\n
2. Multi-Agent Orchestration: 3-layer supervisor + specialist sub-agents\n
3. Human-in-the-Loop: explicit approval gates before posting/edits\n
4. Metrics-Driven Adaptation: rewrite, reschedule, or reroute based on KPIs\n
5. API Integrations: X (Twitter), Instagram, ProductHunt, etc\n\n

**🏗️ Architecture**\n
flowchart LR\n\t
  U[Founder UI (Next.js + Tailwind + ReactFlow)] -->|Actions/Approval| API[(Django DRF)]\n
  API -->|Prompts/Tools| Orchestrator[LangChain + LangGraph]\n
  Orchestrator -->|Agents| Strategy[Strategy Planner]\n
  Orchestrator --> Content[Content Generator]\n
  Orchestrator --> Posting[Platform Poster]\n
  Orchestrator --> Metrics[Metrics Analyzer]\n
  Metrics --> Store[(DB/SQLite)]\n
  Posting -->|X/IG/PH SDKs| Channels{{X • Instagram • Product Hunt}}\n
  Store --> API\n
  API --> U\n\n

**🛠️ Tech Stack**\n
Backend: Django, DRF, LangChain, LangGraph, Google Gemini Generative AI\n
Frontend: Next.js (React), Tailwind, ReactFlow, Mermaid\n
Data/Infra: SQLite (dev), Vultr (deploy)\n\n

**🚦 Project Status**\n
Actively evolving during and after the hackathon, aiming to launch as a startup.\n\n

**⚡ Quickstart**\n
_**Monorepo layout**_\n
.\n
├── backend/\n
│   ├── requirements.txt\n
│   └── src/  # manage.py lives here\n
└── frontend/\n
    └── janus/  # Next.js app\n\n

_**1) Clone**_\n
git clone https://github.com/LeeSinLiang/Janus.git\n
cd Janus\n\n

_**2) Backend**_\n
cd backend\n
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate\n
pip install -r requirements.txt\n
cp .env.example .env\n
cd src\n
python manage.py migrate\n
python manage.py runserver\n\n

_**3) Frontend**_\n
cd ../../frontend/janus\n
npm install\n
npm run dev\n
