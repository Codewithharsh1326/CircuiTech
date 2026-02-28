# CircuiTech: Agentic Electronic Design Automation (EDA)

CircuiTech is an intelligent, agent-driven Electronic Design Automation (EDA) web application. Designed to transition hardware engineering from manual spreadsheet-hunting into an automated conversational workflow, it leverages Large Language Models (LLMs) and real-world Component APIs to instantly architect, source, and route physical Bills of Materials (BOMs).

Through a modern, canvas-first interface, hardware engineers can describe their design constraints in plain English. The underlying agentic orchestrator then extracts the requirements, searches live distributor databases (DigiKey/Octopart) for in-stock components and pricing, synthesizes a structured BOM, and finally generates logical pin-mapping netlists for hardware integration.

---

## 📑 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Repository Structure](#repository-structure)
3. [The Agentic Workflow](#the-agentic-workflow)
4. [Project Impact & Use Cases](#project-impact--use-cases)
5. [Tech Stack & Conventions](#tech-stack--conventions)
6. [Getting Started](#getting-started)
7. [Future Improvements](#future-improvements)
8. [Credits](#credits)

---

## 🏗️ Architecture Overview

The system is split into a robust **React (Vite) Frontend** and an asynchronous **FastAPI Python Backend**. State and session persistence are decoupled via MongoDB, while component sourcing is handled by querying live provider endpoints natively.

![CircuiTech Architecture Flowchart](./flowchart.png)

### Key Architectural Pillars:
- **Canvas-First UI:** A streamlined, floating interface built with Tailwind CSS and Shadcn UI.
- **Micro-Agent Services:** Prompt chaining separates the LLM roles into *Extraction*, *Synthesis*, and *Integration* to prevent hallucination.
- **RESTful Orchestration:** Asynchronous HTTP routines (`httpx`) to hit external REST (DigiKey) and GraphQL (Octopart/Nexar) endpoints concurrently.
- **Event-Sourced Memory:** User chat histories and iterative BOM payloads are persisted using MongoDB `motor` drivers, enabling long-tail context awareness.

---

## 📁 Repository Structure

```text
AMD_web/
├── frontend/          # Vite + React + TypeScript
│   ├── src/
│   │   ├── components/    # Reusable UI components (Shadcn/ui)
│   │   ├── pages/         # Route-level page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities, centralized API clients
│   │   ├── stores/        # Zustand global state stores
│   │   └── types/         # Shared TypeScript interfaces
│   ├── index.html
│   └── vite.config.ts
│
└── backend/           # Python FastAPI
    ├── app/
    │   ├── main.py        # FastAPI app entrypoint & routers
    │   ├── agents/        # Groq LLM agent pipelines (BOM, Pinmap, Component)
    │   ├── models/        # Pydantic models & schema validation
    │   ├── services/      # Business logic & Non-blocking External APIs
    │   └── db/            # Async MongoDB connection via Motor
    ├── requirements.txt
    └── .env               # Environment parameters and local secrets


```

---

## 🧠 The Agentic Workflow

CircuiTech relies on a massive reduction of LLM hallucinations by enforcing a strict tool-calling loop. When a user prompts the system, the following pipeline executes seamlessly natively on the backend:

1. **Phase 1: Extraction (The Hardware Architect)**
   - The user inputs loose constraints (e.g. *"I need a low-power LoRa environmental sensor"*).
   - The primary Groq LLM evaluates the prompt. If constraints are missing (like size, battery type), it halts and asks clarifying questions.
   - Once sufficient, it extracts structural `{"search_queries": ["..."]}` and outputs them as JSON.
   
2. **Phase 2: Execution (The Procurement Engine)**
   - The Python backend traps the JSON array.
   - It iterates over the queries and fires Async OAuth2 requests against the **DigiKey Part Search API** and **Octopart GraphQL**.
   - Live availability, Manufacturer Part Numbers (MPNs), and exact unit prices are returned.

3. **Phase 3: Synthesis (The Sourcing Engineer)**
   - The raw JSON results from DigiKey are injected back into a secondary Synthesizing prompt.
   - The AI acts as a filter, comparing the live parts against the user's constraints, selecting the best matches, and strictly formatting them into the core `BomItem` Pydantic models.

4. **Phase 4: Integration (The Netlist Generator)**
   - Once the BOM is finalized, the user triggers the "Generate Pin Map" feature.
   - The payload travels to an Integration agent, which parses standard datasheets internally to map logical physical connections (e.g. `STM32 SDA` ↔ `Sensor SDA`) returning a structured array for UI routing.

---

## 🌍 Project Impact & Use Cases

### Impact
Traditional electronic design is siloed. Hardware engineers spend over 30% of project timelines manually scouring manufacturer sites, comparing datasheets, and cross-referencing stock availability to build simple starter BOMs. 

CircuiTech drastically accelerates the conceptualization phase. By marrying the associative intelligence of LLMs with the programmatic accuracy of actual supply-chain endpoints, prototyping times are slashed from hours to seconds.

### Core Use Cases
- **Rapid Prototyping Validation:** An engineer pitching an IoT idea can instantly get a workable BOM and immediate cost estimations to see if the project is financially viable.
- **Component Discovery:** Junior engineers or software developers branching into embedded hardware can ask for generic concepts ("a motor driver for a 12V stepper") and receive industry-standard chips they wouldn't have known to search for.
- **Supply Chain Resiliency:** In a post-chip-shortage world, the agents strictly filter for parts that are natively tagged as `InStock` by the APIs.

---

## 🛠️ Tech Stack & Conventions

**Frontend:**
- **React (Vite) + TypeScript:** Functional components with strict typings.
- **Zustand:** Dedicated global client state synchronized strictly across UI tabs.
- **Tailwind CSS & Shadcn UI:** Class-ordered streamlined layouts extending standard generic component behaviors.
- **Axios:** Centralized API client mapped strongly to backend endpoints.

**Backend:**
- **Python 3.12+ & FastAPI:** High performance, asynchronous endpoints leveraging heavy REST routing setups. All operations (DB, LLM, HTTP requests) strictly implemented via non-blocking `async/await`.
- **Pydantic (v2):** Core backbone for all data passing. The system relies aggressively on JSON validation preventing Groq from bleeding unorganized data downstream.
- **Motor:** Asynchronous MongoDB persistence driver holding UUID-indexed user logs and component iterations automatically.
- **HTTPX:** Performing multi-threaded API requests behind the curtain securely.

**AI & Data Providers:**
- **Groq (`llama-3.3-70b-versatile`):** The primary brain. All prompts enforce `{"type": "json_object"}`.
- **DigiKey V3 API (OAuth2) & Octopart (GraphQL)**: Sourcing engine targets.

---

## ⚙️ Getting Started

### 1. Environment Configurations
In `backend`, create a `.env` file referencing `.env.example`:
```ini
GROQ_API_KEY=your_groq_key
MONGODB_URI=your_mongo_atlas_connection
DIGIKEY_CLIENT_ID=your_digikey_id
DIGIKEY_CLIENT_SECRET=your_digikey_secret
OCTOPART_API_KEY=your_nexar_token
CORS_ORIGINS=http://localhost:5173
```

### 2. Bootstrapping the Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload # Runs heavily async backend at :8000
```

### 3. Running the Frontend Server
```bash
cd frontend
npm install
npm run dev # Mounts the React application at :5173
```

---

## 🚀 Future Improvements

While CircuiTech is powerfully capable of end-to-end BOM orchestration, several enhancements could elevate it to a production tier application:

1. **Automated Schematic Generation:**
   - Evolve the *Pin Map Generator* JSON output into an `.sch` or `.kicad_sch` file using programmatic XML/S-expression builders, allowing users to instantly import the design into KiCad or Altium.
   
2. **Multi-Distributor Fallbacks:**
   - Expand the Component Services pipeline to simultaneously query DigiKey, Mouser, and LCSC. The synthesis prompt could then optimize the BOM across three different supply chains to find the absolute lowest total cart cost.
   
3. **Footprint & 3D Model Verification:**
   - Integrate SnapEDA or UltraLibrarian APIs to verify if the selected MPNs have existing CAD models, steering the AI toward parts that have guaranteed footprints to accelerate PCB layout.
   
4. **Token Cost Optimization:**
   - Implement intelligent context-window shrinking for the MongoDB histories to prevent the LLM context from ballooning during extended chat sessions.

---

## 🤝 Credits

**Author**: [Harsh Patel](https://github.com/Codewithharsh1326)  
**Contributor**: [Dharm Dave](https://github.com/Code-With-Dharm)

*Built with passion to push the bleeding edge boundaries of Hardware Engineering Automation.*
