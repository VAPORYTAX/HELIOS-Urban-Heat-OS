"use client";
import {H,rows,str} from "@/lib/api";import {useLive} from "./useLive";import {PageTitle,Section} from "./UI";
const STAGES=[["FortyGuard","PROVIDER"],["Provider metrics","DERIVED"],["Exposure","DERIVED"],["Counterfactuals","MODELED"],["Optimizer","OPTIMIZED"],["Agent decision","GOVERNED"],["Gemma explanation","LLM EXPLAINED"]];
export default function EvidencePage(){
 const q=useLive(H.quality),p=useLive(H.packets);const packets=rows(p.data);
 return <div className="page"><PageTitle kicker="EVIDENCE MODE · PROVENANCE · UNCERTAINTY" title="Evidence Inspector" description="HELIOS makes it visible which claims are provider observations, derived metrics, modeled assumptions, optimization outputs or LLM explanations."/>
 <Section title="Decision provenance chain" eyebrow="FROM OBSERVATION TO EXPLANATION"><div className="pipeline">{STAGES.map(([name,type],i)=><div key={name} className="pipe-stage"><span>{type}</span><b>{name}</b>{i<STAGES.length-1&&<i>→</i>}</div>)}</div></Section>
 <div className="evidence-grid"><Section title="Current quality state" eyebrow="QUALITY SNAPSHOT"><pre className="clean-pre">{JSON.stringify(q.data??{},null,2)}</pre></Section><Section title="Context packets" eyebrow="EVIDENCE PACKETS"><div className="packet-list">{packets.length?packets.slice(0,8).map((x,i)=><div key={i}><b>{str(x,"id","packet_id")}</b><span>{str(x,"created_at","status","area_id")}</span></div>):<span className="muted">No packets returned.</span>}</div></Section></div></div>
}
