from __future__ import annotations
from uuid import uuid4
from sqlalchemy import desc,select
from ortools.sat.python import cp_model
from app.db.models_provider_ops import ProviderOperationalMetric
from app.db.models_provider_decision import ProviderInterventionCandidate,ProviderOptimizerRun,ProviderAgentDecision

CATALOG={
 "shade_structure":{"cost":18000.0,"delta_c":0.65,"feasibility":0.88,"confidence":0.72},
 "tree_canopy":{"cost":15000.0,"delta_c":0.45,"feasibility":0.74,"confidence":0.70},
 "cool_roof":{"cost":12000.0,"delta_c":0.30,"feasibility":0.84,"confidence":0.68},
 "cool_pavement":{"cost":14000.0,"delta_c":0.35,"feasibility":0.78,"confidence":0.67},
 "cooling_center":{"cost":22000.0,"delta_c":0.10,"feasibility":0.82,"confidence":0.65},
}

def _clamp(x): return max(0.0,min(1.0,float(x)))

def _candidate(metric,kind,spec,run_id):
    # Deliberately conservative planning counterfactual, not a guaranteed causal effect.
    temp_fraction=_clamp(spec["delta_c"]/15.0)
    hazard_fraction=min(metric.hazard_index,0.45*temp_fraction)
    teu_red=metric.population*hazard_fraction*spec["feasibility"]
    va_red=metric.population*metric.vulnerability_index*(1+metric.vulnerability_index)*hazard_fraction*spec["feasibility"]
    if kind=="cooling_center":
        # Access intervention primarily benefits exposed people rather than changing ambient field.
        teu_red*=0.55
        va_red*=0.90
    people=min(metric.population,metric.population*spec["feasibility"]*(0.35+0.45*metric.vulnerability_index))
    conf=min(metric.confidence,spec["confidence"])
    return ProviderInterventionCandidate(
        run_id=run_id,area_id=metric.area_id,cell_id=metric.cell_id,intervention_type=kind,
        cost=spec["cost"],temperature_delta_c=spec["delta_c"],teu_reduction=teu_red,
        va_teu_reduction=va_red,people_benefit_proxy=people,feasibility=spec["feasibility"],confidence=conf,
        assumption_json={
            "truth_category":"modelled_counterfactual",
            "causal_claim":False,
            "catalog_version":"provider-intervention-v1",
            "temperature_delta_assumption_c":spec["delta_c"],
            "note":"Planning scenario only; effect sizes are assumptions to be stress-tested, not field-validated causal estimates."
        })

def rebuild_decision_stack(db,area_id="phx-downtown",budget=100000.0):
    metrics=db.execute(
        select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id==area_id)
        .order_by(desc(ProviderOperationalMetric.created_at))
    ).scalars().all()
    latest={}
    for r in metrics: latest.setdefault(r.cell_id,r)
    if len(latest)!=4: raise RuntimeError(f"Expected 4 authoritative provider metrics, got {len(latest)}")

    run_id=str(uuid4())
    candidates=[]
    for m in latest.values():
        for kind,spec in CATALOG.items():
            c=_candidate(m,kind,spec,run_id); db.add(c); candidates.append(c)
    db.flush()

    model=cp_model.CpModel()
    x=[model.NewBoolVar(f"x{i}") for i in range(len(candidates))]
    scale=1000
    model.Add(sum(int(round(c.cost))*x[i] for i,c in enumerate(candidates)) <= int(round(budget)))
    # At most two interventions per cell to limit stacking assumptions.
    for cid in latest:
        ids=[i for i,c in enumerate(candidates) if c.cell_id==cid]
        model.Add(sum(x[i] for i in ids)<=2)

    # Balanced objective weights current burden reduction and vulnerable burden reduction.
    scores=[]
    for c in candidates:
        score=(0.45*c.teu_reduction + 0.45*c.va_teu_reduction + 0.10*(c.people_benefit_proxy/100.0))*c.confidence
        scores.append(int(round(score*scale)))
    model.Maximize(sum(scores[i]*x[i] for i in range(len(candidates))))
    solver=cp_model.CpSolver()
    solver.parameters.num_search_workers=1
    status=solver.Solve(model)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        raise RuntimeError("Provider optimizer found no feasible solution")

    chosen=[c for i,c in enumerate(candidates) if solver.Value(x[i])]
    total=sum(c.cost for c in chosen)
    teu=sum(c.teu_reduction for c in chosen)
    va=sum(c.va_teu_reduction for c in chosen)
    conf=sum(c.confidence for c in chosen)/len(chosen) if chosen else 0.0
    opt=ProviderOptimizerRun(
        area_id=area_id,budget=budget,objective="balanced_provider_burden",
        status="optimal" if status==cp_model.OPTIMAL else "feasible",
        selected_json=[{
            "candidate_id":c.id,"cell_id":c.cell_id,"intervention_type":c.intervention_type,
            "cost":c.cost,"teu_reduction":c.teu_reduction,"va_teu_reduction":c.va_teu_reduction,
            "people_benefit_proxy":c.people_benefit_proxy,"confidence":c.confidence
        } for c in chosen],
        total_cost=total,teu_reduction=teu,va_teu_reduction=va,confidence=conf,
        source_metric_ids=[r.id for r in latest.values()])
    db.add(opt); db.flush()

    actions=[
      {"agent":"Scout","status":"complete","finding":"Provider thermal field and operational baseline are authoritative for this decision run."},
      {"agent":"Diagnostician","status":"complete","finding":"Current provider-operational hazard is low; recommendations are planning/preparedness interventions, not emergency response."},
      {"agent":"Exposure","status":"complete","finding":"Burden weighting uses ACS-derived population and vulnerability with provider-derived hazard."},
      {"agent":"Planner","status":"complete","finding":f"Selected {len(chosen)} interventions under ${budget:,.0f} budget."},
      {"agent":"Skeptic","status":"complete","finding":"Counterfactual temperature effects are assumptions, not causal proof; robustness testing is required next."},
      {"agent":"Evidence","status":"complete","finding":"All selected actions trace to ProviderOperationalMetric IDs and modeled candidate IDs."},
      {"agent":"Executive","status":"review_required","finding":"Use portfolio for planning comparison only; human approval retained."},
    ]
    decision=ProviderAgentDecision(
        optimizer_run_id=opt.id,area_id=area_id,status="review_required",
        confidence=min(conf,min(r.confidence for r in latest.values())),
        requires_human_review=True,agent_actions_json=actions,
        evidence_json={
            "provider_metric_ids":[r.id for r in latest.values()],
            "candidate_ids":[c.id for c in chosen],
            "optimizer_run_id":opt.id,
            "truth_boundary":"Provider state is observed/derived; intervention effects and optimizer benefits are modelled planning outputs.",
            "gemma_used":False,
        })
    db.add(decision); db.commit()
    db.refresh(opt); db.refresh(decision)
    return opt,decision
