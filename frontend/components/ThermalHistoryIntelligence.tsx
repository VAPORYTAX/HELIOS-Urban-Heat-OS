"use client";
import {E,arr,fmt,n,s} from "@/lib/domain";
import {useLive} from "./useLive";
import {useDecision} from "./DecisionContext";

export default function ThermalHistoryIntelligence(){
 const {activeCellId}=useDecision();
 const bx=useLive(E.baselines),sx=useLive(E.thermalStress),hx=useLive(E.hotspots);
 const baselines=arr(bx.data).filter(x=>String(x.cell_id)===activeCellId),stress=arr(sx.data).filter(x=>String(x.cell_id)===activeCellId),hotspots=arr(hx.data);
 const b=baselines[0]??null,st=stress[0]??null,h=hotspots[0]??null;
 const error=bx.error||sx.error||hx.error;
 return <section className="thermal-history panel"><div className="thermal-history-head"><div><div className="section-kicker">TEMPORAL INTELLIGENCE · REAL PROVIDER HISTORY</div><h2>Is this cell merely hot, or unusually and persistently hot?</h2><p>Baseline, anomaly, z-score, persistence, threshold exceedance and hotspot evidence separate today’s temperature from its historical context.</p></div><span className="truth-badge provider">PROVIDER + DERIVED</span></div>
 {error&&<div className="errorbox">Historical thermal intelligence unavailable: {error} <button onClick={()=>{bx.retry();sx.retry();hx.retry()}}>Retry</button></div>}
 <div className="history-active"><span>ACTIVE CELL</span><b>{activeCellId??"—"}</b><small>{b?`${s(b,"sample_days")} historical sample days · local hour ${s(b,"local_hour")}`:"No baseline row for active cell"}</small></div>
 <div className="history-metrics"><article><span>Current</span><b>{fmt(n(b,"current_c"),1)} °C</b><small>provider now-state</small></article><article><span>Historical mean</span><b>{fmt(n(b,"mean_c"),1)} °C</b><small>same-hour baseline</small></article><article className="accent"><span>Anomaly</span><b>{n(b,"anomaly_c")!==null?`${n(b,"anomaly_c")!>=0?"+":""}${fmt(n(b,"anomaly_c"),1)} °C`:"—"}</b><small>relative to baseline</small></article><article><span>Z-score</span><b>{fmt(n(b,"z_score"),2)}</b><small>standardized anomaly</small></article><article><span>Persistence</span><b>{fmt(n(st,"persistence_hours"),1)} h</b><small>thermal-stress persistence</small></article><article><span>Exceedance</span><b>{fmt(n(st,"exceedance_hours"),1)} h</b><small>above {fmt(n(st,"threshold_c"),1)} °C threshold</small></article></div>
 <div className="history-grid"><article><div className="section-kicker">BASELINE CONFIDENCE</div><h3>{fmt(n(b,"confidence"),2)}</h3><p>{b?`Median ${fmt(n(b,"median_c"),1)} °C · standard deviation ${fmt(n(b,"std_c"),2)} °C.`:"No baseline evidence returned for this cell."}</p><small>{s(b,"truth_category")}</small></article><article><div className="section-kicker">LATEST HOTSPOT RECORD</div><h3>{h?s(h,"status","severity"):"No hotspot record"}</h3><p>{h?`Peak ${fmt(n(h,"peak_temperature_c"),1)} °C · mean anomaly ${fmt(n(h,"mean_anomaly_c"),1)} °C · max persistence ${fmt(n(h,"max_persistence_hours"),1)} h across ${s(h,"cell_count")} cells.`:"HELIOS does not infer a hotspot when no stored hotspot evidence is returned."}</p><small>{h?`Confidence ${fmt(n(h,"confidence"),2)}`:"No fabricated hotspot status"}</small></article></div>
 <div className="truth-callout"><b>History is evidence, not prediction.</b><p>These fields describe provider-backed historical context and deterministic derived stress metrics. They are not a weather forecast and do not extend the observed footprint beyond the four validated downtown cells.</p></div>
 </section>
}
