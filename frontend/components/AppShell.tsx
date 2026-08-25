"use client";
import Link from "next/link";
import {usePathname} from "next/navigation";
import {useEffect,useState} from "react";
import {Activity,BrainCircuit,CircleDollarSign,Database,Home,Layers3,Route,ShieldCheck,ThermometerSun} from "lucide-react";
import {E} from "@/lib/domain";
import {readRuntimeState,type HeliosRuntimeState} from "@/lib/runtime";
import {useLive} from "./useLive";
import JudgeTour from "./JudgeTour";
import ExecutiveBrief from "./ExecutiveBrief";
import {useDecision} from "./DecisionContext";

const NAV=[
  ["/","Command","Command",Home],
  ["/atlas","Observe + Diagnose","Thermal Atlas",ThermometerSun],
  ["/interventions","Intervene + Simulate","Interventions",Layers3],
  ["/investment","Optimize","Portfolio",CircleDollarSign],
  ["/thermalway","Protect","ThermalWay",Route],
  ["/ai","Explain","HELIOS AI",BrainCircuit],
  ["/evidence","Verify","Evidence",ShieldCheck],
  ["/system","Readiness","System",Database],
] as const;

export default function AppShell({children}:{children:React.ReactNode}){
  const path=usePathname();
  const runtime=useLive(E.system);
  const {activeCellId}=useDecision();
  const [source,setSource]=useState<HeliosRuntimeState>({mode:"checking"});
  useEffect(()=>{setSource(readRuntimeState());const h=(e:Event)=>setSource((e as CustomEvent<HeliosRuntimeState>).detail);window.addEventListener("helios:runtime-state",h);return()=>window.removeEventListener("helios:runtime-state",h)},[]);
  const backendReady=!runtime.loading&&!runtime.error&&!!(runtime.data as any)?.database?.ready;
  const mode=source.mode==="snapshot"?"VERIFIED SNAPSHOT":source.mode==="offline"?"BACKEND UNAVAILABLE":runtime.loading?"CHECKING BACKEND":backendReady?"LIVE BACKEND":"BACKEND UNAVAILABLE";
  const modeClass=source.mode==="snapshot"?"snapshot":backendReady?"":"offline";
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark"><Activity size={19}/></div>
        <div><b>HELIOS</b><span>Urban Heat Intervention OS</span></div>
      </div>
      <nav>{NAV.map(([href,stage,label,Icon])=>
        <Link key={href} href={href} className={path===href?"nav active":"nav"}>
          <Icon size={17}/><div><span>{label}</span><small>{stage}</small></div>
        </Link>)}
      </nav>
      <div className="side-foot">
        <div><ShieldCheck size={15}/><b>Truth firewall active</b></div>
        <p>Provider, derived, modeled, optimized and AI-explained outputs remain explicitly separated.</p>
        <small>OBSERVE → DIAGNOSE → INTERVENE → SIMULATE → OPTIMIZE → PROTECT → EXPLAIN → VERIFY</small>
      </div>
    </aside>
    <section className="main">
      <header className="topbar">
        <div className="context"><span>PHX-DOWNTOWN</span><b>Decision Environment</b><em>ACTIVE DECISION · {activeCellId??"AUTO-SELECTING"}</em></div>
        <div className="top-status"><span className={modeClass}><i/> {mode}{source.mode==="snapshot"&&source.snapshotAt?<small> · {new Date(source.snapshotAt).toLocaleString()}</small>:null}</span><span>TRUTH FIREWALL</span><span>HUMAN REVIEW GATE</span><ExecutiveBrief/></div>
      </header>
      {source.mode==="snapshot"&&<div className="snapshot-banner"><b>VERIFIED SNAPSHOT — LIVE COMPUTE UNAVAILABLE</b><span>Read-only last-validated evidence is being shown. New AI queries, route calculations and fresh optimization are not represented as live.</span></div>}
      {children}
      <JudgeTour/>
    </section>
  </div>
}
