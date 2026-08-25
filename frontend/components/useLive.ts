"use client";
import {useEffect,useState} from "react";
export function useLive<T>(fn:()=>Promise<T>,deps:any[]=[]){
 const [data,setData]=useState<T|null>(null),[error,setError]=useState<string|null>(null),[loading,setLoading]=useState(true),[attempt,setAttempt]=useState(0);
 useEffect(()=>{let m=true;setLoading(true);setError(null);fn().then(x=>m&&setData(x)).catch(e=>m&&setError(e.message)).finally(()=>m&&setLoading(false));return()=>{m=false}},[attempt,...deps]);
 return {data,error,loading,retry:()=>setAttempt(x=>x+1)};
}
