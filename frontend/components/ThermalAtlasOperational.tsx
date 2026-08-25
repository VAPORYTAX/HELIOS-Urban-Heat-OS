"use client";

import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import {
  Layers3, LocateFixed, Map as MapIcon, Maximize2, Minimize2,
  RotateCcw, SlidersHorizontal, ThermometerSun
} from "lucide-react";
import {useEffect,useMemo,useRef,useState} from "react";
import {H} from "@/lib/api";

type MetricKey="current_c"|"hazard_index"|"teu"|"va_teu"|"vulnerability_index"|"confidence";
type Mode="cells"|"heatmap"|"threeD";
type Feature={id?:string;geometry:any;properties:Record<string,any>};

const METRICS:{key:MetricKey;label:string;unit:string;min:number;mid:number;max:number;desc:string}[]=[
 {key:"current_c",label:"Temperature",unit:"°C",min:25,mid:35,max:45,desc:"Latest provider-backed current temperature"},
 {key:"hazard_index",label:"Hazard",unit:"",min:0,mid:.25,max:.6,desc:"Provider operational planning hazard index"},
 {key:"teu",label:"TEU",unit:"",min:0,mid:130,max:260,desc:"Thermal Exposure Units"},
 {key:"va_teu",label:"VA-TEU",unit:"",min:0,mid:140,max:280,desc:"Vulnerability-adjusted thermal exposure"},
 {key:"vulnerability_index",label:"Vulnerability",unit:"",min:0,mid:.5,max:1,desc:"Derived vulnerability index"},
 {key:"confidence",label:"Confidence",unit:"",min:.5,mid:.75,max:1,desc:"Provider / model confidence"},
];

function lerp(a:number,b:number,t:number){return Math.round(a+(b-a)*Math.max(0,Math.min(1,t)))}
function rgb(h:string){return [parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]}
function color(v:number,d:{min:number;mid:number;max:number}){
 const c1=rgb("#4fd6ce"),c2=rgb("#d9ff53"),c3=rgb("#ff5f57");
 let a=c1,b=c2,t=(v-d.min)/(d.mid-d.min);
 if(v>d.mid){a=c2;b=c3;t=(v-d.mid)/(d.max-d.mid)}
 return `rgb(${lerp(a[0],b[0],t)},${lerp(a[1],b[1],t)},${lerp(a[2],b[2],t)})`;
}
function fmt(v:any,u=""){const n=Number(v);return Number.isFinite(n)?`${n.toFixed(Math.abs(n)>=10?2:3)}${u?` ${u}`:""}`:"—"}
function ring(f:Feature):number[][]{return f.geometry?.coordinates?.[0]??[]}
function centroid(coords:number[][]):[number,number]{
 const n=Math.max(1,coords.length-1),p=coords.slice(0,n);
 return [p.reduce((s,x)=>s+x[0],0)/p.length,p.reduce((s,x)=>s+x[1],0)/p.length]
}

export default function ThermalAtlasOperational(){
 const host=useRef<HTMLDivElement|null>(null),shell=useRef<HTMLDivElement|null>(null),mapRef=useRef<maplibregl.Map|null>(null);
 const [features,setFeatures]=useState<Feature[]>([]);
 const [metric,setMetric]=useState<MetricKey>("teu");
 const [mode,setMode]=useState<Mode>("cells");
 const [selected,setSelected]=useState<Feature|null>(null);
 const [projected,setProjected]=useState<any[]>([]);
 const [isFs,setIsFs]=useState(false);
 const [error,setError]=useState("");
 const def=useMemo(()=>METRICS.find(x=>x.key===metric)!,[metric]);

 function reproject(fs=features){
  const map=mapRef.current;if(!map||!fs.length)return;
  const out=fs.map(f=>{
    const pts=ring(f).map(([lng,lat])=>{const p=map.project([lng,lat]);return [p.x,p.y]});
    const cLngLat=centroid(ring(f)),c=map.project(cLngLat);
    return {f,pts,c:[c.x,c.y]};
  });
  setProjected(out);
 }

 useEffect(()=>{
  if(!host.current||mapRef.current)return;
  const map=new maplibregl.Map({
    container:host.current,
    center:[-112.072,33.4505],zoom:14.5,
    style:{version:8,sources:{osm:{type:"raster",tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],tileSize:256,attribution:"© OpenStreetMap contributors"}},layers:[{id:"osm",type:"raster",source:"osm",paint:{"raster-opacity":0.60,"raster-saturation":-0.2}}]} as any,
    attributionControl:false
  });
  mapRef.current=map;
  map.addControl(new maplibregl.NavigationControl(),"top-right");
  map.addControl(new maplibregl.AttributionControl({compact:true}),"bottom-right");

  map.once("load",async()=>{
    try{
      const fc:any=await H.cells();
      const fs:Feature[]=JSON.parse(JSON.stringify(fc.features??[]));
      if(fs.length!==4)throw new Error(`Expected 4 HELIOS cells, received ${fs.length}`);
      setFeatures(fs);
      const all=fs.flatMap(ring);
      const minLng=Math.min(...all.map(p=>p[0])),maxLng=Math.max(...all.map(p=>p[0]));
      const minLat=Math.min(...all.map(p=>p[1])),maxLat=Math.max(...all.map(p=>p[1]));
      map.fitBounds([[minLng,minLat],[maxLng,maxLat]],{padding:80,duration:0,maxZoom:15.3});
      setTimeout(()=>{
        const out=fs.map(f=>{
          const pts=ring(f).map(([lng,lat])=>{const p=map.project([lng,lat]);return [p.x,p.y]});
          const cc=map.project(centroid(ring(f)));
          return {f,pts,c:[cc.x,cc.y]};
        });
        setProjected(out);
      },60);
    }catch(e:any){setError(e.message)}
  });
  const redraw=()=>setTimeout(()=>reproject(),0);
  map.on("move",redraw);map.on("zoom",redraw);map.on("resize",redraw);
  return()=>{map.remove();mapRef.current=null}
 },[]);

 useEffect(()=>{reproject()},[features]);

 useEffect(()=>{
  const h=()=>{setIsFs(Boolean(document.fullscreenElement));setTimeout(()=>{mapRef.current?.resize();reproject()},120)};
  document.addEventListener("fullscreenchange",h);return()=>document.removeEventListener("fullscreenchange",h)
 },[features]);

 async function fullscreen(){if(!shell.current)return;document.fullscreenElement?await document.exitFullscreen():await shell.current.requestFullscreen()}
 function fit(){
  const map=mapRef.current;if(!map||!features.length)return;
  const all=features.flatMap(ring);
  map.fitBounds([[Math.min(...all.map(p=>p[0])),Math.min(...all.map(p=>p[1]))],[Math.max(...all.map(p=>p[0])),Math.max(...all.map(p=>p[1]))]],{padding:80,duration:450,maxZoom:15.3})
 }
 function reset(){setMetric("teu");setMode("cells");setSelected(null);fit()}
 const normalize=(v:number)=>Math.max(0,Math.min(1,(v-def.min)/(def.max-def.min)));

 return <div className="atlas-operational" ref={shell}>
  <div className="atlas-topline"><div><div className="eyebrow">PLANNING MODE · SPATIAL INTELLIGENCE</div><h1>Thermal Atlas</h1><p>Provider-backed urban heat intelligence over OpenStreetMap.</p></div>
   <div className="atlas-health"><span className="live"><i/>LIVE DATA</span><span>{features.length} HELIOS CELLS</span><span>SVG GEO OVERLAY · READY</span></div></div>
  <div className="atlas-stage">
   <div className="atlas-toolbar">
    <div className="tool-group"><span className="tool-label"><SlidersHorizontal size={13}/>Metric</span>{METRICS.map(x=><button key={x.key} className={metric===x.key?"active":""} onClick={()=>setMetric(x.key)}>{x.label}</button>)}</div>
    <div className="tool-group view"><span className="tool-label"><Layers3 size={13}/>View</span>
      <button className={mode==="cells"?"active":""} onClick={()=>setMode("cells")}><MapIcon size={13}/>Cells</button>
      <button className={mode==="heatmap"?"active":""} onClick={()=>setMode("heatmap")}><ThermometerSun size={13}/>Heatmap</button>
      <button className={mode==="threeD"?"active":""} onClick={()=>setMode("threeD")}><Layers3 size={13}/>3D</button>
      <button onClick={fit}><LocateFixed size={13}/>Fit</button><button onClick={reset}><RotateCcw size={13}/>Reset</button>
      <button className="fullscreen-btn" onClick={fullscreen}>{isFs?<Minimize2 size={13}/>:<Maximize2 size={13}/>} {isFs?"Exit":"Full screen"}</button>
    </div>
   </div>
   <div className="atlas-map-wrap">
    <div ref={host} className="atlas-map-full"/>
    <svg className="helios-svg-overlay">
      <defs>
        <filter id="heatBlur"><feGaussianBlur stdDeviation="34"/></filter>
      </defs>
      {mode==="heatmap"&&projected.map(({f,c},i)=>{
        const v=Number(f.properties[metric]),norm=normalize(v),r=115+norm*105;
        return <circle key={i} cx={c[0]} cy={c[1]} r={r} fill={color(v,def)} opacity={0.30+norm*.28} filter="url(#heatBlur)"/>
      })}
      {mode==="cells"&&projected.map(({f,pts},i)=>{
        const v=Number(f.properties[metric]),points=pts.map((p:number[])=>p.join(",")).join(" ");
        return <g key={i} className="geo-cell" onClick={()=>setSelected(f)}>
          <polygon points={points} fill={color(v,def)} fillOpacity=".78" stroke="#07100c" strokeWidth="7"/>
          <polygon points={points} fill="none" stroke="#edff92" strokeWidth="2.5"/>
        </g>
      })}
      {mode==="threeD"&&projected.map(({f,pts,c},i)=>{
        const v=Number(f.properties[metric]),norm=normalize(v),h=30+norm*115;
        const top=pts.map((p:number[])=>[p[0],p[1]-h]);
        const basePts=pts.map((p:number[])=>p.join(",")).join(" "),topPts=top.map((p:number[])=>p.join(",")).join(" ");
        const sides=pts.slice(0,-1).map((p:number[],j:number)=>{
          const q=pts[j+1],tp=top[j],tq=top[j+1];
          return `${p[0]},${p[1]} ${q[0]},${q[1]} ${tq[0]},${tq[1]} ${tp[0]},${tp[1]}`;
        });
        return <g key={i} className="geo-cell" onClick={()=>setSelected(f)}>
          <polygon points={basePts} fill="#07100c" fillOpacity=".32"/>
          {sides.map((s:string,j:number)=><polygon key={j} points={s} fill={color(v,def)} fillOpacity=".55" stroke="#07100c" strokeWidth="2"/>)}
          <polygon points={topPts} fill={color(v,def)} fillOpacity=".92" stroke="#edff92" strokeWidth="3"/>
          <text x={c[0]} y={c[1]-h-8} textAnchor="middle" className="svg-cell-label">{f.properties.cell_id}</text>
        </g>
      })}
    </svg>
    <div className="legend"><div><span>{def.label}</span><b>{def.desc}</b></div><div className="legend-bar"/><div className="legend-scale"><span>{def.min}{def.unit}</span><span>{def.mid}{def.unit}</span><span>{def.max}{def.unit}</span></div><div className="legend-mode">{mode==="cells"?"GEOGRAPHIC CELL CHOROPLETH":mode==="heatmap"?"THERMAL INTENSITY SURFACE":"2.5D BURDEN · HEIGHT = METRIC"}</div></div>
    <aside className="atlas-inspector"><div className="eyebrow">CELL INSPECTOR</div><h2>{selected?.properties.cell_id??"Select a HELIOS cell"}</h2>{selected?<><div className="inspector-primary"><span>{def.label}</span><b>{fmt(selected.properties[metric],def.unit)}</b></div><div className="inspector-grid">{METRICS.map(x=><div key={x.key}><span>{x.label}</span><b>{fmt(selected.properties[x.key],x.unit)}</b></div>)}</div><div className="truth-block"><span>TRUTH CATEGORY</span><b>{selected.properties.truth_category}</b></div></>:<p>Click a colored HELIOS cell in Cells or 3D view.</p>}</aside>
    {error&&<div className="atlas-error">{error}</div>}
   </div>
  </div>
 </div>
}
