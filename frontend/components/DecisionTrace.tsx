"use client";
import {E,arr,n,providerOptimizer,s} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";

export default function DecisionTrace({compact=false}:{compact?:boolean}){
 const {activeCellId,activeCell}=useDecision();
 const interventions=useLive(E.interventions),optimizer=useLive(E.optimizer);
 const candidates=arr(interventions.data).filter(x=>!activeCellId||String(x.cell_id)===activeCellId);
 const opt=providerOptimizer(optimizer.data);
 const selected=candidates.filter(x=>x.selected);
 const stages=[
  ["OBSERVATION",activeCell?"PROVIDER VERIFIED":"WAITING",activeCellId??"Select a verified cell"],
  ["EXPOSURE",activeCell?"COMPUTED":"WAITING",activeCell?`TEU ${n(activeCell,"teu")?.toFixed(1)??"—"} · VA-TEU ${n(activeCell,"va_teu")?.toFixed(1)??"—"}`:"No live cell selected"],
  ["INTERVENTIONS",interventions.loading?"LOADING":`${candidates.length} CANDIDATES`,candidates.length?"Provider-native modeled actions":"No candidate evidence"],
  ["COUNTERFACTUAL",candidates.length?"AVAILABLE":"WAITING",candidates.length?"Modeled action deltas available":"Select a cell with candidates"],
  ["OPTIMIZER",optimizer.loading?"LOADING":selected.length?"SELECTED":"NOT SELECTED",selected.length?`${selected.length} selected action${selected.length===1?"":"s"} for active cell`:`Portfolio ${s(opt,"solver_status","status")}`],
  ["GEMMA","EXPLANATION ONLY","Cannot change deterministic evidence"],
  ["HUMAN","APPROVAL REQUIRED","Final decision remains with human reviewer"],
 ];
 return <section className={`decision-trace ${compact?"compact":""}`}>
  <div className="trace-head"><div><span>DECISION TRACE</span><b>{activeCellId??"No active cell"}</b></div><small>Provider evidence → deterministic engines → governed explanation</small></div>
  <div className="trace-flow">{stages.map(([name,status,detail],i)=><div className="trace-step" key={name}><div><span>{name}</span><b>{status}</b><small>{detail}</small></div>{i<stages.length-1&&<i>↓</i>}</div>)}</div>
 </section>
}
