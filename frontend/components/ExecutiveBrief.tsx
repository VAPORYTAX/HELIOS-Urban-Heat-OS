"use client";
import {useMemo,useState} from "react";
import {E,arr,fmt,money,n,providerOptimizer,s,labelAction} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";

export default function ExecutiveBrief(){
 const [open,setOpen]=useState(false);
 const {activeCellId,activeCell,providerRows}=useDecision();
 const optimizer=useLive(E.optimizer),interventions=useLive(E.interventions),system=useLive(E.system),journeys=useLive(E.journeys);
 const opt=providerOptimizer(optimizer.data),candidates=arr(interventions.data).filter(x=>String(x.cell_id)===activeCellId),selected=candidates.filter(x=>x.selected),journey=arr(journeys.data)[0]??null;
 const action=selected[0]??candidates[0]??null;
 const before=n(activeCell,"teu"),delta=n(action,"teu_reduction"),after=before!==null&&delta!==null?Math.max(0,before-delta):null;
 const beforeVa=n(activeCell,"va_teu"),deltaVa=n(action,"va_teu_reduction"),afterVa=beforeVa!==null&&deltaVa!==null?Math.max(0,beforeVa-deltaVa):null;
 const summary=useMemo(()=>[
  `HELIOS — Phoenix Heat Action Brief`,
  `Area: phx-downtown`,
  `Active cell: ${activeCellId??"not selected"}`,
  `Verified provider cells: ${providerRows.length}`,
  `Active-cell TEU: ${fmt(before,1)}`,
  `Active-cell VA-TEU: ${fmt(beforeVa,1)}`,
  `Portfolio: ${money(n(opt,"total_cost"))} selected from ${money(n(opt,"budget"))} budget; ${s(opt,"selected_count")} actions`,
  `Modeled portfolio impact: ${fmt(n(opt,"teu_reduction"),1)} TEU; ${fmt(n(opt,"va_teu_reduction"),1)} VA-TEU reduction`,
  action?`Active-cell modeled action: ${labelAction(action).replaceAll("_"," ")} (${action.selected?"selected":"not selected"})`:"Active-cell modeled action: unavailable",
  action?`Counterfactual TEU: ${fmt(before,1)} → ${fmt(after,1)}; VA-TEU: ${fmt(beforeVa,1)} → ${fmt(afterVa,1)}`:"Counterfactual: unavailable",
  journey?`ThermalWay validated journey available; modeled TEC saved ${fmt(n(journey,"saved"),1)} with ${fmt(n(journey,"extra_minutes"),1)} extra minutes.`:"ThermalWay journey: not loaded",
  `Truth: provider → derived → modeled → optimized → AI-explained. Human review required.`,
  `Limitation: current provider-validated footprint is four downtown Phoenix cells; modeled outputs are planning estimates, not guaranteed causal effects.`
 ].join("\n"),[activeCellId,providerRows.length,opt,action,before,after,beforeVa,afterVa,journey]);
 async function copy(){try{await navigator.clipboard.writeText(summary)}catch{}}
 return <>
  <button className="brief-launch" onClick={()=>setOpen(true)}>Generate Decision Brief</button>
  {open&&<div className="brief-backdrop" role="dialog" aria-modal="true" aria-label="HELIOS executive decision brief"><section className="brief-sheet">
   <header><div><span>HELIOS · EXECUTIVE DECISION OUTPUT</span><h1>PHOENIX HEAT ACTION BRIEF</h1><p>Decision-ready synthesis of provider evidence, deterministic analytics and governed explanation.</p></div><button onClick={()=>setOpen(false)} aria-label="Close brief">×</button></header>
   <div className="brief-grid"><article><span>AREA</span><b>PHX-DOWNTOWN</b><small>{providerRows.length||"—"} provider-verified cells</small></article><article><span>ACTIVE CELL</span><b>{activeCellId??"NOT SELECTED"}</b><small>TEU {fmt(before,1)} · VA-TEU {fmt(beforeVa,1)}</small></article><article><span>PORTFOLIO</span><b>{money(n(opt,"total_cost"))}</b><small>{s(opt,"selected_count")} actions · {s(opt,"solver_status","status")} CP-SAT</small></article><article><span>MODELED IMPACT</span><b>−{fmt(n(opt,"teu_reduction"),1)} TEU</b><small>−{fmt(n(opt,"va_teu_reduction"),1)} VA-TEU</small></article></div>
   <section className="brief-section"><div className="section-kicker">OBSERVED EVIDENCE</div><h2>Not every degree of heat creates the same human burden.</h2><div className="brief-two"><div><span>TEU</span><b>{fmt(before,1)}</b><small>thermal exposure planning burden</small></div><div><span>VA-TEU</span><b>{fmt(beforeVa,1)}</b><small>vulnerability-adjusted planning burden</small></div></div></section>
   <section className="brief-section"><div className="section-kicker">ACTIVE-CELL COUNTERFACTUAL</div>{action?<><h2>{labelAction(action).replaceAll("_"," ")} · {money(n(action,"estimated_cost"))}</h2><div className="brief-counter"><div><span>CURRENT TEU</span><b>{fmt(before,1)}</b></div><i>→</i><div><span>MODELED AFTER</span><b>{fmt(after,1)}</b></div><strong>{delta!==null?`−${fmt(delta,1)} TEU`:"—"}</strong></div><p>{action.selected?"This action is in the authoritative CP-SAT portfolio.":"This action is not in the authoritative selected portfolio under the current budget and constraints."}</p></>:<p>No modeled intervention candidate is available for the active cell.</p>}</section>
   <section className="brief-section"><div className="section-kicker">MOBILITY + AI + TRUST</div><div className="brief-three"><div><span>THERMALWAY</span><b>{journey?"VALIDATED JOURNEY":"AVAILABLE ON DEMAND"}</b><small>{journey?`${fmt(n(journey,"saved"),1)} modeled TEC saved · +${fmt(n(journey,"extra_minutes"),1)} min`:"Real OSM, modeled thermal cost"}</small></div><div><span>GEMMA 4</span><b>{(system.data as any)?.intelligence?.reachable?"REACHABLE":"NOT CONFIRMED"}</b><small>Explanation only · semantic firewall</small></div><div><span>HUMAN REVIEW</span><b>REQUIRED</b><small>Deterministic engines remain authoritative</small></div></div></section>
   <section className="brief-limit"><b>Decision boundary</b><p>Current live provider validation covers four downtown Phoenix cells only. TEU, VA-TEU, intervention effects and ThermalWay TEC are planning metrics; modeled reductions are not guaranteed causal outcomes.</p></section>
   <footer><button onClick={()=>window.print()}>Print</button><button onClick={copy}>Copy summary</button><button className="primary" onClick={()=>setOpen(false)}>Close</button></footer>
  </section></div>}
 </>
}
