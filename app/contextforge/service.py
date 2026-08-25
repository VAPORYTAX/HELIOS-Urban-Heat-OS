from __future__ import annotations
import hashlib, json
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.contextforge.contracts import ContextBuildRequest
from app.contextforge.prompts import BUNDLE_VERSION, PROMPTS
from app.contextforge.utility import context_utility, estimate_tokens, trim_ranked
from app.contextforge.provider_overlay import reconcile_provider_state
from app.contextforge.provider_decision_overlay import inject_provider_decision
from app.db.models_context import ContextPacket, PromptRegistry
from app.db.models_demographics import CellDemographic
from app.db.models_exposure import DriverAttribution, ExposureMetric, Facility, UrbanContextCell
from app.db.models_interventions import ScenarioResult
from app.db.models_optimizer import OptimizationRun, OptimizationSelection
from app.db.models_quality import QualitySnapshot
from app.db.models_thermal import ThermalCell, ThermalHotspot, ThermalObservation

def seed_prompts(db:Session):
    for item in PROMPTS:
        row=db.get(PromptRegistry,item["id"])
        if row is None:
            row=PromptRegistry(id=item["id"]); db.add(row)
        row.name=item["name"]; row.version=item["version"]; row.role=item["role"]
        row.template_text=item["template"]; row.active=True
        row.metadata_json={"bundle_version":BUNDLE_VERSION}
    db.commit()

def latest(db,model,*criteria,order_field):
    q=select(model)
    for c in criteria: q=q.where(c)
    return db.execute(q.order_by(desc(order_field)).limit(1)).scalar_one_or_none()

def evidence_item(kind,ref,truth,confidence,relevance,spatial,freshness,impact,payload):
    return {
        "kind":kind,"ref":str(ref),"truth_category":truth,"confidence":confidence,
        "utility_score":context_utility(relevance=relevance,confidence=confidence,spatial_match=spatial,freshness=freshness,decision_impact=impact),
        "payload":payload,
    }

def build_context_packet(db:Session,req:ContextBuildRequest):
    seed_prompts(db)
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==req.area_id)).scalars().all()
    if not cells: raise ValueError("area has no thermal cells")

    evidence=[]; summaries=[]
    for cell in cells:
        obs=latest(db,ThermalObservation,ThermalObservation.cell_id==cell.id,order_field=ThermalObservation.observed_at)
        exp=latest(db,ExposureMetric,ExposureMetric.cell_id==cell.id,order_field=ExposureMetric.observed_at)
        drv=latest(db,DriverAttribution,DriverAttribution.cell_id==cell.id,order_field=DriverAttribution.observed_at)
        ctx=db.execute(select(UrbanContextCell).where(UrbanContextCell.cell_id==cell.id)).scalar_one_or_none()
        demo=db.execute(select(CellDemographic).where(CellDemographic.cell_id==cell.id)).scalar_one_or_none()

        if obs:
            truth=getattr(obs,"source_type","unknown")
            evidence.append(evidence_item("thermal_observation",obs.id,truth,0.80 if truth=="fixture" else 0.95,0.95,1.0,0.45 if truth=="fixture" else 0.9,0.95,{
                "cell_id":cell.id,"temperature_c":obs.temperature_c,"observed_at":obs.observed_at.isoformat()}))
        if demo:
            evidence.append(evidence_item("demographics",demo.id,demo.source_json.get("truth_category","derived"),demo.confidence,0.9,1.0,0.95,0.95,{
                "cell_id":cell.id,"population":demo.population,"population_density_km2":demo.population_density_km2,
                "under5_population":demo.under5_population,"age65_population":demo.age65_population,
                "poverty_population":demo.poverty_population,"no_vehicle_households":demo.no_vehicle_households,
                "vulnerability_index":demo.vulnerability_index}))
        if ctx:
            evidence.append(evidence_item("urban_context",ctx.id,(ctx.source_json or {}).get("truth_category","mixed"),ctx.data_quality,0.85,1.0,0.9,0.8,{
                "cell_id":cell.id,"vegetation_fraction":ctx.vegetation_fraction,"impervious_fraction":ctx.impervious_fraction,
                "building_fraction":ctx.building_fraction,"road_fraction":ctx.road_fraction,"shade_fraction":ctx.shade_fraction,
                "solar_exposure_index":ctx.solar_exposure_index}))
        if exp and drv:
            s={"cell_id":cell.id,"teu":exp.teu,"va_teu":exp.vulnerable_teu,"hazard_index":exp.hazard_index,
               "exposure_index":exp.exposure_index,"vulnerability_index":exp.vulnerability_index,
               "confidence":exp.confidence,"dominant_driver":drv.dominant_driver,"driver_confidence":drv.confidence}
            summaries.append(s)
            evidence.append(evidence_item("exposure_metric",exp.id,"derived",exp.confidence,1.0,1.0,0.9,1.0,s))

    hotspots=db.execute(select(ThermalHotspot).where(ThermalHotspot.area_id==req.area_id).order_by(desc(ThermalHotspot.detected_at)).limit(5)).scalars().all()
    for h in hotspots:
        evidence.append(evidence_item("hotspot",h.id,"derived",h.confidence,0.9,1.0,0.6,0.95,{
            "severity":h.severity,"peak_temperature_c":h.peak_temperature_c,"mean_anomaly_c":h.mean_anomaly_c,
            "persistence_hours":h.max_persistence_hours,"detected_at":h.detected_at.isoformat()}))

    facilities=db.execute(select(Facility).where(Facility.area_id==req.area_id)).scalars().all()
    evidence.append(evidence_item("facilities_summary",f"area:{req.area_id}:facilities","observed",0.9,0.65,1.0,0.95,0.65,{
        "count":len(facilities),"types":sorted({f.facility_type for f in facilities})}))

    quality=db.execute(select(QualitySnapshot).where(QualitySnapshot.area_id==req.area_id).order_by(desc(QualitySnapshot.created_at)).limit(1)).scalar_one_or_none()
    if quality:
        evidence.append(evidence_item("quality_snapshot",quality.id,"derived",quality.health_score,1,1,1,1,{
            "status":quality.status,"health_score":quality.health_score,"requires_human_review":quality.requires_human_review}))

    opt=db.execute(select(OptimizationRun).where(OptimizationRun.area_id==req.area_id,OptimizationRun.status=="complete").order_by(desc(OptimizationRun.created_at)).limit(1)).scalar_one_or_none()
    opt_summary=None
    if opt:
        sels=db.execute(select(OptimizationSelection).where(OptimizationSelection.run_id==opt.id)).scalars().all()
        sc=db.execute(select(ScenarioResult).where(ScenarioResult.scenario_id==opt.scenario_id)).scalar_one_or_none() if opt.scenario_id else None
        opt_summary={"run_id":opt.id,"objective":opt.objective,"budget":opt.budget,"total_cost":opt.total_cost,"selected_count":opt.selected_count,
                     "actions":[{"cell_id":s.cell_id,"intervention_id":s.intervention_id,"cost":s.cost,
                                 "estimated_teu_benefit":s.estimated_teu_benefit,
                                 "estimated_va_teu_benefit":s.estimated_vulnerable_teu_benefit,
                                 "confidence":s.confidence} for s in sels],
                     "scenario":None if not sc else {"teu_reduction":sc.teu_reduction,"teu_reduction_pct":sc.teu_reduction_pct,
                                                   "va_teu_reduction":sc.vulnerable_teu_reduction,"thermal_roi":sc.thermal_roi,
                                                   "confidence":sc.confidence,"uncertainty_interval":[sc.lower_teu_reduction,sc.upper_teu_reduction]}}
        evidence.append(evidence_item("optimizer",opt.id,"modelled",sc.confidence if sc else 0.7,1,1,0.95,1,opt_summary))

    ranked,evidence_tokens=trim_ranked(evidence,max(1000,int(req.token_budget*0.50)))
    prompts=db.execute(select(PromptRegistry).where(PromptRegistry.active.is_(True)).order_by(PromptRegistry.id)).scalars().all()
    packet={
      "schema":"helios.context.packet.v1",
      "mission":"Reduce urban heat burden through evidence-grounded intervention decisions.",
      "task":{"task_type":req.task_type,"mode":req.mode,"user_intent":req.user_intent,"area_id":req.area_id},
      "truth_policy":{"allowed_categories":["provider","observed","derived","modelled","assumed","fixture","mixed"],
                      "fixture_requires_review":True,"derived_is_not_observed":True,"diagnostic_is_not_causal":True},
      "state":{"cells":sorted(summaries,key=lambda x:x["teu"],reverse=True),"optimizer":opt_summary,
               "quality":None if not quality else {"status":quality.status,"health_score":quality.health_score,"requires_human_review":quality.requires_human_review}},
      "evidence_refs":[{"kind":x["kind"],"ref":x["ref"],"truth_category":x["truth_category"],"confidence":x["confidence"],"utility_score":x["utility_score"]} for x in ranked],
      "prompts":[{"name":p.name,"version":p.version,"role":p.role,"text":p.template_text} for p in prompts],
    }
    if req.include_raw_evidence: packet["ranked_evidence"]=ranked
    packet=reconcile_provider_state(db,packet,req.area_id)
    packet=inject_provider_decision(db,packet,req.area_id)
    canonical=json.dumps(packet,sort_keys=True,separators=(",",":"),default=str)
    ch=hashlib.sha256(canonical.encode()).hexdigest()
    tokens=estimate_tokens(packet)
    existing=db.execute(select(ContextPacket).where(ContextPacket.context_hash==ch)).scalar_one_or_none()
    if existing: return existing
    row=ContextPacket(area_id=req.area_id,task_type=req.task_type,mode=req.mode,user_intent=req.user_intent,
                      context_hash=ch,prompt_bundle_version=BUNDLE_VERSION,token_budget=req.token_budget,
                      estimated_tokens=tokens,status="ready" if tokens<=req.token_budget else "over_budget",
                      packet_json=packet,evidence_json={"ranked":ranked,"evidence_tokens":evidence_tokens})
    db.add(row); db.commit(); db.refresh(row); return row
