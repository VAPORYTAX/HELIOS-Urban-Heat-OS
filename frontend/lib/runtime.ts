export type HeliosRuntimeMode="live"|"snapshot"|"offline"|"checking";
export type HeliosRuntimeState={mode:HeliosRuntimeMode;snapshotAt?:string|null};
const KEY="helios-runtime-state";
export function readRuntimeState():HeliosRuntimeState{
 if(typeof window==="undefined")return {mode:"checking"};
 try{return JSON.parse(sessionStorage.getItem(KEY)??"") as HeliosRuntimeState}catch{return {mode:"checking"}}
}
export function setRuntimeState(state:HeliosRuntimeState){
 if(typeof window==="undefined")return;
 try{sessionStorage.setItem(KEY,JSON.stringify(state))}catch{}
 window.dispatchEvent(new CustomEvent("helios:runtime-state",{detail:state}));
}
