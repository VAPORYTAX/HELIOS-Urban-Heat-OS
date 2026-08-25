import {setRuntimeState} from "./runtime";

export const API_BASE=process.env.NEXT_PUBLIC_HELIOS_API_BASE ?? "/api/helios";
const CACHE_PREFIX="helios:last-verified:";
let snapshotPromise:Promise<any>|null=null;
const SNAPSHOT_SAFE=(key:string)=>!key.startsWith("/thermalway/compare")&&!key.startsWith("/thermalway/route")&&!key.startsWith("/thermalway/pareto")&&!key.startsWith("/thermalway/safe-haven")&&!key.startsWith("/thermalway/time-optimizer")&&!key.startsWith("/thermalway/exposure-budget");

function cacheKey(key:string){return CACHE_PREFIX+key}
function writeCache(key:string,data:any){if(typeof window==="undefined"||!SNAPSHOT_SAFE(key))return;try{localStorage.setItem(cacheKey(key),JSON.stringify({captured_at:new Date().toISOString(),data}))}catch{}}
function readCache(key:string){if(typeof window==="undefined"||!SNAPSHOT_SAFE(key))return null;try{return JSON.parse(localStorage.getItem(cacheKey(key))??"null")}catch{return null}}
async function staticSnapshot(){
 if(typeof window==="undefined")return null;
 if(!snapshotPromise)snapshotPromise=fetch("/data/verified_snapshot.json",{cache:"no-store"}).then(r=>r.ok?r.json():null).catch(()=>null);
 return snapshotPromise;
}

export async function get(path:string,params?:Record<string,any>){
 const qs=new URLSearchParams();
 for(const [k,v] of Object.entries(params??{})){
   if(v!==undefined&&v!==null) qs.set(k,String(v));
 }
 const query=qs.toString();
 const key=`${path}${query?`?${query}`:""}`;
 const url=`${API_BASE}${key}`;
 try{
  const r=await fetch(url,{cache:"no-store"});
  if(!r.ok) throw new Error(`${r.status} ${r.statusText}: ${path}`);
  const data=await r.json();
  writeCache(key,data);
  if(path==="/system/status")setRuntimeState({mode:"live"});
  return data;
 }catch(err:any){
  if(SNAPSHOT_SAFE(key)){
   const snap=await staticSnapshot();
   if(snap?.status==="verified_snapshot"&&snap?.endpoints&&Object.prototype.hasOwnProperty.call(snap.endpoints,key)){
    if(path==="/system/status")setRuntimeState({mode:"snapshot",snapshotAt:snap.generated_at??null});
    return snap.endpoints[key];
   }
   const cached=readCache(key);
   if(cached?.data!==undefined){
    if(path==="/system/status")setRuntimeState({mode:"snapshot",snapshotAt:cached.captured_at??null});
    return cached.data;
   }
  }
  if(path==="/system/status")setRuntimeState({mode:"offline"});
  throw err;
 }
}
export async function post(path:string,body:any){
 const r=await fetch(`${API_BASE}${path}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 if(!r.ok) throw new Error(`${r.status} ${r.statusText}: ${(await r.text()).slice(0,400)}`);
 return r.json();
}
export const E={
 system:()=>get("/system/status"),
 caps:()=>get("/system/capabilities"),
 provider:()=>get("/provider-ops/metrics"),
 cells:()=>get("/spatial/cells",{area_id:"phx-downtown"}),
 baselines:()=>get("/fortyguard/history/baselines",{area_id:"phx-downtown"}),
 thermalStress:()=>get("/fortyguard/history/stress",{area_id:"phx-downtown"}),
 hotspots:()=>get("/thermal/hotspots",{area_id:"phx-downtown"}),
 interventions:()=>get("/interventions/provider-native/candidates",{area_id:"phx-downtown"}),
 scenarios:()=>get("/scenarios",{area_id:"phx-downtown"}),
 scenarioResult:(id:string)=>get(`/scenarios/${id}/result`),
 optimizer:()=>get("/optimizer/provider-native/latest",{area_id:"phx-downtown"}),
 decisionScience:()=>get("/decision-science/latest",{area_id:"phx-downtown"}),
 agents:()=>get("/agents/runs",{area_id:"phx-downtown"}),
 latestAgent:()=>get("/agents/recommendations/latest",{area_id:"phx-downtown"}),
 agentRun:(id:string)=>get(`/agents/runs/${id}`),
 quality:()=>get("/quality/latest",{area_id:"phx-downtown"}),
 packets:()=>get("/context/packets",{area_id:"phx-downtown"}),
 accessibility:()=>get("/thermalway/accessibility"),
 journeys:()=>get("/thermalway/critical-journeys"),
 thermalModes:()=>get("/thermalway/modes"),
 compare:(o:[number,number],d:[number,number],profile:string)=>get("/thermalway/compare",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,area_id:"phx-downtown"}),
 routeMode:(o:[number,number],d:[number,number],profile:string,mode:"fastest"|"cool"|"warm"|"thermal_safe")=>get("/thermalway/route",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,mode}),
 pareto:(o:[number,number],d:[number,number],profile:string)=>get("/thermalway/pareto",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,k:5}),
 safeHaven:(o:[number,number],profile:string)=>get("/thermalway/safe-haven",{origin_lon:o[0],origin_lat:o[1],profile}),
 timeOptimizer:(o:[number,number],d:[number,number],profile:string)=>get("/thermalway/time-optimizer",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile}),
 exposureBudget:(o:[number,number],d:[number,number],profile:string,budget?:number)=>get("/thermalway/exposure-budget",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,thermal_budget:budget}),
 ask:(query:string)=>post("/intelligence/query",{area_id:"phx-downtown",query,mode:"investment",task_type:"portfolio_optimization",force_thinking:false,token_budget:7000})
};

export function arr(v:any):any[]{
 if(Array.isArray(v)) return v;
 if(!v||typeof v!=="object") return [];
 for(const k of ["items","results","data","metrics","cells","runs","candidates","records","facilities","journeys","checks","recommended_actions","modes"]) if(Array.isArray(v[k])) return v[k];
 return [];
}
export function n(v:any,...keys:string[]):number|null{
 for(const k of keys){const x=Number(v?.[k]);if(Number.isFinite(x))return x}
 return null;
}
export function s(v:any,...keys:string[]):string{
 for(const k of keys) if(v?.[k]!==undefined&&v?.[k]!==null&&String(v[k]).trim()) return String(v[k]);
 return "—";
}
export function latest(v:any){
 const a=arr(v);
 if(!a.length) return v??{};
 return [...a].sort((x,y)=>Date.parse(y.created_at??y.timestamp??0)-Date.parse(x.created_at??x.timestamp??0))[0];
}
export function providerOptimizer(v:any){
 const a=arr(v);
 if(!a.length&&v&&typeof v==="object")return v;
 const ranked=[...a].sort((x,y)=>{
   const score=(z:any)=>(n(z,"teu_reduction","modeled_teu_reduction")!==null?10:0)+(n(z,"va_teu_reduction","modeled_va_teu_reduction")!==null?10:0)+(s(z,"status")==="optimal"?3:0)+(n(z,"confidence")!==null?2:0)+(n(z,"total_cost")===99000?1:0);
   return score(y)-score(x)
 });
 return ranked[0]??latest(v);
}
export function money(x:number|null){return x==null?"—":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(x)}
export function fmt(x:number|null,d=2){return x==null?"—":x.toFixed(d)}
export function labelAction(x:any){
 return s(x,"intervention_type","type","name","action","catalog_name","intervention_name");
}
