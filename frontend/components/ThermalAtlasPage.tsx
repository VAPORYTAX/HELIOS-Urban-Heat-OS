"use client";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import {useEffect,useRef,useState} from "react";
import {H} from "@/lib/api";
import {PageTitle} from "./UI";

const LAYERS=[
 ["current_c","Temperature","°C"],
 ["hazard_index","Hazard",""],
 ["teu","TEU",""],
 ["va_teu","VA-TEU",""],
 ["vulnerability_index","Vulnerability",""],
 ["confidence","Confidence",""],
] as const;

export default function ThermalAtlasPage(){
 const host=useRef<HTMLDivElement|null>(null), mapRef=useRef<maplibregl.Map|null>(null);
 const [metric,setMetric]=useState("teu"),[selected,setSelected]=useState<any>(null),[error,setError]=useState("");
 useEffect(()=>{
  if(!host.current||mapRef.current)return;
  const style:any={version:8,sources:{osm:{type:"raster",tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],tileSize:256,attribution:"© OpenStreetMap contributors"}},layers:[{id:"osm",type:"raster",source:"osm"}]};
  const map=new maplibregl.Map({container:host.current,style,center:[-112.0718,33.4505],zoom:14,attributionControl:false});
  mapRef.current=map;map.addControl(new maplibregl.NavigationControl(),"top-right");map.addControl(new maplibregl.AttributionControl({compact:true}),"bottom-right");
  map.once("load",async()=>{try{
    const fc:any=await H.cells();
    map.addSource("cells",{type:"geojson",data:fc});
    map.addLayer({id:"cells-fill",type:"fill",source:"cells",paint:{"fill-color":"#d9ff53","fill-opacity":0.38}});
    map.addLayer({id:"cells-line",type:"line",source:"cells",paint:{"line-color":"#d9ff53","line-width":2}});
    map.on("click","cells-fill",e=>{const f=e.features?.[0];if(f?.properties)setSelected(f.properties)});
    const pts:number[][]=[];const add=(x:any)=>{if(Array.isArray(x)&&typeof x[0]==="number")pts.push(x);else if(Array.isArray(x))x.forEach(add)};
    (fc.features??[]).forEach((f:any)=>add(f.geometry?.coordinates));
    if(pts.length){let minx=999,miny=999,maxx=-999,maxy=-999;pts.forEach(([x,y])=>{minx=Math.min(minx,x);maxx=Math.max(maxx,x);miny=Math.min(miny,y);maxy=Math.max(maxy,y)});map.fitBounds([[minx,miny],[maxx,maxy]],{padding:60,duration:0})}
  }catch(e:any){setError(e.message)}});
  return()=>{map.remove();mapRef.current=null}
 },[]);
 useEffect(()=>{
  const map=mapRef.current;if(!map||!map.getLayer("cells-fill"))return;
  const expression:any=["interpolate",["linear"],["coalesce",["to-number",["get",metric]],0],0,"#67ded7",0.25,"#d9ff53",0.6,"#ffae42",1,"#ff5f57"];
  if(metric==="current_c")expression.splice(3,expression.length-3,25,"#67ded7",32,"#d9ff53",38,"#ffae42",45,"#ff5f57");
  if(metric==="teu"||metric==="va_teu")expression.splice(3,expression.length-3,0,"#67ded7",100,"#d9ff53",180,"#ffae42",260,"#ff5f57");
  map.setPaintProperty("cells-fill","fill-color",expression);
 },[metric]);
 const def=LAYERS.find(x=>x[0]===metric)!;
 return <div className="page"><PageTitle kicker="PLANNING MODE · SPATIAL INTELLIGENCE" title="Thermal Atlas" description="Explore provider-backed temperature, hazard, exposure and vulnerability over OpenStreetMap. Geometry comes from HELIOS PostGIS cells."/>
 <div className="atlas-layout"><section className="map-card"><div className="layer-tabs">{LAYERS.map(([k,label])=><button className={metric===k?"active":""} onClick={()=>setMetric(k)} key={k}>{label}</button>)}</div><div ref={host} className="atlas-map"/>{error&&<div className="map-error">{error}</div>}<div className="map-note">Layer: {def[1]} · OpenStreetMap basemap · HELIOS PostGIS overlay</div></section>
 <aside className="inspector"><div className="eyebrow">CELL INSPECTOR</div><h2>{selected?.cell_id??"Select a cell"}</h2>{selected?<div className="fact-list">
 {LAYERS.map(([k,label,unit])=><div key={k}><span>{label}</span><b>{value(selected[k],unit)}</b></div>)}
 <div><span>Truth category</span><b>{selected.truth_category??"—"}</b></div>
 </div>:<p className="muted">Click a HELIOS polygon to inspect current provider-operational metrics and confidence.</p>}</aside></div></div>
}
function value(v:any,unit:string){const n=Number(v);return Number.isFinite(n)?`${n.toFixed(kdec(n))}${unit?" "+unit:""}`:"—"}function kdec(n:number){return Math.abs(n)>=10?2:3}
