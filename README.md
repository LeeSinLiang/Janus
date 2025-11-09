**✨ Overview**<br>
Janus is an AI-native, multi-agent GTM OS that automates strategy, content, posting, and feedback loops. It visualizes campaigns as graphs, adapts creatives from real-time metrics, and keeps a human in the loop for approvals, essentially following this workflow: <br>
Strategize and Plan → Create Content (text, images, videos) → Post Content (X, ProductHunt, Instagram, etc) → Measure Metrics (likes, retweets, comments, shares, etc) → Adapt Strategy — on autopilot, with your sign-off.<br><br>

**🧠 Why**<br>
Marketing isn’t blocked by content creation, it’s blocked by iteration speed. Janus accelerates learning cycles across channels (X, Instagram, ProductHunt, and more soon) and routes the next best action automatically.<br><br>

**🧩 Features**<br>
1. Canvas OS: node-based campaign builder (phases, posts, A/B arms, triggers)<br>
2. Multi-Agent Orchestration: 3-layer supervisor + specialist sub-agents<br>
3. Human-in-the-Loop: explicit approval gates before posting/edits<br>
4. Metrics-Driven Adaptation: rewrite, reschedule, or reroute based on KPIs<br>
5. API Integrations: X (Twitter), Instagram, ProductHunt, etc<br><br>

**🏗️ Architecture**<br>
flowchart LR<br>\t
  U[Founder UI (Next.js + Tailwind + ReactFlow)] -->|Actions/Approval| API[(Django DRF)]<br>
  API -->|Prompts/Tools| Orchestrator[LangChain + LangGraph]<br>
  Orchestrator -->|Agents| Strategy[Strategy Planner]<br>
  Orchestrator --> Content[Content Generator]<br>
  Orchestrator --> Posting[Platform Poster]<br>
  Orchestrator --> Metrics[Metrics Analyzer]<br>
  Metrics --> Store[(DB/SQLite)]<br>
  Posting -->|X/IG/PH SDKs| Channels{{X • Instagram • Product Hunt}}<br>
  Store --> API<br>
  API --> U<br><br>

**🛠️ Tech Stack**<br>
Backend: Django, DRF, LangChain, LangGraph, Google Gemini Generative AI<br>
Frontend: Next.js (React), Tailwind, ReactFlow, Mermaid<br>
Data/Infra: SQLite (dev), Vultr (deploy)<br><br>

**🚦 Project Status**<br>
Actively evolving during and after the hackathon, aiming to launch as a startup.<br><br>

**⚡ Quickstart**<br>
_**Monorepo layout**_<br>
```
.
├── backend/
│   ├── requirements.txt
│   └── src/  # manage.py lives here
└── frontend/
    └── janus/  # Next.js app
```

_**1) Clone**_<br>
git clone https://github.com/LeeSinLiang/Janus.git<br>
cd Janus<br><br>

_**2) Backend**_<br>
cd backend<br>
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate<br>
pip install -r requirements.txt<br>
cp .env.example .env<br>
cd src<br>
python manage.py migrate<br>
python manage.py runserver<br><br>

_**3) Frontend**_<br>
cd ../../frontend/janus<br>
npm install<br>
npm run dev<br>
