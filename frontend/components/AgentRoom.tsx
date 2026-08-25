"use client";
import {E,arr,fmt,n,s} from "@/lib/domain";
import {useLive} from "./useLive";

export default function AgentRoom(){
 const runs=useLive(E.agents),latest=useLive(E.latestAgent),rows=arr(runs.data),rec:any=latest.data??{};
 const summary=rows[0]?.summary??{};
 return <section className="agent-room panel"><div className="agent-room-head"><div><div className="section-kicker">AGENT ROOM · GOVERNED DECISION ORCHESTRATION</div><h2>Multiple reasoning roles. One evidence boundary.</h2><p>HELIOS separates agent findings, evidence records, recommendation synthesis and skeptical review. Human approval remains mandatory.</p></div><span className="truth-badge modeled">GOVERNED</span></div>
 {runs.loading||latest.loading?<div className="empty compact-empty">Loading governed agent evidence…</div>:runs.error||latest.error?<div className="errorbox">Agent evidence unavailable: {runs.error??latest.error} <button onClick={()=>{runs.retry();latest.retry()}}>Retry</button></div>:<>
  <div className="agent-metrics"><article><span>Latest run</span><b>{s(rows[0],"status")}</b><small>{s(rows[0],"mode")}</small></article><article><span>Confidence</span><b>{fmt(n(rows[0],"confidence"),2)}</b><small>run-level confidence</small></article><article><span>Decision</span><b>{s(rec,"decision_status")}</b><small>{s(rec,"headline")}</small></article><article><span>Human review</span><b>{rec?.requires_human_review?"REQUIRED":"CHECK"}</b><small>cannot be bypassed</small></article></div>
  <div className="agent-flow"><div><span>01</span><b>EVIDENCE</b><small>Provider + deterministic state</small></div><i>→</i><div><span>02</span><b>ANALYSIS</b><small>Structured findings</small></div><i>→</i><div><span>03</span><b>SKEPTIC</b><small>Challenge assumptions</small></div><i>→</i><div><span>04</span><b>RECOMMEND</b><small>Review-required synthesis</small></div><i>→</i><div><span>05</span><b>HUMAN</b><small>Approve / reject / revise</small></div></div>
  <div className="agent-grid"><section><div className="section-kicker">LATEST RECOMMENDATION</div><h3>{s(rec,"headline")}</h3><div className="agent-actions">{arr(rec?.recommended_actions).map((x:any,i:number)=><div key={i}><b>{s(x,"action","cell_id",`Action ${i+1}`)}</b><span>{s(x,"reason","rationale","status")}</span></div>)}</div></section><section><div className="section-kicker">SKEPTIC FINDINGS</div><h3>What could invalidate the decision?</h3><pre className="clean-pre">{JSON.stringify(rec?.skeptic_findings??summary?.skeptic_findings??{},null,2)}</pre></section></div>
  <details className="technical"><summary>Governed agent records</summary><pre>{JSON.stringify({latest_run:rows[0],recommendation:rec},null,2)}</pre></details>
 </>}
 </section>
}
