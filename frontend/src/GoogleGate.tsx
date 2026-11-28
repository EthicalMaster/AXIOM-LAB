import {useEffect,useRef,useState,type ReactNode} from 'react';
import type {Session} from '@supabase/supabase-js';
import {supabase,googleConfigured,googleConfigError,setGoogleToken} from './supabaseAuth';
import {AxiomMark} from './Motion';
import {ThemeSwitch} from './Theme';
import {AccountContext} from './AccountPanel';
import {Loading} from './WorkspaceTools';

type Verification={user_id:string;workspace_allowed:boolean;operator?:boolean;mode?:string};
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
  if(session && verified && verified.id===userId && verified.result.workspace_allowed)return <AccountContext.Provider key={userId} value={{email:session.user.email??'Signed-in researcher',id:userId!,privateWorkspace:verified.result.mode==='multi-user beta',operator:verified.result.operator===true,busy,error,signOut:()=>void signOut()}}>{children}</AccountContext.Provider>;
  return <main className="auth-experience" aria-labelledby="google-title">
    <aside className="auth-brand-panel" aria-label="About AXIOM LAB">
      <a className="auth-wordmark" href="./"><span>∴</span> AXIOM LAB</a>
      <div className="auth-brand-content"><div className="auth-orbit" aria-hidden="true"><AxiomMark/></div><span className="auth-kicker">RESEARCH / STUDIO</span><h2>Good research starts with evidence.</h2><p>Explore data, investigate relationships and keep a reproducible record of your findings.</p><div className="auth-principles"><span>01 · Original data</span><span>02 · Scientific methods</span><span>03 · Research records</span></div></div>
      <footer>AXIOM LAB · Scientific research workspace</footer>
    </aside>
    <section className="auth-content"><div className="auth-top"><a href="./">← Back to home</a><ThemeSwitch/></div>
      <div className="auth-card"><span className="auth-kicker">YOUR RESEARCH WORKSPACE</span>
        <h1 id="google-title">{session===undefined?'Checking your session':!session?'Welcome to AXIOM LAB':verified?'Workspace access required':'Verifying your identity'}</h1>
        {session===undefined?<Loading label="Checking Google session"/>:!session?<><p>Sign in with Google to access your research, datasets and experiments.</p><button className="auth-google" type="button" disabled={busy} onClick={()=>void signIn()}><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.4-.2-2.1H12v4h5.4a4.6 4.6 0 0 1-2 3v2.6h3.3c1.9-1.7 2.9-4.3 2.9-7.5Z"/><path fill="#34A853" d="M12 22c2.7 0 5-.9 6.7-2.3L15.4 17c-.9.6-2.1 1-3.4 1-2.6 0-4.8-1.7-5.6-4.1H3v2.7A10 10 0 0 0 12 22Z"/><path fill="#FBBC05" d="M6.4 13.9a6 6 0 0 1 0-3.8V7.4H3a10 10 0 0 0 0 9.2Z"/><path fill="#EA4335" d="M12 6c1.5 0 2.8.5 3.8 1.5l2.9-2.9A9.6 9.6 0 0 0 12 2a10 10 0 0 0-9 5.4l3.4 2.7A5.9 5.9 0 0 1 12 6Z"/></svg>{busy?'Connecting…':'Continue with Google'}</button><p className="auth-note">Authentication is handled by Google and Supabase. Workspace permissions are verified separately.</p></>:<>
          {verified?<><p>Your Google identity has been verified. {verified.result.mode==='multi-user beta'?'Ask the administrator to invite this account to the private beta.':'Workspace access is limited to the configured owner.'}</p><div className="auth-identity"><span>Verified account ID</span><code>{verified.result.user_id}</code></div></>:!error?<Loading label="Verifying identity with the scientific API"/>:<button className="retry-button" type="button" onClick={()=>{setError('');setRetry(n=>n+1);}}>Retry verification</button>}
          <button className="retry-button auth-signout" type="button" disabled={busy} onClick={()=>void signOut()}>{busy?'Signing out…':'Sign out'}</button></>}
        {error&&<p className="inline-alert error" role="alert">{error}</p>}
      </div><footer className="auth-content-footer">Evidence first. Every result should have a reason.</footer>
    </section>
  </main>;
}
