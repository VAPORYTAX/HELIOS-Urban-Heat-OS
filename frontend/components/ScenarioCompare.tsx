"use client";
import {useEffect,useState} from "react";
import {E,arr,fmt,money,n,s} from "@/lib/domain";
import {useLive} from "./useLive";

export default function ScenarioCompare(){
 const scenarios=useLive(E.scenarios),rows=arr(scenarios.data).slice(0,3),[results,setResults]=useState<any[]>([]),[error,setError]=useState<string|null>(null);
 useEffect(()=>{let mounted=true;if(!rows.length){setResults([]);return}Promise.all(rows.map(async x=>{try{return await E.scenarioResult(String(x.id))}catch{return null}})).then(x=>mounted&&setResults(x)).catch(e=>mounted&&setError(e.message));return()=>{mounted=false}},[scenarios.data]);
 return <section className="scenario-compare panel"><div className="scenario-head"><div><div className="section-kicker">SCENARIO COMPARE · COUNTERFACTUAL PORTFOLIOS</div><h2>What changes across modeled intervention scenarios?</h2><p>Compare stored deterministic scenario results without converting modeled effects into causal promises.</p></div><span className="truth-badge modeled">MODELED</span></div>
 {scenarios.loading?<div className="empty compact-empty">Loading scenario records…</div>:scenarios.error||error?<div className="errorbox">Scenario comparison unavailable: {scenarios.error??error} <button onClick={scenarios.retry}>Retry</button></div>:!rows.length?<div className="empty compact-empty">No stored scenarios are available.</div>:<div className="scenario-cards">{rows.map((x:any,i:number)=>{const r=results[i]??{};return <article key={s(x,"id")}><header><span>SCENARIO {i+1}</span><b>{s(x,"name")}</b><small>{s(x,"status")} · {s(x,"objective")}</small></header><div><span>Budget</span><b>{money(n(x,"budget"))}</b></div><div><span>Baseline TEU</span><b>{fmt(n(r,"baseline_teu"),1)}</b></div><div><span>Modeled TEU</span><b>{fmt(n(r,"projected_teu"),1)}</b></div><div className="accent"><span>Modeled reduction</span><b>{fmt(n(r,"teu_reduction"),1)}</b><small>{fmt(n(r,"teu_reduction_pct"),1)}%</small></div><div><span>VA-TEU reduction</span><b>{fmt(n(r,"vulnerable_teu_reduction"),1)}</b></div><div><span>Confidence</span><b>{fmt(n(r,"confidence"),2)}</b></div></article>})}</div>}
 <div className="truth-callout"><b>Scenario comparison is planning evidence.</b><p>Counterfactual scenario outputs show modeled differences under explicit assumptions; they are not measured causal impacts.</p></div>
 </section>
}
