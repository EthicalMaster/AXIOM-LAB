import {useState,type FormEvent,type ReactNode} from 'react';
import {apiFetch} from './apiClient';
import {Loading} from './WorkspaceTools';
import {WorkspaceIcon} from './WorkspaceIcon';
export function useMathRequest<T>(){
 const [result,setResult]=useState<T|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function run(path:string,payload:unknown){if(busy)return null;setError('');setBusy(true);setResult(null);try{const r=await apiFetch(`/api/v1/math/${path}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const value=await r.json() as T;setResult(value);return value;}catch(e){setError(e instanceof Error?e.message:'Computation failed.');return null;}finally{setBusy(false);}}
 return {result,error,busy,run,setError};
}
export function MathShell({title,subtitle,children,onSubmit,busy,error,result}:{title:string;subtitle:string;children:ReactNode;onSubmit:(e:FormEvent<HTMLFormElement>)=>void;busy:boolean;error:string;result:ReactNode}){return <section className="science-panel math-panel" aria-label={title}><header className="math-panel-header"><div><h3>{title}</h3><p>{subtitle}</p></div><span className="math-engine-chip">CPU / BOUNDED INPUT</span></header><div className="math-split"><form className="math-input" onSubmit={onSubmit}>{children}</form><div className="math-output" aria-busy={busy}>{busy?<Loading label="Computing scientific result"/>:error?<div className="inline-alert error" role="alert">{error}</div>:result??<div className="math-empty"><span aria-hidden="true">∴</span><strong>Ready to calculate</strong><p>Choose an input and run the calculation to see results here.</p></div>}</div></div></section>}
export function MathAction({busy,children}:{busy:boolean;children:ReactNode}){return <button type="submit" className="primary-button math-action" disabled={busy}><span>{busy?'Computing…':children}</span><WorkspaceIcon name="arrow"/></button>}
export function readNumbers(text:string,min:number,max:number){const parts=text.split(',').map(s=>s.trim());const nums=parts.map(Number);return parts.length>=min&&parts.length<=max&&parts.every(Boolean)&&nums.every(Number.isFinite)?nums:null;}
export function Warnings({items}:{items:string[]}){return items.length>0?<ul className="warning-panel math-warnings">{items.map((w,i)=><li key={i}>{w}</li>)}</ul>:null;}
