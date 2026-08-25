"use client";
import {AlertTriangle,CheckCircle2} from "lucide-react";
export function PageTitle({kicker,title,description,aside}:{kicker:string,title:string,description:string,aside?:React.ReactNode}){
 return <div className="page-title"><div><div className="eyebrow">{kicker}</div><h1>{title}</h1><p>{description}</p></div>{aside}</div>
}
export function Metric({label,value,sub,accent=false}:{label:string,value:string,sub?:string,accent?:boolean}){
 return <article className={"metric "+(accent?"accent":"")}><span>{label}</span><b>{value}</b>{sub&&<small>{sub}</small>}</article>
}
export function Status({ok,label}:{ok:boolean,label:string}){return <span className={"status "+(ok?"ok":"bad")}>{ok?<CheckCircle2 size={13}/>:<AlertTriangle size={13}/>} {label}</span>}
export function Empty({children}:{children:React.ReactNode}){return <div className="empty">{children}</div>}
export function Section({title,eyebrow,children,className=""}:{title:string,eyebrow?:string,children:React.ReactNode,className?:string}){
 return <section className={"panel "+className}>{eyebrow&&<div className="eyebrow">{eyebrow}</div>}<h2>{title}</h2>{children}</section>
}
