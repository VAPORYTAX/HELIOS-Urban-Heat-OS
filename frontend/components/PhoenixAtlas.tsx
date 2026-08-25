"use client";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import {Layers3,LocateFixed,Map as MapIcon,Maximize2,Minimize2,RotateCcw,ThermometerSun} from "lucide-react";
import Link from "next/link";
import {useEffect,useMemo,useRef,useState} from "react";
import {E} from "@/lib/domain";
import {useDecision} from "./DecisionContext";

type Metric="current_c"|"hazard_index"|"teu"|"va_teu"|"vulnerability_index"|"confidence";
type Mode="coverage"|"cells"|"heatmap"|"threeD";
type F={id?:string;geometry:any;properties:Record<string,any>};
const M:{key:Metric;label:string;unit:string;min:number;mid:number;max:number;desc:string}[]=[
 {key:"current_c",label:"Temperature",unit:"°C",min:25,mid:35,max:45,desc:"Latest provider-backed temperature"},
 {key:"hazard_index",label:"Hazard",unit:"",min:0,mid:.25,max:.6,desc:"Provider operational planning hazard"},
 {key:"teu",label:"TEU",unit:"",min:0,mid:130,max:260,desc:"Thermal Exposure Units"},
 {key:"va_teu",label:"VA-TEU",unit:"",min:0,mid:140,max:280,desc:"Vulnerability-adjusted exposure"},
 {key:"vulnerability_index",label:"Vulnerability",unit:"",min:0,mid:.5,max:1,desc:"Derived vulnerability index"},
 {key:"confidence",label:"Confidence",unit:"",min:.5,mid:.75,max:1,desc:"Provider/model confidence"}
];
const PHX:[number,number,number,number]=[-112.324,33.290,-111.925,33.920];
function rgb(h:string){return [parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]}
function lerp(a:number,b:number,t:number){return Math.round(a+(b-a)*Math.max(0,Math.min(1,t)))}
function c(v:number,d:any){let a=rgb("#4fd6ce"),b=rgb("#d9ff53"),t=(v-d.min)/(d.mid-d.min);if(v>d.mid){a=rgb("#d9ff53");b=rgb("#ff5f57");t=(v-d.mid)/(d.max-d.mid)}return `rgb(${lerp(a[0],b[0],t)},${lerp(a[1],b[1],t)},${lerp(a[2],b[2],t)})`}
function ring(f:F):number[][]{return f.geometry?.coordinates?.[0]??[]}
function ctr(r:number[][]):[number,number]{const p=r.slice(0,-1);return[p.reduce((s,x)=>s+x[0],0)/p.length,p.reduce((s,x)=>s+x[1],0)/p.length]}
function fnum(v:any,u=""){const x=Number(v);return Number.isFinite(x)?`${x.toFixed(Math.abs(x)>=10?2:3)}${u?` ${u}`:""}`:"—"}

export default function Atlas(){
 const host=useRef<HTMLDivElement|null>(null),wrap=useRef<HTMLDivElement|null>(null),mapRef=useRef<maplibregl.Map|null>(null);
 const {activeCellId,setActiveCellId}=useDecision();
 const [fs,setFs]=useState<F[]>([]),[proj,setProj]=useState<any[]>([]),[metric,setMetric]=useState<Metric>("teu"),[mode,setMode]=useState<Mode>("cells"),[sel,setSel]=useState<F|null>(null),[full,setFull]=useState(false),[error,setError]=useState<string|null>(null);
 const def=useMemo(()=>M.find(x=>x.key===metric)!,[metric]);
 function choose(f:F){setSel(f);const id=String(f.properties.cell_id??"");if(id)setActiveCellId(id)}
 function project(features=fs){const m=mapRef.current;if(!m||!features.length)return;setProj(features.map(f=>{const pts=ring(f).map(([x,y])=>{const p=m.project([x,y]);return[p.x,p.y]});const q=m.project(ctr(ring(f)));return{f,pts,q:[q.x,q.y]}}))}
 useEffect(()=>{if(!host.current)return;const map=new maplibregl.Map({container:host.current,center:[-112.074,33.448],zoom:10.4,style:{version:8,sources:{osm:{type:"raster",tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],tileSize:256,attribution:"© OpenStreetMap contributors"}},layers:[{id:"osm",type:"raster",source:"osm",paint:{"raster-opacity":.62,"raster-saturation":-.22}}]} as any,attributionControl:false});mapRef.current=map;map.addControl(new maplibregl.NavigationControl(),"top-right");map.addControl(new maplibregl.AttributionControl({compact:true}),"bottom-right");
  map.once("load",async()=>{try{const fc:any=await E.cells();const a:F[]=JSON.parse(JSON.stringify(fc.features??[]));if(!a.length)throw new Error("No verified spatial cells returned");setFs(a);const pts=a.flatMap(ring);map.fitBounds([[Math.min(...pts.map(p=>p[0])),Math.min(...pts.map(p=>p[1]))],[Math.max(...pts.map(p=>p[0])),Math.max(...pts.map(p=>p[1]))]],{padding:90,duration:0,maxZoom:15.2});setTimeout(()=>project(a),80)}catch(e:any){setError(e.message)}});
  const h=()=>project();map.on("move",h);map.on("zoom",h);map.on("resize",h);return()=>map.remove()
 },[]);
 useEffect(()=>project(),[fs]);
 useEffect(()=>{if(!activeCellId||!fs.length)return;const f=fs.find(x=>String(x.properties.cell_id)===activeCellId);if(f)setSel(f)},[activeCellId,fs]);
 useEffect(()=>{const h=()=>{setFull(!!document.fullscreenElement);setTimeout(()=>{mapRef.current?.resize();project()},120)};document.addEventListener("fullscreenchange",h);return()=>document.removeEventListener("fullscreenchange",h)},[fs]);
 function cityView(){mapRef.current?.fitBounds([[PHX[0],PHX[1]],[PHX[2],PHX[3]]],{padding:55,duration:450})}
 function liveView(){if(!fs.length)return;const a=fs.flatMap(ring);mapRef.current?.fitBounds([[Math.min(...a.map(p=>p[0])),Math.min(...a.map(p=>p[1]))],[Math.max(...a.map(p=>p[0])),Math.max(...a.map(p=>p[1]))]],{padding:90,duration:450,maxZoom:15.2})}
 async function toggle(){if(!wrap.current)return;document.fullscreenElement?await document.exitFullscreen():await wrap.current.requestFullscreen()}
 const norm=(v:number)=>Math.max(0,Math.min(1,(v-def.min)/(def.max-def.min)));
 return <div className="atlas-operational" ref={wrap}>
  <div className="atlas-topline"><div><div className="eyebrow">OBSERVE + DIAGNOSE · PHOENIX SPATIAL INTELLIGENCE</div><h1>See the city. Trust only what is observed.</h1><p>Four cells observed. The rest intentionally unknown. Click a verified cell to carry it through the complete HELIOS decision loop.</p></div><div className="atlas-health"><span className={fs.length===4?"live":"warn"}><i/>{fs.length===4?"LIVE PROVIDER DATA":"DATA CHECK"}</span><span>{fs.length||"—"} VERIFIED CELLS</span><span>PHX-DOWNTOWN ONLY</span></div></div>
  <div className="atlas-stage"><div className="atlas-toolbar">
   <div className="tool-group">{M.map(x=><button key={x.key} className={metric===x.key?"active":""} onClick={()=>setMetric(x.key)}>{x.label}</button>)}</div>
   <div className="tool-group view"><button className={mode==="coverage"?"active":""} onClick={()=>setMode("coverage")}><LocateFixed size={13}/>Coverage</button><button className={mode==="cells"?"active":""} onClick={()=>setMode("cells")}><MapIcon size={13}/>Cells</button><button className={mode==="heatmap"?"active":""} onClick={()=>setMode("heatmap")}><ThermometerSun size={13}/>Heatmap</button><button className={mode==="threeD"?"active":""} onClick={()=>setMode("threeD")}><Layers3 size={13}/>3D</button><button onClick={cityView}>Phoenix</button><button onClick={liveView}>Live AOI</button><button onClick={()=>{setMetric("teu");setMode("coverage");setSel(null);cityView()}}><RotateCcw size={13}/>Reset</button><button className="fullscreen-btn" onClick={toggle}>{full?<Minimize2 size={13}/>:<Maximize2 size={13}/>} Full screen</button></div>
  </div>
  <div className="atlas-map-wrap"><div ref={host} className="atlas-map-full"/>{error&&<div className="atlas-error">Backend unavailable: {error}. Reload to retry.</div>}
   <div className="phoenix-overlay-note"><b>CITYWIDE CONTEXT</b><span>Phoenix OSM · unobserved areas neutral</span><i>LIVE PROVIDER-COVERED AOI: 4 downtown cells</i></div>
   <svg className="helios-svg-overlay">
    <defs><filter id="hb"><feGaussianBlur stdDeviation="34"/></filter></defs>
    {mode==="coverage"&&proj.map(({pts,f},i)=><g key={i} className={`geo-cell ${String(f.properties.cell_id)===activeCellId?"active":""}`} onClick={()=>choose(f)}><polygon points={pts.map((p:number[])=>p.join(",")).join(" ")} fill="#d9ff53" fillOpacity=".31" stroke="#d9ff53" strokeWidth={String(f.properties.cell_id)===activeCellId?7:4} strokeDasharray="12 8"/></g>)}
    {mode==="cells"&&proj.map(({pts,f},i)=>{const v=Number(f.properties[metric]);return <g key={i} className={`geo-cell ${String(f.properties.cell_id)===activeCellId?"active":""}`} onClick={()=>choose(f)}><polygon points={pts.map((p:number[])=>p.join(",")).join(" ")} fill={c(v,def)} fillOpacity=".80" stroke={String(f.properties.cell_id)===activeCellId?"#ffffff":"#07100c"} strokeWidth={String(f.properties.cell_id)===activeCellId?9:7}/><polygon points={pts.map((p:number[])=>p.join(",")).join(" ")} fill="none" stroke="#efff9b" strokeWidth="2.5"/></g>})}
    {mode==="heatmap"&&proj.map(({q,f},i)=>{const v=Number(f.properties[metric]),z=norm(v);return <circle key={i} cx={q[0]} cy={q[1]} r={115+z*110} fill={c(v,def)} opacity={.28+z*.3} filter="url(#hb)"/>})}
    {mode==="threeD"&&proj.map(({pts,q,f},i)=>{const v=Number(f.properties[metric]),h=35+norm(v)*120,top=pts.map((p:number[])=>[p[0],p[1]-h]);return <g key={i} className={`geo-cell ${String(f.properties.cell_id)===activeCellId?"active":""}`} onClick={()=>choose(f)}>{pts.slice(0,-1).map((p:number[],j:number)=>{const q2=pts[j+1],a=top[j],b=top[j+1];return <polygon key={j} points={`${p[0]},${p[1]} ${q2[0]},${q2[1]} ${b[0]},${b[1]} ${a[0]},${a[1]}`} fill={c(v,def)} fillOpacity=".58" stroke="#07100c" strokeWidth="2"/>})}<polygon points={top.map((p:number[])=>p.join(",")).join(" ")} fill={c(v,def)} fillOpacity=".94" stroke={String(f.properties.cell_id)===activeCellId?"#ffffff":"#efff9b"} strokeWidth="3"/><text x={q[0]} y={q[1]-h-8} textAnchor="middle" className="svg-cell-label">{f.properties.cell_id}</text></g>})}
   </svg>
   <div className="coverage-card"><div className="eyebrow">COVERAGE CONTRACT</div><h3>{mode==="coverage"?"Live provider footprint":"Verified live AOI"}</h3><div className="coverage-keys"><span><i className="observed"/>Observed by provider</span><span><i className="derived"/>Derived burden</span><span><i className="context"/>Citywide context / unobserved</span></div><p>Only highlighted downtown cells carry current provider-backed operational metrics. Unobserved Phoenix is never assigned fabricated values.</p><button onClick={liveView}>Zoom to live AOI</button></div>
   <div className="legend"><div><span>{def.label}</span><b>{def.desc}</b></div><div className="legend-bar"/><div className="legend-scale"><span>{def.min}{def.unit}</span><span>{def.mid}{def.unit}</span><span>{def.max}{def.unit}</span></div><div className="legend-mode">{mode==="coverage"?"PROVIDER COVERAGE":mode==="cells"?"VERIFIED CELL CHOROPLETH":mode==="heatmap"?"LIVE-AOI INTENSITY SURFACE":"2.5D LIVE-AOI BURDEN"}</div></div>
   <aside className="atlas-inspector"><div className="eyebrow">DECISION CELL INSPECTOR</div><h2>{sel?.properties.cell_id??"Live AOI"}</h2>{sel?<><div className="inspector-primary"><span>{def.label}</span><b>{fnum(sel.properties[metric],def.unit)}</b></div><div className="inspector-grid">{M.map(x=><div key={x.key}><span>{x.label}</span><b>{fnum(sel.properties[x.key],x.unit)}</b></div>)}</div><div className="truth-block"><span>Truth category</span><b>{sel.properties.truth_category}</b><p>Observed/derived provider-operational metrics. No citywide interpolation.</p></div><div className="atlas-actions"><button onClick={()=>choose(sel)}>Make active decision</button><Link href="/interventions">Intervene + simulate →</Link><Link href="/investment">See portfolio →</Link><Link href="/evidence">Verify lineage →</Link></div></>:<p>Click one of the four verified cells. Phoenix outside this footprint is not currently observed.</p>}</aside>
  </div></div>
 </div>
}
