export const API_BASE =
  process.env.NEXT_PUBLIC_HELIOS_API_BASE ?? "/api/helios";

export async function apiGet(path:string, params?:Record<string,string|number|boolean|undefined>){
  const u=new URL(`${API_BASE}${path}`);
  for(const [k,v] of Object.entries(params??{})){
    if(v!==undefined)u.searchParams.set(k,String(v));
  }
  const r=await fetch(u.toString(),{cache:"no-store"});
  if(!r.ok)throw new Error(`${r.status} ${r.statusText}: ${path}`);
  return r.json();
}
export async function apiPost(path:string,body:any){
  const r=await fetch(`${API_BASE}${path}`,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body),
  });
  if(!r.ok)throw new Error(`${r.status} ${r.statusText}: ${(await r.text()).slice(0,500)}`);
  return r.json();
}
export const H={
  system:()=>apiGet("/system/status"),
  caps:()=>apiGet("/system/capabilities"),
  provider:()=>apiGet("/provider-ops/metrics"),
  cells:()=>apiGet("/spatial/cells",{area_id:"phx-downtown"}),
  thermal:()=>apiGet("/thermal/current",{area_id:"phx-downtown"}),
  exposure:()=>apiGet("/exposure/cells",{area_id:"phx-downtown"}),
  interventions:()=>apiGet("/interventions/candidates",{area_id:"phx-downtown"}),
  catalog:()=>apiGet("/interventions/catalog"),
  optimizer:()=>apiGet("/optimizer/runs",{area_id:"phx-downtown"}),
  quality:()=>apiGet("/quality/latest",{area_id:"phx-downtown"}),
  audit:()=>apiGet("/quality/audit",{area_id:"phx-downtown"}),
  packets:()=>apiGet("/context/packets",{area_id:"phx-downtown"}),
  intelligenceRuns:()=>apiGet("/intelligence/runs",{area_id:"phx-downtown"}),
  facilities:()=>apiGet("/facilities",{area_id:"phx-downtown"}),
  demographics:()=>apiGet("/demographics/cells",{area_id:"phx-downtown"}),
  accessibility:()=>apiGet("/thermalway/accessibility"),
  journeys:()=>apiGet("/thermalway/critical-journeys"),
  compare:(o:[number,number],d:[number,number],profile:string)=>apiGet("/thermalway/compare",{
    origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,area_id:"phx-downtown"
  }),
  safeHaven:(o:[number,number],profile:string)=>apiGet("/thermalway/safe-haven",{
    origin_lon:o[0],origin_lat:o[1],profile,area_id:"phx-downtown"
  }),
  ask:(query:string,task_type="portfolio_optimization",mode="investment")=>apiPost("/intelligence/query",{
    area_id:"phx-downtown",query,mode,task_type,force_thinking:false,token_budget:7000
  }),
};
export function rows(v:any):any[]{
  if(Array.isArray(v))return v;
  if(!v||typeof v!=="object")return [];
  for(const k of ["items","results","data","metrics","cells","runs","candidates","facilities","journeys","records"])
    if(Array.isArray(v[k]))return v[k];
  return [];
}
export function num(v:any,...keys:string[]):number|null{
  for(const k of keys){
    const x=Number(v?.[k]);
    if(Number.isFinite(x))return x;
  }
  return null;
}
export function str(v:any,...keys:string[]):string{
  for(const k of keys)if(v?.[k]!==undefined&&v?.[k]!==null)return String(v[k]);
  return "â€”";
}
export function latest(v:any):any{
  const r=rows(v); return r[0]??v??{};
}
export function fmt(v:number|null,d=1){return v==null?"â€”":v.toFixed(d)}
export function money(v:number|null){return v==null?"â€”":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(v)}

