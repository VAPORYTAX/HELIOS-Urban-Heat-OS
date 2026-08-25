"use client";
import Link from "next/link";
import {useMemo,useState} from "react";
import {E,arr,n,money,fmt,labelAction,s} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";
import CounterfactualTwin from "./CounterfactualTwin";
import ScenarioCompare from "./ScenarioCompare";

export default function Interventions(){
 const live=useLive(E.interventions),all=arr(live.data),{activeCellId}=useDecision(),[q,setQ]=useState(""),[selectedOnly,setSelectedOnly]=useState(false),[activeOnly,setActiveOnly]=useState(true);
 const shown=useMemo(()=>all.filter(v=>(!activeOnly||String(v.cell_id)===activeCellId)&&(!selectedOnly||v.selected)&&JSON.stringify(v).toLowerCase().includes(q.toLowerCase())),[all,q,selectedOnly,activeOnly,activeCellId]);
 return <div className="page interventions-page"><div className="page-title"><div><div className="eyebrow">INTERVENE + SIMULATE · PHYSICAL COOLING OPTIONS</div><h1>From hotspot to physical action.</h1><p>HELIOS carries the active provider-verified cell into candidate actions, transparent counterfactuals and scenario comparison.</p></div><Link className="page-cta" href="/investment">Send candidates to Portfolio Optimizer →</Link></div>
 <section className="active-strip"><span>ACTIVE DECISION CELL</span><b>{activeCellId??"Selecting…"}</b><small>Every action below remains a modeled planning candidate until human review.</small></section>
 <div className="intervention-tools"><input className="search" value={q} onChange={e=>setQ(e.target.value)} placeholder="Filter by action or cell…"/><button className={activeOnly?"active":""} onClick={()=>setActiveOnly(x=>!x)}>Active cell only</button><button className={selectedOnly?"active":""} onClick={()=>setSelectedOnly(x=>!x)}>CP-SAT selected only</button><span>{shown.length} of {all.length} candidates</span></div>
 {live.loading&&<div className="empty">Loading provider-native candidates…</div>}{live.error&&<div className="empty">Backend unavailable: {live.error} <button onClick={live.retry}>Retry</button></div>}{!live.loading&&!live.error&&!shown.length&&<div className="empty">No intervention candidates match this view.</div>}
 <div className="cards">{shown.map(v=><article className={`intervention ${v.selected?"selected":""}`} key={s(v,"id")}><div className="intervention-top"><div><span className="truth-badge modeled">MODELED</span><h2>{labelAction(v).replaceAll("_"," ")}</h2></div><b>{s(v,"cell_id")}</b></div>{v.selected&&<div className="selected-ribbon">SELECTED BY CP-SAT</div>}<div className="intervention-metrics"><div><span>Estimated cost</span><b>{money(n(v,"estimated_cost"))}</b></div><div><span>Modeled TEU reduction</span><b>{fmt(n(v,"teu_reduction"),2)}</b></div><div><span>Modeled VA-TEU reduction</span><b>{fmt(n(v,"va_teu_reduction"),2)}</b></div><div><span>Confidence</span><b>{fmt(n(v,"confidence"),2)}</b></div></div><div className="fit-note"><b>Diagnostic fit</b><p>Feasibility {fmt(n(v,"feasibility"),2)}. {v.assumptions?.note??"Planning scenario only; effect sizes require stress testing."}</p><small>Diagnostic association—not causal proof.</small></div><footer>{s(v,"truth_category")} · human review required</footer></article>)}</div>
 <CounterfactualTwin/>
 <ScenarioCompare/>
 <section className="handoff-panel"><div><div className="section-kicker">NEXT · OPTIMIZE</div><h2>Which combination creates the strongest budget-feasible portfolio?</h2><p>Send these modeled actions to the authoritative provider-native CP-SAT portfolio record.</p></div><Link href="/investment">Open Portfolio Intelligence →</Link></section>
 </div>
}
