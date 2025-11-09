**✨ Overview**
Janus is an AI-native, multi-agent GTM OS that automates strategy, content, posting, and feedback loops. It visualizes campaigns as graphs, adapts creatives from real-time metrics, and keeps a human in the loop for approvals, essentially following this workflow: 
Strategize and Plan → Create Content (text, images, videos) → Post Content (X, ProductHunt, Instagram, etc) → Measure Metrics (likes, retweets, comments, shares, etc) → Adapt Strategy — on autopilot, with your sign-off.

**🧠 Why**
Marketing isn’t blocked by content creation, it’s blocked by iteration speed. Janus accelerates learning cycles across channels (X, Instagram, ProductHunt, and more soon) and routes the next best action automatically.

**🧩 Features**
1. Canvas OS: node-based campaign builder (phases, posts, A/B arms, triggers)
2. Multi-Agent Orchestration: 3-layer supervisor + specialist sub-agents
3. Human-in-the-Loop: explicit approval gates before posting/edits
4. Metrics-Driven Adaptation: rewrite, reschedule, or reroute based on KPIs
5. API Integrations: X (Twitter), Instagram, ProductHunt, etc

**🏗️ Architecture**
flowchart LR
  U[Founder UI (Next.js + Tailwind + ReactFlow)] -->|Actions/Approval| API[(Django DRF)]
  API -->|Prompts/Tools| Orchestrator[LangChain + LangGraph]
  Orchestrator -->|Agents| Strategy[Strategy Planner]
  Orchestrator --> Content[Content Generator]
  Orchestrator --> Posting[Platform Poster]
  Orchestrator --> Metrics[Metrics Analyzer]
  Metrics --> Store[(DB/SQLite)]
  Posting -->|X/IG/PH SDKs| Channels{{X • Instagram • Product Hunt}}
  Store --> API
  API --> U

**🛠️ Tech Stack**
Backend: Django, DRF, LangChain, LangGraph, Google Gemini Generative AI
Frontend: Next.js (React), Tailwind, ReactFlow, Mermaid
Data/Infra: SQLite (dev), Vultr (deploy)

**🚦 Project Status**
Actively evolving during and after the hackathon, aiming to launch as a startup.

**⚡ Quickstart**
_**Monorepo layout**_
.
├── backend/
│   ├── requirements.txt
│   └── src/  # manage.py lives here
└── frontend/
    └── janus/  # Next.js app

_**1) Clone**_
git clone https://github.com/LeeSinLiang/Janus.git
cd Janus

_**2) Backend**_
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
cd src
python manage.py migrate
python manage.py runserver

_**3) Frontend**_
cd ../../frontend/janus
npm install
npm run dev
