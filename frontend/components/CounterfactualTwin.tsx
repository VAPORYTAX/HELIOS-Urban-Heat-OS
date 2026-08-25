"use client";
import {useMemo,useState} from "react";
import {E,arr,fmt,labelAction,money,n,s} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";

export default function CounterfactualTwin(){
 const {activeCellId,activeCell}=useDecision();
 const live=useLive(E.interventions);
 const candidates=useMemo(()=>arr(live.data).filter(x=>String(x.cell_id)===activeCellId),[live.data,activeCellId]);
 const [candidateId,setCandidateId]=useState<string>("");
 const selected=candidates.find(x=>String(x.id)===candidateId)??candidates[0]??null;
 const beforeTeu=n(activeCell,"teu"),beforeVa=n(activeCell,"va_teu");
 const dTeu=n(selected,"teu_reduction"),dVa=n(selected,"va_teu_reduction");
 const afterTeu=beforeTeu!==null&&dTeu!==null?Math.max(0,beforeTeu-dTeu):null;
 const afterVa=beforeVa!==null&&dVa!==null?Math.max(0,beforeVa-dVa):null;
 const pct=beforeTeu&&dTeu!==null?Math.max(0,dTeu/beforeTeu*100):null;
 if(!activeCellId)return <section className="twin empty compact-empty">Select a provider-verified cell to open the Counterfactual Twin.</section>;
 return <section className="twin panel">
  <div className="twin-head"><div><div className="section-kicker">SIMULATE · COUNTERFACTUAL TWIN</div><h2>What changes if we intervene in {activeCellId}?</h2></div><span className="truth-badge modeled">MODELED COUNTERFACTUAL</span></div>
  {live.loading?<div className="empty compact-empty">Loading modeled interventions…</div>:live.error?<div className="errorbox">Counterfactual candidates unavailable: {live.error} <button onClick={live.retry}>Retry</button></div>:!selected?<div className="empty compact-empty">No provider-native intervention candidate is available for this cell.</div>:<>
   <label className="twin-picker"><span>Intervention</span><select value={String(selected.id)} onChange={e=>setCandidateId(e.target.value)}>{candidates.map(x=><option key={String(x.id)} value={String(x.id)}>{labelAction(x).replaceAll("_"," ")} · {money(n(x,"estimated_cost"))}</option>)}</select></label>
   <div className="twin-flow"><article><span>CURRENT</span><b>{fmt(beforeTeu,1)}</b><small>TEU</small><em>{fmt(beforeVa,1)} VA-TEU</em></article><i>→</i><article className="action"><span>INTERVENTION</span><b>{labelAction(selected).replaceAll("_"," ")}</b><small>{money(n(selected,"estimated_cost"))} · confidence {fmt(n(selected,"confidence"),2)}</small><em>{n(selected,"temperature_delta_c")!==null?`${fmt(n(selected,"temperature_delta_c"),2)} °C modeled temperature delta`:s(selected,"truth_category")}</em></article><i>→</i><article className="after"><span>MODELED AFTER</span><b>{fmt(afterTeu,1)}</b><small>TEU</small><em>{fmt(afterVa,1)} VA-TEU</em></article></div>
   <div className="twin-deltas"><div><span>Δ TEU</span><b>{dTeu!==null?`−${fmt(dTeu,1)}`:"—"}</b></div><div><span>Δ VA-TEU</span><b>{dVa!==null?`−${fmt(dVa,1)}`:"—"}</b></div><div><span>Modeled reduction</span><b>{pct!==null?`${fmt(pct,1)}%`:"—"}</b></div><div><span>Portfolio</span><b>{selected.selected?"SELECTED BY CP-SAT":"NOT SELECTED"}</b></div></div>
   <div className="truth-callout"><b>Modeled planning estimate — not a guaranteed causal effect.</b><p>After-values are deterministic arithmetic using the current cell burden and the backend-provided provider-native modeled reduction for this intervention. Assumptions and confidence remain attached to the candidate.</p></div>
   <details className="technical"><summary>Counterfactual evidence record</summary><pre>{JSON.stringify(selected,null,2)}</pre></details>
  </>}
 </section>
}
