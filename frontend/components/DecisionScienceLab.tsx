"use client";
import {E,arr,fmt,money,n,s} from "@/lib/domain";
import {useLive} from "./useLive";

function objEntries(v:any){return v&&typeof v==="object"?Object.entries(v):[]}
export default function DecisionScienceLab(){
 const live=useLive(E.decisionScience),d:any=live.data??{};
 const scenarios=arr(d?.sensitivity?.scenarios),voi=arr(d?.value_of_information?.top_information_priorities),seq=arr(d?.sequencing);
 const budgets=objEntries(d?.reverse_optimization?.budget_frontier);
 const objectives=objEntries(d?.sensitivity?.objective_sensitivity);
 const wcm=objEntries(d?.what_changes_mind);
 return <section className="decision-science panel">
  <div className="decision-science-head"><div><div className="section-kicker">ROBUSTNESS · REGRET · VALUE OF INFORMATION</div><h2>Would the decision survive uncertainty?</h2><p>HELIOS stress-tests the current provider-native portfolio across effect and cost assumptions, alternative objectives and budget frontiers.</p></div><span className="truth-badge modeled">MODELED DECISION SCIENCE</span></div>
  {live.loading?<div className="empty compact-empty">Loading decision-science evidence…</div>:live.error?<div className="errorbox">Decision-science evidence unavailable: {live.error} <button onClick={live.retry}>Retry</button></div>:<>
   <div className="ds-metrics"><article><span>Robustness score</span><b>{fmt(n(d,"robustness_score"),2)}</b><small>share of stress scenarios retaining ≥75% portfolio overlap</small></article><article><span>Maximum regret</span><b>{fmt(n(d,"max_regret"),2)}</b><small>modeled objective-value opportunity loss</small></article><article><span>Mean regret</span><b>{fmt(n(d,"mean_regret"),2)}</b><small>across effect/cost stress grid</small></article><article><span>Status</span><b>{s(d,"status")}</b><small>human review required</small></article></div>
   <div className="ds-grid"><section><div className="section-kicker">SENSITIVITY</div><h3>Stress grid</h3><div className="scenario-grid">{scenarios.slice(0,20).map((x:any,i:number)=><div key={i}><span>{fmt(n(x,"effect_multiplier"),1)}× effect · {fmt(n(x,"cost_multiplier"),1)}× cost</span><b>Regret {fmt(n(x,"regret"),2)}</b><small>Jaccard {fmt(n(x,"selection_jaccard"),2)} · {s(x,"selected_count")} actions</small></div>)}</div></section><section><div className="section-kicker">OBJECTIVE SENSITIVITY</div><h3>What if priorities change?</h3><div className="objective-list">{objectives.map(([k,v]:any)=><div key={k}><span>{String(k).replaceAll("_"," ")}</span><b>{fmt(n(v,"value"),2)}</b><small>{money(n(v,"cost"))}</small></div>)}</div></section></div>
   <div className="ds-grid"><section><div className="section-kicker">VALUE OF INFORMATION</div><h3>Where better evidence matters most</h3><div className="voi-list">{voi.map((x:any,i:number)=><div key={s(x,"candidate_id",String(i))}><span>{String(i+1).padStart(2,"0")}</span><div><b>{s(x,"intervention_type").replaceAll("_"," ")}</b><small>{s(x,"cell_id")}</small></div><strong>{fmt(n(x,"voi_priority"),3)}</strong></div>)}</div></section><section><div className="section-kicker">REVERSE OPTIMIZATION</div><h3>Budget frontier</h3><div className="budget-frontier">{budgets.map(([k,v]:any)=><div key={k}><span>{money(Number(k))}</span><b>{fmt(n(v,"value"),1)}</b><small>{s(v,"selected_count")} actions · spend {money(n(v,"cost"))}</small></div>)}</div></section></div>
   <div className="ds-grid"><section><div className="section-kicker">INTERVENTION SEQUENCING</div><h3>What should happen first?</h3><div className="sequence-list">{seq.map((x:any)=><div key={s(x,"candidate_id")}><span>{s(x,"sequence")}</span><div><b>{s(x,"intervention_type").replaceAll("_"," ")}</b><small>{s(x,"cell_id")} · {money(n(x,"cost"))}</small></div><strong>{fmt(n(x,"priority_score"),5)}</strong></div>)}</div></section><section><div className="section-kicker">WHAT WOULD CHANGE MY MIND?</div><h3>Explicit reconsideration triggers</h3><div className="wcm-list">{wcm.map(([k,v])=><div key={k}><b>{String(k).replaceAll("_"," ")}</b><span>{typeof v==="boolean"?(v?"TRIGGERED":"NOT TRIGGERED"):String(v)}</span></div>)}</div></section></div>
   <details className="technical"><summary>Raw decision-science record</summary><pre>{JSON.stringify(d,null,2)}</pre></details>
  </>}
 </section>
}
