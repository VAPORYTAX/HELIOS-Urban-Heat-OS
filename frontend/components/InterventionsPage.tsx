"use client";
import {useMemo,useState} from "react";
import {H,rows,num,str,money,fmt} from "@/lib/api";
import {useLive} from "./useLive";
import {PageTitle,Empty} from "./UI";

export default function InterventionsPage(){
 const x=useLive(H.interventions);const all=rows(x.data);const [q,setQ]=useState("");
 const data=useMemo(()=>all.filter(r=>JSON.stringify(r).toLowerCase().includes(q.toLowerCase())),[all,q]);
 return <div className="page"><PageTitle kicker="DESIGN MODE · COUNTERFACTUAL ACTIONS" title="Intervention Studio" description="Inspect feasible cooling actions, modeled benefits, cost and confidence. Counterfactual effects remain planning assumptions rather than causal proof." aside={<input className="search" value={q} onChange={e=>setQ(e.target.value)} placeholder="Filter actions…"/>}/>
 {x.error&&<div className="errorbox">{x.error}</div>}
 <div className="cards">{data.length?data.map((r,i)=><article className="intervention" key={str(r,"id","intervention_id")+i}>
  <div className="intervention-top"><div><span>MODELED INTERVENTION</span><h2>{str(r,"intervention_type","type","name","action")}</h2></div><b>{str(r,"cell_id")}</b></div>
  <div className="intervention-metrics"><div><span>Cost</span><b>{money(num(r,"cost","estimated_cost"))}</b></div><div><span>TEU benefit</span><b>{fmt(num(r,"estimated_teu_benefit","teu_reduction"),2)}</b></div><div><span>VA-TEU benefit</span><b>{fmt(num(r,"estimated_va_teu_benefit","va_teu_reduction"),2)}</b></div><div><span>Confidence</span><b>{fmt(num(r,"confidence"),2)}</b></div></div>
  <p>{str(r,"reason","rationale","description")}</p>
 </article>):<Empty>No intervention candidates returned by the live API.</Empty>}</div></div>
}
