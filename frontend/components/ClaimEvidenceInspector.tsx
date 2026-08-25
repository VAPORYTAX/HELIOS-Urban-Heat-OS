"use client";
import {E,fmt,n,providerOptimizer,s} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";

export default function ClaimEvidenceInspector(){
 const {activeCellId,activeCell}=useDecision();
 const ox=useLive(E.optimizer),dx=useLive(E.decisionScience),opt=providerOptimizer(ox.data),ds:any=dx.data??{};
 const claims=[
  {claim:`${activeCellId??"Active cell"} current temperature`,value:`${fmt(n(activeCell,"current_c"),1)} °C`,category:"PROVIDER / DERIVED",source:"FortyGuard operational metric",confidence:fmt(n(activeCell,"confidence"),2),boundary:"Current verified AOI only"},
  {claim:"Active-cell thermal exposure burden",value:`${fmt(n(activeCell,"teu"),1)} TEU`,category:"DERIVED",source:"HELIOS exposure engine",confidence:fmt(n(activeCell,"confidence"),2),boundary:"Planning metric"},
  {claim:"Active-cell vulnerability-adjusted burden",value:`${fmt(n(activeCell,"va_teu"),1)} VA-TEU`,category:"DERIVED",source:"HELIOS exposure + vulnerability context",confidence:fmt(n(activeCell,"confidence"),2),boundary:"Aggregate planning metric"},
  {claim:"Selected portfolio cost",value:s(opt,"total_cost")!=="—"?`$${Number(n(opt,"total_cost")??0).toLocaleString()}`:"—",category:"OPTIMIZED",source:"Provider-native CP-SAT record",confidence:fmt(n(opt,"confidence"),2),boundary:"Budget-constrained recommendation"},
  {claim:"Modeled portfolio TEU reduction",value:fmt(n(opt,"teu_reduction"),1),category:"MODELED + OPTIMIZED",source:"Counterfactual + CP-SAT",confidence:fmt(n(opt,"confidence"),2),boundary:"Not a causal guarantee"},
  {claim:"Decision robustness",value:fmt(n(ds,"robustness_score"),2),category:"MODELED",source:"Decision-science stress test",confidence:"—",boundary:"Scenario-dependent planning evidence"},
 ];
 return <section className="claim-inspector panel"><div className="claim-head"><div><div className="section-kicker">CLAIM / EVIDENCE INSPECTOR</div><h2>What exactly is HELIOS claiming?</h2><p>Every headline decision value is paired with its evidence class, source, confidence where available, and the boundary a judge should retain.</p></div><span>NO HIDDEN TRUTH PROMOTION</span></div><div className="claim-table"><div className="claim-row head"><b>Claim</b><b>Value</b><b>Truth category</b><b>Evidence source</b><b>Confidence</b><b>Boundary</b></div>{claims.map((x,i)=><div className="claim-row" key={i}><span>{x.claim}</span><strong>{x.value}</strong><em>{x.category}</em><span>{x.source}</span><span>{x.confidence}</span><small>{x.boundary}</small></div>)}</div><div className="truth-callout"><b>AI-explained claims never replace these evidence records.</b><p>Gemma may summarize this ledger, but provider, derived, modeled and optimized values remain authoritative in their own truth categories.</p></div></section>
}
