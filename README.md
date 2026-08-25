# HELIOS — Urban Heat Intervention Operating System

> **FortyGuard tells us where the city is hot. HELIOS tells us how to change it.**  
> **Don’t map the heat. Rewrite it.**

HELIOS is a decision operating system built for the FortyGuard Hackathon 2026. It converts provider-backed urban thermal observations into a transparent chain of exposure intelligence, physical cooling interventions, modeled counterfactuals, budget optimization, thermal-safe mobility, advanced decision science, governed local AI, evidence inspection and human decision support.

## Public demo

**https://helios-urban-heat-os.vercel.app**

The public UI is deployed on Vercel. Dynamic compute is served by the HELIOS FastAPI/PostGIS/Gemma stack through a server-side proxy. The UI explicitly distinguishes live compute, verified read-only snapshot state and unavailable compute; snapshot mode never impersonates live routing or AI inference.

## The decision loop

```text
FORTYGUARD
   │
   ▼
OBSERVE ── provider-verified thermal evidence
   │
   ▼
DIAGNOSE ── TEU + vulnerability-adjusted VA-TEU
   │
   ▼
INTERVENE ── physical cooling candidates
   │
   ▼
SIMULATE ── transparent modeled counterfactual twin
   │
   ▼
OPTIMIZE ── budget-constrained CP-SAT portfolio
   │
   ▼
PROTECT ── ThermalWay heat-aware mobility
   │
   ▼
EXPLAIN ── governed Gemma 4 interpretation
   │
   ▼
VERIFY ── provenance, uncertainty, decision trace
   │
   ▼
HUMAN DECISION
```

The frontend keeps one **active decision cell** across the workflow. A judge can select a real provider-covered cell in the Thermal Atlas and carry that same evidence through diagnosis, intervention, counterfactual modeling, optimization, mobility, AI explanation, provenance and an executive decision brief.

## Current validated scope

The current live provider-validated operational footprint is **four downtown Phoenix cells (`phx-downtown`)**. HELIOS may display citywide Phoenix OSM context, but unobserved areas remain neutral and are never assigned fabricated provider heat values.

Current provider-native portfolio state used by the judging build has been validated around a **$100,000 planning budget**, with the authoritative optimizer record carrying selected actions, modeled TEU/VA-TEU reductions, confidence and a mandatory human-review state. Values are read from the live API rather than hardcoded into the decision UI.

## Major product surfaces

### Command
The executive cockpit. It explains the FortyGuard → HELIOS relationship, live evidence footprint, equity-adjusted burden, active decision cell, closed-loop decision trace and the current portfolio. A persistent **Generate Decision Brief** action produces a print/copy-ready Phoenix Heat Action Brief.

### Thermal Atlas
A dual-scale Phoenix context + verified-AOI map with provider coverage, cell choropleth, heat-intensity view and 2.5D burden mode. Only provider-covered cells are actionable thermal evidence. Selecting a cell makes it the active decision entity across the product.

### Intervention Studio + Counterfactual Twin
Provider-native candidate actions are shown with cost, modeled TEU reduction, modeled VA-TEU reduction, confidence, feasibility and selection state. The Counterfactual Twin shows:

```text
CURRENT → INTERVENTION → MODELED AFTER
```

using backend-provided modeled reduction values while clearly labeling the output as a planning estimate rather than a causal guarantee.

Stored counterfactual scenarios are also available through Scenario Compare.

### Portfolio + Optimizer Lab
The provider-native CP-SAT portfolio exposes selected/non-selected actions, budget utilization, modeled benefits, confidence and deterministic benefit-per-dollar comparisons. It does not invent solver rationale.

The Advanced Decision Science Lab surfaces existing deterministic analyses:
- robustness across effect/cost stress scenarios
- maximum and mean regret
- objective sensitivity
- Value of Information priority
- reverse-optimization budget frontier
- intervention sequencing
- explicit “What would change my mind?” triggers

### ThermalWay
ThermalWay operates on the real Phoenix OSM network and separates routing truth from modeled thermal cost:
- A* fastest route
- Dijkstra thermal-safe route
- one-click prevalidated Phoenix judge scenario
- traveler profiles
- modeled Thermal Exposure Cost (TEC)
- extra-time vs TEC tradeoff
- Pareto route alternatives
- safe-haven routing to observed facility context
- exposure-budget reasoning
- departure-time honesty gate when provider forecast evidence is unavailable

TEC is a planning exposure metric, **not medical risk**.

### HELIOS AI + Agent Room
Gemma 4 is an explanation/orchestration layer behind a semantic firewall. Deterministic numerical, spatial, routing and optimization engines remain authoritative.

The UI explicitly states what Gemma can and cannot do, discloses fallback status, and exposes a governed Agent Room with recommendation, skeptical findings, confidence and human-review state.

### Evidence Inspector
Every output is separated into truth categories:
- **PROVIDER** — raw/validated provider evidence
- **DERIVED** — deterministic metrics computed from evidence
- **MODELED** — counterfactual/planning estimates
- **OPTIMIZED** — solver-selected decisions
- **AI-EXPLAINED** — language interpretation only

ContextForge evidence packets, quality checks and the active-cell Decision Trace remain inspectable.

### System / Flight Readiness
The system page exposes service readiness, provider coverage, engine capabilities and the judging continuity contract. Failures are visible rather than disguised.

## Judging resilience

HELIOS includes a sanitized read-only snapshot mechanism for continuity if the live local compute tier becomes temporarily unreachable.

Run while the validated local backend is healthy:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Export-JudgingSnapshot.ps1
```

The exporter captures only non-sensitive validated result data into:

```text
frontend/public/data/verified_snapshot.json
```

Snapshot mode is visibly labeled:

> **VERIFIED SNAPSHOT — LIVE COMPUTE UNAVAILABLE**

Dynamic Gemma requests, fresh route computation, Pareto routing, safe-haven routing and exposure-budget calculations are never replayed from cached results as though they were live.

## Architecture

```text
Browser
  │
  ▼
Next.js / Vercel
  │  same-origin /api/helios/*
  ▼
Server-side proxy
  │
  ▼
FastAPI
  ├── FortyGuard/provider operations
  ├── thermal + exposure engines
  ├── counterfactual interventions
  ├── CP-SAT portfolio optimizer
  ├── advanced decision science
  ├── ThermalWay routing
  ├── governed agents + ContextForge
  └── Gemma 4 semantic firewall
        │
        ▼
PostgreSQL / PostGIS + real OSM/context evidence
```

## Local stack

Backend:

```powershell
cd D:\HELIOS
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Frontend:

```powershell
cd D:\HELIOS\frontend
npm ci
npm run build
npm run start
```

The browser-facing frontend must use the same-origin API path `/api/helios`. `HELIOS_BACKEND_URL` is used only by the Next.js server-side proxy.

## Verification

The project includes backend regression tests and a GitHub Actions frontend production-build check. The final local release workflow should verify:

```powershell
cd D:\HELIOS
.\.venv\Scripts\python.exe -m pytest -q

cd D:\HELIOS\frontend
npm run build
```

It should also verify public routes and `/api/helios/*` proxy endpoints before submission.

## Truth and limitations

HELIOS deliberately does **not** claim:
- citywide provider heat coverage when only four downtown cells are validated
- causal intervention impact from modeled counterfactuals
- medical risk from ThermalWay TEC
- causal driver attribution from diagnostic associations
- autonomous authority for Gemma or agents
- live data when the UI is operating from a verified snapshot

Human review is mandatory for planning decisions.

## Hackathon submission

Built for the **FortyGuard Hackathon 2026** as a resilient-city decision system that moves beyond heat visualization toward accountable intervention, investment and mobility decisions.
