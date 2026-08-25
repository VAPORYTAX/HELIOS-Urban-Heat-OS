export const API_BASE =
  process.env.NEXT_PUBLIC_HELIOS_API_BASE ?? "/api/helios";

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

export async function apiGet<T = Json>(path: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params ?? {}).forEach(([k,v]) => {
    if (v !== undefined) url.searchParams.set(k, String(v));
  });
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${path}`);
  return res.json() as Promise<T>;
}

export const live = {
  system: () => apiGet("/system/status"),
  capabilities: () => apiGet("/system/capabilities"),
  providerOps: () => apiGet("/provider-ops/metrics"),
  thermalCurrent: (area_id:string) => apiGet("/thermal/current",{area_id}),
  exposureCells: (area_id:string) => apiGet("/exposure/cells",{area_id}),
  exposureArea: (area_id:string) => apiGet("/exposure/area",{area_id}),
  interventions: (area_id:string) => apiGet("/interventions/candidates",{area_id}),
  optimizerRuns: (area_id:string) => apiGet("/optimizer/runs",{area_id}),
  intelligenceRuns: (area_id:string) => apiGet("/intelligence/runs",{area_id}),
  qualityLatest: (area_id:string) => apiGet("/quality/latest",{area_id}),
  contextCells: (area_id:string) => apiGet("/context/cells",{area_id}),
  demographics: (area_id:string) => apiGet("/demographics/cells",{area_id}),
  facilities: (area_id:string) => apiGet("/facilities",{area_id}),
  accessibility: () => apiGet("/thermalway/accessibility"),
  criticalJourneys: () => apiGet("/thermalway/critical-journeys"),
};

