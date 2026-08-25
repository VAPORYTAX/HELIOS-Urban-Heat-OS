# Architecture

```text
FortyGuard ──> provider observations/history ──> operational hazard
                                      │
Census/ACS ──> vulnerability ─────────┼──> TEU / VA-TEU
OSM ─────────> context + route graph ─┘          │
                                                 v
                         modeled counterfactual candidates
                                                 │
                                                 v
                               OR-Tools CP-SAT portfolio
                                                 │
                              governed agents + human gate
                                                 │
                            ContextForge evidence packet
                                                 │
                              Gemma explanation + firewall
```

The FastAPI layer exposes each authoritative engine independently. PostgreSQL/PostGIS stores spatial cells, observations, derived metrics, provider-native candidates, portfolios, agent decisions, routes, quality snapshots, and context packets. The Next.js client requests these records directly; MapLibre supplies OSM context while deterministic SVG overlays render the four verified cells, live-AOI intensity visualization, and 2.5D metric burden.

Truth is typed by stage: provider/observed, derived, modeled, optimized, governed, and LLM-explained. The semantic firewall validates Gemma numeric claims against ContextForge authoritative numbers. The human-review gate is never bypassed.

Citywide deployment scales by tiling new provider-validated AOIs, partitioning PostGIS spatial/time-series records, rebuilding local OSM graphs, and scheduling provider ingestion plus metric/portfolio recomputation. Neutral city context may precede provider coverage; thermal claims may not.
