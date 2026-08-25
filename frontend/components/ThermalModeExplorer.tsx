"use client";
import {useState} from "react";
import {E,fmt,n,s} from "@/lib/domain";

type P=[number,number];
const ORIGIN:P=[-112.0775,33.4465];
const DESTINATION:P=[-112.0665,33.4545];
const PROFILE="older_adult";
const MODES=[
 {id:"fastest" as const,label:"FASTEST",definition:"Minimize travel time",accent:"fast"},
 {id:"cool" as const,label:"COOL ROUTE",definition:"Minimize cumulative modeled heat exposure",accent:"cool"},
 {id:"warm" as const,label:"WARM ROUTE",definition:"Minimize cumulative modeled cold exposure",accent:"warm"},
 {id:"thermal_safe" as const,label:"THERMAL-SAFE",definition:"Minimize modeled thermal stress",accent:"safe"},
];
export default function ThermalModeExplorer(){
 const [rows,setRows]=useState<any[]>([]),[busy,setBusy]=useState(false),[error,setError]=useState<string|null>(null);
 async function run(){setBusy(true);setError(null);try{const values=await Promise.all(MODES.map(m=>E.routeMode(ORIGIN,DESTINATION,PROFILE,m.id)));setRows(values)}catch(e:any){setRows([]);setError(e.message)}finally{setBusy(false)}}
 return <section className="thermal-mode-explorer panel"><div className="mode-explorer-head"><div><div className="section-kicker">THERMALWAY · FOUR ROUTING OBJECTIVES</div><h2>One journey. Four different definitions of “best.”</h2><p>Fastest, Cool Route, Warm Route and Thermal-Safe Route use the same real OSM graph while optimizing different explicit objectives from the available provider now-state.</p></div><button className="page-cta" onClick={run} disabled={busy}>{busy?"Computing four routes…":"Run all four modes"}</button></div>
 {error&&<div className="errorbox">Route-mode comparison unavailable: {error}. No cached route is presented as a new calculation.</div>}
 <div className="mode-cards">{MODES.map((m,i)=>{const x=rows[i];return <article className={m.accent} key={m.id}><header><span>{m.label}</span><b>{m.definition}</b></header><div><span>Distance</span><b>{x?`${fmt((n(x,"distance_m")??0)/1000,2)} km`:"—"}</b></div><div><span>Duration</span><b>{x?`${fmt(n(x,"duration_min"),1)} min`:"—"}</b></div><div><span>Modeled thermal cost</span><b>{x?fmt(n(x,"thermal_exposure_cost"),1):"—"}</b></div><small>{x?s(x,"mode_contract"):"Run the live comparison to populate."}</small></article>})}</div>
 <div className="truth-callout"><b>Warm Route is not a heat-avoidance route.</b><p>It minimizes modeled cold exposure when cold stress exists. In the current hot Phoenix provider field, its cold-stress signal may be zero or weak. Thermal-Safe minimizes the modeled thermal-stress objective; all route thermal costs are planning metrics, not medical risk.</p></div>
 </section>
}
