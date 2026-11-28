import {createContext,useContext,useState} from 'react';
import {apiFetch} from './apiClient';
import './account-panel.css';

type Account={email:string;id:string;privateWorkspace:boolean;operator:boolean;busy:boolean;error:string;signOut:()=>void};
type Usage={datasets:number;bytes:number;pending:number;mode:'local'|'cloud'};
type UpstreamStats={calls:number;failures:number;sample_count:number;p95_ms:number|null};
type Ops={scope:string;upstream:Record<string,UpstreamStats>};
export const AccountContext=createContext<Account|null>(null);

export function AccountPanel({onResearch}:{onResearch:()=>void}){
  const account=useContext(AccountContext);
  const [open,setOpen]=useState(false);
  const [usage,setUsage]=useState<Usage|null>(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const [ops,setOps]=useState<Ops|null>(null);
  const [opsBusy,setOpsBusy]=useState(false);
  const [opsError,setOpsError]=useState('');
  if(!account)return null;
  async function loadOps(){
    setOpsBusy(true);setOpsError('');setOps(null);
    try{const r=await apiFetch('/api/v1/auth/ops');setOps(await r.json() as Ops);}
    catch(e){setOpsError(e instanceof Error?e.message:'Diagnostics unavailable.');}
    finally{setOpsBusy(false);}
  }
  async function load(){
    setLoading(true);setError('');setUsage(null);
    try{const r=await apiFetch('/api/v1/auth/usage');setUsage(await r.json() as Usage);}
    catch(e){setError(e instanceof Error?e.message:'Storage usage unavailable.');}
    finally{setLoading(false);}
  }
  return <section className="account-panel" aria-label="Signed-in account">
    <button type="button" className="account-trigger" aria-expanded={open} onClick={()=>setOpen(v=>!v)}>
      <span className="account-avatar" aria-hidden="true">{account.email.charAt(0).toUpperCase()||'A'}</span>
      <span className="account-label"><strong>{account.privateWorkspace?'Personal workspace':'Owner workspace'}</strong><small title={account.email}>{account.email}</small></span>
      <span aria-hidden="true">{open?'−':'+'}</span>
    </button>
    {open&&<div className="account-details">
      <div className="account-profile"><strong>My profile</strong><span>{account.email}</span><small>Google account connected</small><code>{account.id}</code></div>
      <button type="button" className="retry-button" onClick={()=>{onResearch();setOpen(false);}}>My research</button>
      {account.privateWorkspace&&<><button type="button" className="retry-button" disabled={loading} onClick={()=>void load()}>{loading?'Checking…':'Storage usage'}</button>
      {usage&&<p role="status">{usage.datasets} datasets · {(usage.bytes/1048576).toFixed(2)} MiB<br/>{usage.mode==='cloud'?'Cloud':'Local'} storage{usage.pending?` · ${usage.pending} pending upload(s)`:''}</p>}
      {error&&<p role="alert">{error}</p>}</>}
      {account.operator&&<><button type="button" className="retry-button" disabled={opsBusy} onClick={()=>void loadOps()}>{opsBusy?'Checking…':'Operator diagnostics'}</button>
      {ops&&<div role="status"><small>Current backend process</small>{Object.entries(ops.upstream).map(([name,v])=><p key={name}><strong>{name.toUpperCase()}</strong><br/>{v.calls} calls · {v.failures} failed<br/>p95: {v.p95_ms===null?'—':`${v.p95_ms.toFixed(1)} ms`}</p>)}</div>}
      {opsError&&<p role="alert">{opsError}</p>}</>}
      <button type="button" className="retry-button" disabled={account.busy} onClick={account.signOut}>{account.busy?'Signing out…':'Sign out'}</button>
    </div>}
    {account.error&&<p role="alert">{account.error}</p>}
  </section>;
}
