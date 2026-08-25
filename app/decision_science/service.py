from __future__ import annotations
from itertools import product
from statistics import mean
from sqlalchemy import desc,select
from ortools.sat.python import cp_model
from app.db.models_provider_decision import ProviderInterventionCandidate,ProviderOptimizerRun
from app.db.models_decision_science import DecisionScienceRun

def _solve(cands,budget,effect_mult=1.0,cost_mult=1.0,objective="balanced"):
    model=cp_model.CpModel()
    xs=[model.NewBoolVar(f"x{i}") for i in range(len(cands))]
    costs=[int(round(c.cost*cost_mult)) for c in cands]
    model.Add(sum(costs[i]*xs[i] for i in range(len(cands)))<=int(round(budget)))
    by_cell={}
    for i,c in enumerate(cands): by_cell.setdefault(c.cell_id,[]).append(i)
    for ids in by_cell.values(): model.Add(sum(xs[i] for i in ids)<=2)
    vals=[]
    for c in cands:
        teu=c.teu_reduction*effect_mult
        va=c.va_teu_reduction*effect_mult
        people=c.people_benefit_proxy
        if objective=="teu": score=teu
        elif objective=="vulnerable": score=va
        elif objective=="people": score=people/10.0
        else: score=.45*teu+.45*va+.10*(people/100.0)
        vals.append(int(round(score*c.confidence*1000)))
    model.Maximize(sum(vals[i]*xs[i] for i in range(len(cands))))
    solver=cp_model.CpSolver(); solver.parameters.num_search_workers=1
    status=solver.Solve(model)
    chosen=[i for i,x in enumerate(xs) if solver.Value(x)] if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else []
    value=sum(vals[i] for i in chosen)/1000.0
    return chosen,value,sum(costs[i] for i in chosen)

def run_decision_science(db,area_id="phx-downtown"):
    opt=db.execute(select(ProviderOptimizerRun).where(ProviderOptimizerRun.area_id==area_id).order_by(desc(ProviderOptimizerRun.created_at)).limit(1)).scalar_one()
    run_id=None
    if opt.selected_json:
        selected_ids={x["candidate_id"] for x in opt.selected_json}
    else:
        selected_ids=set()
    # candidates from the same decision generation are identified by selected candidate run_id
    sel=db.execute(select(ProviderInterventionCandidate).where(ProviderInterventionCandidate.id.in_(selected_ids))).scalars().all()
    if not sel: raise RuntimeError("Selected provider candidates not found")
    run_id=sel[0].run_id
    cands=db.execute(select(ProviderInterventionCandidate).where(ProviderInterventionCandidate.run_id==run_id)).scalars().all()

    base_idx=[i for i,c in enumerate(cands) if c.id in selected_ids]
    scenarios=[]
    regrets=[]
    stable=0
    grids=list(product([0.60,0.80,1.00,1.20,1.40],[0.90,1.00,1.10,1.20]))
    for em,cm in grids:
        idx,val,cost=_solve(cands,opt.budget,em,cm,"balanced")
        base_val=sum((.45*cands[i].teu_reduction*em+.45*cands[i].va_teu_reduction*em+.10*(cands[i].people_benefit_proxy/100))*cands[i].confidence for i in base_idx if cands[i].cost*cm+sum(cands[j].cost*cm for j in base_idx if j<i)<=opt.budget)
        regret=max(0.0,val-base_val)
        regrets.append(regret)
        same=len(set(idx).intersection(base_idx))/max(1,len(set(idx).union(base_idx)))
        if same>=0.75: stable+=1
        scenarios.append({"effect_multiplier":em,"cost_multiplier":cm,"optimal_value":val,"base_value":base_val,"regret":regret,"selection_jaccard":same,"selected_count":len(idx),"cost":cost})
    robustness=stable/len(grids)

    objectives={}
    for obj in ("balanced","teu","vulnerable","people"):
        idx,val,cost=_solve(cands,opt.budget,1,1,obj)
        objectives[obj]={"value":val,"cost":cost,"selected":[cands[i].id for i in idx]}

    budgets={}
    for b in (50000,75000,100000,125000,150000):
        idx,val,cost=_solve(cands,b,1,1,"balanced")
        budgets[str(b)]={"value":val,"cost":cost,"selected_count":len(idx)}

    # VOI proxy: candidates close to the selection boundary deserve better effect/cost evidence.
    scored=[]
    for c in cands:
        score=(.45*c.teu_reduction+.45*c.va_teu_reduction+.10*(c.people_benefit_proxy/100))*c.confidence/max(c.cost,1)
        scored.append((score,c))
    scored.sort(reverse=True,key=lambda x:x[0])
    boundary=scored[min(len(scored)-1,max(0,len(base_idx)-1))][0]
    voi=[]
    for score,c in scored:
        proximity=1/(1+abs(score-boundary)*100000)
        uncertainty=1-c.confidence
        v=proximity*uncertainty
        voi.append({"candidate_id":c.id,"cell_id":c.cell_id,"intervention_type":c.intervention_type,"voi_priority":v,"reason":"selection-boundary proximity × uncertainty"})
    voi=sorted(voi,key=lambda x:x["voi_priority"],reverse=True)[:8]

    seq=sorted(
        [{"candidate_id":c.id,"cell_id":c.cell_id,"intervention_type":c.intervention_type,"cost":c.cost,
          "priority_score":((c.teu_reduction+c.va_teu_reduction)*c.confidence/max(c.cost,1)),
          "teu_reduction":c.teu_reduction,"va_teu_reduction":c.va_teu_reduction}
         for c in cands if c.id in selected_ids],
        key=lambda x:x["priority_score"],reverse=True)
    for i,x in enumerate(seq,1): x["sequence"]=i

    wcm={
      "effect_assumption_drop": "Portfolio should be reconsidered if intervention effects fall materially below 60% of assumed values.",
      "cost_escalation": "Portfolio should be reconsidered if delivered costs exceed 120% of catalog assumptions.",
      "provider_state_change": "Any new provider thermal field that materially changes cell burden ranking should trigger a full rebuild.",
      "vulnerability_update": "New demographic evidence that changes vulnerability ranking should trigger re-optimization.",
      "selection_instability": robustness < 0.75,
    }

    row=DecisionScienceRun(
        area_id=area_id,optimizer_run_id=opt.id,status="review_required",
        robustness_score=robustness,max_regret=max(regrets),mean_regret=mean(regrets),
        sensitivity_json={"scenarios":scenarios,"objective_sensitivity":objectives},
        voi_json={"top_information_priorities":voi},
        reverse_optimization_json={"budget_frontier":budgets},
        sequencing_json=seq,what_changes_mind_json=wcm)
    db.add(row);db.commit();db.refresh(row)
    return row
