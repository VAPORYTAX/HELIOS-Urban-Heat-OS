export const API_BASE =
  process.env.NEXT_PUBLIC_HELIOS_API_BASE ?? "http://127.0.0.1:8080/api/v1";

export async function apiGet(path:string, params?:Record<string,string|number|boolean|undefined>){
  const u=new URL(`${API_BASE}${path}`);
  Object.entries(params??{}).forEach(([k,v])=>{if(v!==undefined)u.searchParams.set(k,String(v))});
  const r=await fetch(u.toString(),{cache:"no-store"});
  if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export async function apiPost(path:string, body:any){
  const r=await fetch(`${API_BASE}${path}`,{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)
  });
  if(!r.ok) throw new Error(`${r.status} ${r.statusText}: ${(await r.text()).slice(0,500)}`);
  return r.json();
}

export const helios={
  cells:()=>apiGet("/spatial/cells",{area_id:"phx-downtown"}),
  compare:(o:[number,number],d:[number,number],profile:string)=>apiGet("/thermalway/compare",{
    origin_lon:o[0],origin_lat:o[1],dest_lon:d[0],dest_lat:d[1],profile,area_id:"phx-downtown"
  }),
  ask:(query:string)=>apiPost("/intelligence/query",{
    area_id:"phx-downtown",query,mode:"investment",
    task_type:"portfolio_optimization",force_thinking:false,token_budget:7000
  }),
};
