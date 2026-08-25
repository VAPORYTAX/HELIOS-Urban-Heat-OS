"use client";
import {H,rows} from "@/lib/api";import {useLive} from "./useLive";import {PageTitle,Status,Section} from "./UI";
export default function SystemPage(){
 const s=useLive(H.system),c=useLive(H.caps),a=useLive(H.accessibility),j=useLive(H.journeys);const x:any=s.data??{},caps:any=c.data??{};
 const items=[["FastAPI",!!x.service],["PostgreSQL / PostGIS",!!x.database?.ready],["Gemma 4",!!x.intelligence?.reachable],["Truth firewall",x.intelligence?.firewall==="enabled"],["ThermalWay",!!caps.engines?.thermalway],["Portfolio optimizer",!!caps.engines?.portfolio_optimizer],["Governed agents",!!caps.engines?.governed_agents],["Decision science",!!caps.engines?.decision_science]];
 return <div className="page"><PageTitle kicker="EVIDENCE MODE · OPERATIONAL READINESS" title="System Health" description="Live readiness of the services and governed engines that make up HELIOS."/>
 <div className="health-grid">{items.map(([name,ok]:any)=><article key={name}><span>{name}</span><Status ok={ok} label={ok?"READY":"CHECK"}/></article>)}</div>
 <div className="system-grid"><Section title="Runtime contract" eyebrow="LIVE SYSTEM STATUS"><pre className="clean-pre">{JSON.stringify(x,null,2)}</pre></Section><Section title="Operational counts" eyebrow="CURRENT READINESS"><div className="fact-list compact"><div><span>API route objects</span><b>{x.api?.route_count??"—"}</b></div><div><span>Accessibility rows</span><b>{rows(a.data).length}</b></div><div><span>Critical journeys</span><b>{rows(j.data).length}</b></div><div><span>Traveler profiles</span><b>{caps.thermalway?.profiles?.length??"—"}</b></div></div></Section></div></div>
}
