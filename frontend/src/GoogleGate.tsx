import {useEffect,useRef,useState,type ReactNode} from 'react';
import type {Session} from '@supabase/supabase-js';
import {supabase,googleConfigured,googleConfigError,setGoogleToken} from './supabaseAuth';
import {AxiomMark} from './Motion';
import {Loading} from './WorkspaceTools';

type Verification={user_id:string;workspace_allowed:boolean;mode?:string};
export function GoogleGate({children}:{children:ReactNode}){
  if(!googleConfigured)return <>{children}</>;
  if(googleConfigError || !supabase)return <main className="access-shell"><h1>Authentication configuration required</h1><p>Check the frontend Supabase URL and publishable key.</p></main>;
  return <GoogleSessionGate>{children}</GoogleSessionGate>;
}
function GoogleSessionGate({children}:{children:ReactNode}){
  const client=supabase!;
  const [session,setSession]=useState<Session|null|undefined>(undefined);
  const [verified,setVerified]=useState<{id:string;result:Verification}|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const [retry,setRetry]=useState(0);
  const authorizedIdentity=useRef<string|null>(null);
  useEffect(()=>{
    const {data:{subscription}}=client.auth.onAuthStateChange((_event,next)=>{
      if(!next || next.user.id!==authorizedIdentity.current){authorizedIdentity.current=null;setGoogleToken(null);}
      else setGoogleToken(next.access_token);
      setSession(next);
    });
    return ()=>{subscription.unsubscribe();authorizedIdentity.current=null;setGoogleToken(null);};
  },[client]);
  const userId=session?.user.id;
  useEffect(()=>{
    setVerified(null);
    if(!userId)return;
    const controller=new AbortController();
    // Verification is repeated on identity changes and manual retry; every protected API request is independently checked server-side.
    const run=async()=>{
      try{
        const {data,error:sessionError}=await client.auth.getSession();
        if(sessionError || !data.session || data.session.user.id!==userId)throw new Error('Session unavailable. Sign in again.');
        const res=await fetch('/api/v1/auth/google/verify',{headers:{Authorization:`Bearer ${data.session.access_token}`},cache:'no-store',signal:controller.signal});
        if(!res.ok)throw new Error(`Server could not verify your session (HTTP ${res.status}). Check backend configuration.`);
        const result=await res.json() as Verification;
        if(result.user_id!==userId)throw new Error('Session identity mismatch.');
        if(!controller.signal.aborted){
          const latest=await client.auth.getSession();
          if(controller.signal.aborted || latest.error || latest.data.session?.user.id!==userId)return;
          if(result.workspace_allowed){authorizedIdentity.current=userId;setGoogleToken(latest.data.session.access_token);}
          setVerified({id:userId,result});setError('');
        }
      }catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Verification unavailable.');}
    };
    void run();return ()=>controller.abort();
  },[client,userId,retry]);
  async function signIn(){
    setBusy(true);setError('');
    try{
      const redirect=new URL(window.location.pathname,window.location.origin);redirect.searchParams.set('view','studio');
      const {error:e}=await client.auth.signInWithOAuth({provider:'google',options:{redirectTo:redirect.toString()}});
      if(e)throw e;
    }catch{setError('Google sign-in could not start. Check your connection and retry.');setBusy(false);}
  }
  async function signOut(){
    setBusy(true);setError('');
    try{const {error:e}=await client.auth.signOut({scope:'local'});if(e)throw e;}
    catch{setError('Sign-out failed. Retry.');}finally{setBusy(false);}
  }
  if(session && verified && verified.id===userId && verified.result.workspace_allowed)return <><div className="session-toolbar"><span>{session.user.email??'Signed-in researcher'}{verified.result.mode==='multi-user beta'?' · Private workspace':''}</span><button type="button" className="retry-button" disabled={busy} onClick={()=>void signOut()}>Sign out of Google</button>{error&&<span role="alert">{error}</span>}</div><section key={userId} style={{display:'contents'}}>{children}</section></>;
  return <main className="access-shell" aria-labelledby="google-title"><a className="access-home-link" href="./">← Back to AXIOM LAB home</a><AxiomMark/><h1 id="google-title">AXIOM LAB</h1>
    {session===undefined?<Loading label="Checking Google session"/>:!session?<><p>Sign in to your research studio with Google.</p><button className="primary-button" type="button" disabled={busy} onClick={()=>void signIn()}>Continue with Google</button></>:<>
      {verified?<><p>{verified.result.mode==='multi-user beta'?'Google identity verified. Ask the administrator to invite this user ID to the private beta.':'Google identity verified. Workspace access is limited to the configured owner.'}</p><p>Verified account ID: <code>{verified.result.user_id}</code></p></>:!error?<Loading label="Verifying identity with the scientific API"/>:<button className="retry-button" onClick={()=>{setError('');setRetry(n=>n+1);}}>Retry verification</button>}
      <button className="retry-button" type="button" disabled={busy} onClick={()=>void signOut()}>Sign out</button></>}
    {error&&<p className="inline-alert error" role="alert">{error}</p>}
  </main>;
}
