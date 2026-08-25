# HELIOS

**Hyperlocal Environmental Layer for Intervention & Optimization Systems**  
*Don’t map the heat. Rewrite it.*

HELIOS is an urban heat intervention operating system. It turns provider-backed observations into exposure and vulnerability intelligence, modeled cooling interventions, CP-SAT investment portfolios, ThermalWay climate-safe mobility, governed agent decisions, provenance packets, and evidence-grounded local Gemma explanations.

## Why it matters

Heat maps locate a problem; public decision-makers also need to compare actions, allocate constrained budgets, protect journeys, inspect uncertainty, and retain human authority. HELIOS closes that loop without allowing an LLM to own numerical, spatial, routing, or optimization truth.

## Architecture

- FastAPI service under `/api/v1`
- PostgreSQL/PostGIS in `helios-postgis`
- FortyGuard provider observations and seven-day operational history
- OSM spatial context and pedestrian network
- deterministic TEU/VA-TEU, counterfactual, attribution, routing, and decision-science engines
- OR-Tools CP-SAT portfolio optimizer
- ContextForge provenance and governed agents
- Gemma 4 12B QAT through LM Studio native FAST transport, reasoning off
- Next.js production UI with MapLibre, SVG overlays, and Recharts

See [ARCHITECTURE.md](ARCHITECTURE.md) for the data flow.

## Prerequisites and setup

Install Docker Desktop, Python 3.12+, Node.js LTS, and LM Studio. Download `google/gemma-4-12b-qat` in LM Studio. Copy `.env.example` to `.env` and configure local, non-secret settings. Never commit `.env`.

```powershell
docker compose up -d
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .
Set-Location frontend
npm ci
Set-Location ..
.\Start-HELIOS.ps1
```

The launcher builds and serves the production frontend at `127.0.0.1:3000`, starts FastAPI at `127.0.0.1:8080`, checks PostGIS and LM Studio, and validates critical APIs plus all eight pages.

## Data, algorithms, and truth boundaries

FortyGuard supplies current provider-backed thermal observations. Census/ACS supports vulnerability, while OpenStreetMap supplies neutral Phoenix context and the ThermalWay walking graph. ThermalWay uses A* for fastest routing, Dijkstra for thermal-safe routing, and includes Yen K-shortest support. TEC, TEU, and VA-TEU are planning metrics. Intervention effects are modeled assumptions, not causal proof. Driver attribution is diagnostic. Human review remains mandatory.

HELIOS is Phoenix-scale in architecture, but its current provider-validated operational footprint is **four cells in the phx-downtown validation AOI**. Phoenix outside it is not currently observed and receives no fabricated thermal values.

Gemma explains verified HELIOS evidence only. A response is Gemma-backed only when `status=complete`, `fallback_used=false`, and `validation.valid=true`.

## Demo

Follow [DEMO_SCRIPT.md](DEMO_SCRIPT.md). The core path is Command → Atlas → Intervention Studio → Investment → ThermalWay → Evidence → AI → System.

## Screenshots

- Command overview — add final capture
- Thermal Atlas live AOI — add final capture
- ThermalWay comparison — add final capture
- Investment portfolio — add final capture
- Evidence and Gemma acceptance — add final capture
