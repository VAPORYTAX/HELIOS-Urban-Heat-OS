"use client";
import Link from "next/link";
import {useEffect,useState} from "react";
import {useDecision} from "./DecisionContext";

const STEPS=[
 {stage:"OBSERVE",title:"Start with verified evidence",body:"Four provider-verified downtown Phoenix cells establish the live thermal evidence footprint. HELIOS carries one active cell through the entire decision loop.",href:"/atlas",cta:"Open Thermal Atlas"},
 {stage:"DIAGNOSE",title:"Quantify who carries the burden",body:"TEU measures planning exposure burden; VA-TEU adds vulnerability context so the decision does not ignore who bears the heat.",href:"/",cta:"See burden + equity"},
 {stage:"INTERVENE",title:"Move from hotspot to physical action",body:"Provider-native candidates translate the active cell into cooling options with cost, confidence and modeled benefit.",href:"/interventions",cta:"Open interventions"},
 {stage:"SIMULATE",title:"See before → action → modeled after",body:"The Counterfactual Twin applies backend-provided modeled reductions to the current active-cell burden without turning estimates into causal guarantees.",href:"/interventions",cta:"Open Counterfactual Twin"},
 {stage:"OPTIMIZE",title:"Make the budget decision",body:"Under the current budget and constraints, the authoritative CP-SAT portfolio identifies selected and non-selected modeled actions.",href:"/investment",cta:"Open Portfolio"},
 {stage:"PROTECT",title:"Protect heat-sensitive journeys",body:"One click runs a prevalidated Phoenix route comparison: A* fastest versus Dijkstra thermal-safe on the real OSM network.",href:"/thermalway",cta:"Run ThermalWay demo"},
 {stage:"EXPLAIN",title:"Use governed local AI",body:"Gemma 4 explains active-cell and portfolio evidence but cannot invent observations, alter optimizer results or bypass review.",href:"/ai",cta:"Open HELIOS AI"},
 {stage:"VERIFY",title:"Trace every claim",body:"Decision Trace and Evidence Inspector expose provider, derived, modeled, optimized and AI-explained states with uncertainty and review boundaries.",href:"/evidence",cta:"Inspect evidence"},
 {stage:"DECIDE",title:"Issue an executive decision brief",body:"Return to Command and generate the Phoenix Heat Action Brief: observed evidence, active-cell counterfactual, portfolio, mobility, AI status, trust and limitations in one decision-ready view.",href:"/",cta:"Return to Command"},
];

export function startJudgeTour(){window.dispatchEvent(new Event("helios:start-tour"))}

export default function JudgeTour(){
 const[open,setOpen]=useState(false),[step,setStep]=useState(0),{activeCellId}=useDecision();
 useEffect(()=>{const start=()=>{const saved=Number(sessionStorage.getItem("helios-tour-step")??0);setStep(Number.isFinite(saved)?Math.min(saved,STEPS.length-1):0);setOpen(true)};window.addEventListener("helios:start-tour",start);return()=>window.removeEventListener("helios:start-tour",start)},[]);
 function go(next:number){const value=Math.max(0,Math.min(STEPS.length-1,next));setStep(value);sessionStorage.setItem("helios-tour-step",String(value))}
 function exit(){setOpen(false);sessionStorage.removeItem("helios-tour-step")}
 if(!open)return null;const x=STEPS[step];
 return <div className="tour-backdrop" role="dialog" aria-modal="true" aria-label="HELIOS judge tour"><aside className="tour-panel"><div className="tour-top"><span>HELIOS CLOSED-LOOP JUDGE TOUR</span><button onClick={exit} aria-label="Exit tour">×</button></div><div className="tour-progress">{STEPS.map((_,i)=><i key={i} className={i<=step?"active":""}/>)}</div><div className="tour-context">ACTIVE DECISION · {activeCellId??"AUTO-SELECTING VERIFIED CELL"}</div><div className="tour-count">STEP {step+1} OF {STEPS.length}</div><strong>{x.stage}</strong><h2>{x.title}</h2><p>{x.body}</p><div className="tour-truth">FortyGuard evidence → deterministic HELIOS engines → governed explanation → human decision</div><div className="tour-actions"><button onClick={()=>go(step-1)} disabled={step===0}>Back</button><Link href={x.href} onClick={()=>sessionStorage.setItem("helios-tour-step",String(step))}>{x.cta}</Link>{step<STEPS.length-1?<button className="primary" onClick={()=>go(step+1)}>Next</button>:<button className="primary" onClick={exit}>Finish</button>}</div></aside></div>
}
