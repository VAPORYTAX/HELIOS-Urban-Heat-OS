"use client";
import Link from "next/link";
import {useEffect,useState} from "react";

const STEPS=[
 {stage:"OBSERVE",title:"Start with verified evidence",body:"Four provider-verified downtown Phoenix cells establish the live thermal evidence footprint.",href:"/atlas",cta:"Open Thermal Atlas"},
 {stage:"DIAGNOSE",title:"Quantify who carries the burden",body:"HELIOS converts thermal observations into TEU and vulnerability-adjusted burden.",href:"/atlas",cta:"Inspect live burden"},
 {stage:"ACT",title:"Move from hotspot to action",body:"The system generates provider-native cooling intervention candidates with explicit modeled assumptions.",href:"/interventions",cta:"See interventions"},
 {stage:"OPTIMIZE",title:"Make the budget decision",body:"Under a real budget, CP-SAT selects the strongest modeled intervention portfolio.",href:"/investment",cta:"Open Portfolio"},
 {stage:"PROTECT",title:"Protect heat-sensitive journeys",body:"ThermalWay compares fastest travel with thermal-exposure-aware routing on the real OSM network.",href:"/thermalway",cta:"Compare routes"},
 {stage:"EXPLAIN",title:"Use governed local AI",body:"Gemma 4 explains the evidence but cannot alter deterministic HELIOS outputs.",href:"/ai",cta:"Open HELIOS AI"},
 {stage:"VERIFY",title:"Trust every claim",body:"Every output remains labeled by provenance, confidence, truth category and review requirement.",href:"/evidence",cta:"Inspect evidence"},
];

export function startJudgeTour(){window.dispatchEvent(new Event("helios:start-tour"))}

export default function JudgeTour(){
 const[open,setOpen]=useState(false),[step,setStep]=useState(0);
 useEffect(()=>{const start=()=>{const saved=Number(sessionStorage.getItem("helios-tour-step")??0);setStep(Number.isFinite(saved)?Math.min(saved,STEPS.length-1):0);setOpen(true)};window.addEventListener("helios:start-tour",start);return()=>window.removeEventListener("helios:start-tour",start)},[]);
 function go(next:number){const value=Math.max(0,Math.min(STEPS.length-1,next));setStep(value);sessionStorage.setItem("helios-tour-step",String(value))}
 function exit(){setOpen(false);sessionStorage.removeItem("helios-tour-step")}
 if(!open)return null;const x=STEPS[step];
 return <div className="tour-backdrop" role="dialog" aria-modal="true" aria-label="HELIOS judge tour"><aside className="tour-panel"><div className="tour-top"><span>90-SECOND JUDGE TOUR</span><button onClick={exit} aria-label="Exit tour">×</button></div><div className="tour-progress">{STEPS.map((_,i)=><i key={i} className={i<=step?"active":""}/>)}</div><div className="tour-count">STEP {step+1} OF {STEPS.length}</div><strong>{x.stage}</strong><h2>{x.title}</h2><p>{x.body}</p><div className="tour-truth">Provider evidence → deterministic engines → governed explanation</div><div className="tour-actions"><button onClick={()=>go(step-1)} disabled={step===0}>Back</button><Link href={x.href} onClick={()=>sessionStorage.setItem("helios-tour-step",String(step))}>{x.cta}</Link>{step<STEPS.length-1?<button className="primary" onClick={()=>go(step+1)}>Next</button>:<button className="primary" onClick={exit}>Finish</button>}</div></aside></div>
}
