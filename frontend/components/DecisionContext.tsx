"use client";
import {createContext,useContext,useEffect,useMemo,useState} from "react";
import {E,arr,n} from "@/lib/domain";
import {useLive} from "./useLive";

type DecisionState={
 activeCellId:string|null;
 activeCell:any|null;
 providerRows:any[];
 loading:boolean;
 error:string|null;
 setActiveCellId:(id:string|null)=>void;
 clearActiveCell:()=>void;
};
const DecisionContext=createContext<DecisionState|null>(null);
const KEY="helios-active-cell";

export function DecisionProvider({children}:{children:React.ReactNode}){
 const provider=useLive(E.provider);
 const rows=arr(provider.data);
 const [activeCellId,setRaw]=useState<string|null>(null);
 useEffect(()=>{
   const saved=sessionStorage.getItem(KEY);
   if(saved)setRaw(saved);
 },[]);
 useEffect(()=>{
   if(activeCellId||!rows.length)return;
   const highest=[...rows].sort((a,b)=>(n(b,"va_teu")??-Infinity)-(n(a,"va_teu")??-Infinity))[0];
   const id=highest?.cell_id?String(highest.cell_id):null;
   if(id){setRaw(id);sessionStorage.setItem(KEY,id)}
 },[activeCellId,rows.length]);
 function setActiveCellId(id:string|null){setRaw(id);if(id)sessionStorage.setItem(KEY,id);else sessionStorage.removeItem(KEY)}
 const activeCell=useMemo(()=>rows.find(x=>String(x.cell_id)===activeCellId)??null,[rows,activeCellId]);
 const value=useMemo(()=>({activeCellId,activeCell,providerRows:rows,loading:provider.loading,error:provider.error,setActiveCellId,clearActiveCell:()=>setActiveCellId(null)}),[activeCellId,activeCell,rows,provider.loading,provider.error]);
 return <DecisionContext.Provider value={value}>{children}</DecisionContext.Provider>
}

export function useDecision(){
 const v=useContext(DecisionContext);
 if(!v)throw new Error("useDecision must be used inside DecisionProvider");
 return v;
}
