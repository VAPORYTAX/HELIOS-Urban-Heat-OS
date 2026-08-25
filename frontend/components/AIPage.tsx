"use client";
import {useState} from "react";import {H} from "@/lib/api";import {PageTitle,Section} from "./UI";import {BrainCircuit,ShieldCheck} from "lucide-react";
export default function AIPage(){
 const [q,setQ]=useState("Assess the current intervention portfolio for phx-downtown. What should a decision-maker prioritize and why?");
 const [a,setA]=useState<any>(null),[busy,setBusy]=useState(false);
 async function ask(){setBusy(true);setA(null);try{setA(await H.ask(q))}catch(e:any){setA({error:e.message})}finally{setBusy(false)}}
 const answer=a?.answer??a?.response_json??a;
 return <div className="page"><PageTitle kicker="COMMAND MODE · GOVERNED LOCAL INTELLIGENCE" title="HELIOS AI" description="Gemma 4 explains evidence from HELIOS; it does not replace numerical, spatial or optimization engines." aside={<BrainCircuit size={34}/>}/>
 <div className="ai-layout"><section className="ai-work"><div className="ai-policy"><ShieldCheck size={14}/> Native FAST · reasoning off · semantic firewall · human review</div><textarea value={q} onChange={e=>setQ(e.target.value)}/><button onClick={ask} disabled={busy||!q.trim()}>{busy?"HELIOS is working…":"Ask HELIOS"}</button>
 {answer&&<div className="answer">{answer.error?<div className="errorbox">{answer.error}</div>:<><div className="eyebrow">ASSESSMENT</div><h2>{answer.headline??"HELIOS decision response"}</h2><p>{answer.summary??""}</p>
 {Array.isArray(answer.recommended_actions)&&<div className="action-list">{answer.recommended_actions.map((x:any,i:number)=><div key={i}><b>{x.cell_id??x.action??`Action ${i+1}`}</b><span>{x.reason??x.rationale??""}</span></div>)}</div>}
 {Array.isArray(answer.uncertainties)&&<Section title="Uncertainties" eyebrow="REVIEW BEFORE ACTION"><ul>{answer.uncertainties.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul></Section>}
 <details className="technical"><summary>View technical response</summary><pre>{JSON.stringify(a,null,2)}</pre></details></>}</div>}</section>
 <aside className="ai-side"><Section title="Governance" eyebrow="INFERENCE CONTRACT"><div className="fact-list compact"><div><span>Model</span><b>Gemma 4 12B QAT</b></div><div><span>Transport</span><b>LM Studio native FAST</b></div><div><span>Reasoning</span><b>OFF</b></div><div><span>Fallback</span><b>{a?.fallback_used===false?"FALSE":a?"Check response":"—"}</b></div><div><span>Human review</span><b>REQUIRED</b></div></div></Section></aside></div></div>
}
