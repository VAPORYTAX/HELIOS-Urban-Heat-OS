export const API_BASE=process.env.NEXT_PUBLIC_HELIOS_API_BASE ?? "/api/helios";

export async function get(path:string,params?:Record<string,any>){
 const qs=new URLSearchParams();
 for(const [k,v] of Object.entries(params??{})){
   if(v!==undefined&&v!==null) qs.set(k,String(v));
 }
 const query=qs.toString();
 const url=`${API_BASE}${path}${query?`?${query}`:""}`;
 const r=await fetch(url,{cache:"no-store"});
 if(!r.ok) throw new Error(`${r.status} ${r.statusText}: ${path}`);
 return r.json();
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
 interventions:()=>get("/interventions/provider-native/candidates",{area_id:"phx-downtown"}),
 optimizer:()=>get("/optimizer/provider-native/latest",{area_id:"phx-downtown"}),
 quality:()=>get("/quality/latest",{area_id:"phx-downtown"}),
 packets:()=>get("/context/packets",{area_id:"phx-downtown"}),
 accessibility:()=>get("/thermalway/accessibility"),
 journeys:()=>get("/thermalway/critical-journeys"),
 compare:(o:[number,number],d:[number,number],profile:string)=>get("/thermalway/compare",{origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,area_id:"phx-downtown"}),
 ask:(query:string)=>post("/intelligence/query",{area_id:"phx-downtown",query,mode:"investment",task_type:"portfolio_optimization",force_thinking:false,token_budget:7000})
};

export function arr(v:any):any[]{
 if(Array.isArray(v)) return v;
 if(!v||typeof v!=="object") return [];
 for(const k of ["items","results","data","metrics","cells","runs","candidates","records","facilities","journeys","checks"]) if(Array.isArray(v[k])) return v[k];
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


