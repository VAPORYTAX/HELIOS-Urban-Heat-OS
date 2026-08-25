"use client";
import Link from "next/link";
import {Bar,BarChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis} from "recharts";
import {H,rows,num,latest,fmt,money,str} from "@/lib/api";
import {useLive} from "./useLive";
import {Metric,Section} from "./UI";

export default function CommandPage(){
 const provider=useLive(H.provider), optimizer=useLive(H.optimizer), system=useLive(H.system);
 const pr=rows(provider.data), opt=latest(optimizer.data), sys:any=system.data??{};
 const totalTeu=pr.reduce((s,r)=>s+(num(r,"teu")??0),0);
 const totalVa=pr.reduce((s,r)=>s+(num(r,"va_teu","vulnerable_teu")??0),0);
 const burden=pr.map(r=>({cell:str(r,"cell_id","id"),TEU:num(r,"teu")??0,"VA-TEU":num(r,"va_teu","vulnerable_teu")??0})).sort((a,b)=>b["VA-TEU"]-a["VA-TEU"]);
 return <div className="page">
  <section className="command-hero">
   <div><div className="eyebrow">HYPERLOCAL ENVIRONMENTAL INTELLIGENCE</div><h1>Don’t map the heat.<br/><em>Rewrite it.</em></h1>
   <p>HELIOS turns provider-backed heat observations into exposure intelligence, cooling interventions, optimized investment portfolios, climate-safe mobility and governed local AI.</p>
   <div className="cta"><Link href="/atlas">Explore Thermal Atlas</Link><Link className="secondary" href="/investment">Open Investment Intelligence</Link></div></div>
   <div className="decision-orb"><span>DECISION LOOP</span><b>OBSERVE</b><i>→</i><b>DIAGNOSE</b><i>→</i><b>ACT</b></div>
  </section>
  <section className="metrics five">
   <Metric label="Operational cells" value={pr.length?String(pr.length):"—"} sub="provider-backed"/>
   <Metric label="Total TEU" value={pr.length?fmt(totalTeu):"—"} sub="planning exposure"/>
   <Metric label="VA-TEU" value={pr.length?fmt(totalVa):"—"} sub="vulnerability-adjusted"/>
   <Metric label="Selected portfolio" value={money(num(opt,"total_cost","cost"))} sub={`of ${money(num(opt,"budget","budget_limit"))}`}/>
   <Metric label="Gemma 4" value={sys?.intelligence?.reachable?"LIVE":"—"} sub="native FAST · firewall"/>
  </section>
  <section className="command-grid">
   <Section title="Where burden concentrates" eyebrow="PROVIDER OPERATIONAL BURDEN">
    {burden.length?<div className="chart-wrap"><ResponsiveContainer width="100%" height={280}><BarChart data={burden}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="cell"/><YAxis/><Tooltip/><Bar dataKey="TEU" fill="var(--cyan)"/><Bar dataKey="VA-TEU" fill="var(--acid)"/></BarChart></ResponsiveContainer></div>:<p className="muted">Waiting for provider metrics.</p>}
   </Section>
   <Section title="Decision posture" eyebrow="EXECUTIVE INTERPRETATION">
    <div className="decision-card">
      <span>CURRENT STATE</span>
      <b>{pr.length?"Planning & preparedness":"Awaiting live data"}</b>
      <p>HELIOS keeps hazard, exposure, vulnerability and modeled intervention effects separate. Human review remains required before operational deployment.</p>
    </div>
    <div className="mini-grid">
      <Link href="/interventions"><b>Design</b><span>Generate and inspect cooling actions →</span></Link>
      <Link href="/thermalway"><b>Protect movement</b><span>Compare thermal-safe routes →</span></Link>
      <Link href="/evidence"><b>Prove it</b><span>Inspect evidence and uncertainty →</span></Link>
    </div>
   </Section>
  </section>
 </div>
}
