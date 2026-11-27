import {Loading,RecoveryScreen} from './WorkspaceTools';
import {AxiomMark} from './Motion';
import {apiFetch} from './apiClient';
import {useEffect,useState,type FormEvent,type ReactNode} from 'react';
type State={required:boolean;authenticated:boolean};
export function AccessGate({children}:{children:ReactNode}){
  const [state,setState]=useState<State|null>(null);
  const [token,setToken]=useState('');
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const [attempt,setAttempt]=useState(0);
  useEffect(()=>{
    const controller=new AbortController();
    void apiFetch('/api/v1/auth/status',{signal:controller.signal}).then(res=>{
      return res.json() as Promise<State>;
    }).then(setState).catch(e=>{if(e instanceof Error && e.name!=='AbortError')setError(e.message);});
    return ()=>controller.abort();
  },[attempt]);
  async function login(e:FormEvent){
    e.preventDefault();if(busy)return;setBusy(true);setError('');
    try{
      await apiFetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});
      setToken('');setState({required:true,authenticated:true});
    }catch(e){setError(e instanceof Error?e.message:'Sign-in unavailable');}
    finally{setBusy(false);}
  }
  async function logout(){
    if(busy)return;setBusy(true);setError('');
    try{
      await apiFetch('/api/v1/auth/logout',{method:'POST'});
      setState({required:true,authenticated:false});
    }catch(e){setError(e instanceof Error?e.message:'Logout unavailable');}finally{setBusy(false);}
  }
  if(state && (!state.required || state.authenticated))return <>
    {state.required&&<div className="session-toolbar"><button type="button" className="retry-button" disabled={busy} onClick={()=>void logout()}>{busy?'Locking…':'Lock workspace'}</button></div>}
    {error&&<div className="inline-alert error session-error" role="alert">{error} <button type="button" onClick={()=>setError('')}>Dismiss</button></div>}
    {children}
  </>;
  if(!state&&!error)return <main className="startup-screen"><div className="startup-identity"><AxiomMark/><h1>AXIOM LAB</h1><p>Scientific research studio</p><Loading label="Checking workspace access"/></div></main>;
  if(!state&&error)return <RecoveryScreen full title="Cannot connect to AXIOM LAB" detail={error} onRetry={()=>{setError('');setAttempt(n=>n+1)}}/>;
  return <main className="access-shell" aria-labelledby="access-title">
    <h1 id="access-title">AXIOM LAB</h1>
    <form onSubmit={e=>void login(e)}>
        <p>Single-user protected workspace. Enter the access token configured by the administrator.</p>
        <label htmlFor="access-token">Access token</label>
        <input id="access-token" type="password" value={token} onChange={e=>setToken(e.target.value)} required autoComplete="current-password"/>
        <button type="submit" className="primary-button" disabled={busy||!token}> {busy?'Checking…':'Unlock workspace'} </button>
        {busy&&<Loading label="Checking workspace access"/>}
      </form>
    {error&&<div className="inline-alert error" role="alert">{error} <button type="button" onClick={()=>setError('')}>Dismiss</button></div>}
  </main>;
}
