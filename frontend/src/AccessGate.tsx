import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import {useEffect,useState,type FormEvent,type ReactNode} from 'react';
type State={required:boolean;authenticated:boolean};
export function AccessGate({children}:{children:ReactNode}){
  const [state,setState]=useState<State|null>(null);
  const [token,setToken]=useState('');
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  useEffect(()=>{
    const controller=new AbortController();
    void apiFetch('/api/v1/auth/status',{signal:controller.signal}).then(res=>{
      if(!res.ok)throw Error(`Authentication status unavailable (HTTP ${res.status})`);
      return res.json() as Promise<State>;
    }).then(setState).catch(e=>{if(e instanceof Error && e.name!=='AbortError')setError(e.message);});
    return ()=>controller.abort();
  },[]);
  async function login(e:FormEvent){
    e.preventDefault();setBusy(true);setError('');
    try{
      const response=await apiFetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});
      if(!response.ok)throw Error('Access token rejected.');
      setToken('');setState({required:true,authenticated:true});
    }catch(e){setError(e instanceof Error?e.message:'Sign-in unavailable');}
    finally{setBusy(false);}
  }
  async function logout(){
    setError('');
    try{
      const response=await apiFetch('/api/v1/auth/logout',{method:'POST'});
      if(!response.ok)throw Error(`Session logout failed (HTTP ${response.status})`);
      setState({required:true,authenticated:false});
    }catch(e){setError(e instanceof Error?e.message:'Logout unavailable');}
  }
  if(state && (!state.required || state.authenticated))return <>
    {state.required&&<div className="session-toolbar"><button type="button" className="retry-button" onClick={()=>void logout()}>Lock workspace</button></div>}
    {children}
  </>;
  if(!state&&!error)return <main className="startup-screen"><div><h1>∴ AXIOM LAB</h1><Loading label="Connecting to scientific engine"/></div></main>;
  return <main className="access-shell" aria-labelledby="access-title">
    <h1 id="access-title">AXIOM LAB</h1>
    {!state ? <p role="status">Connecting to the scientific workspace…</p>:
      <form onSubmit={e=>void login(e)}>
        <p>Single-user protected workspace. Enter the access token configured by the administrator.</p>
        <label htmlFor="access-token">Access token</label>
        <input id="access-token" type="password" value={token} onChange={e=>setToken(e.target.value)} required autoComplete="current-password"/>
        <button type="submit" className="primary-button" disabled={busy||!token}> {busy?'Checking…':'Unlock workspace'} </button>
      </form>}
    {error&&<div className="inline-alert error" role="alert">{error} <button type="button" onClick={()=>window.location.reload()}>Retry</button></div>}
  </main>;
}
