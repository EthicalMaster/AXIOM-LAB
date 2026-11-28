import {useEffect,useId,useRef,useState,type FormEvent} from 'react';
import {apiFetch} from './apiClient';
import {AIAnswer} from './AIAnswer';
import {AxiomMark} from './Motion';

type Reply={answer:string;source:string;question:string;providerRequested:boolean};
const prompts=['How should I begin exploring my dataset?','How do I choose an appropriate statistical test?','What does R² tell me about a model?','How can I make an experiment reproducible?'];
export function ResearchAssistant({datasetId}:{datasetId?:string}){
 const id=useId(),[question,setQuestion]=useState(''),[remote,setRemote]=useState(false),[reply,setReply]=useState<Reply|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[copied,setCopied]=useState(false);
 const pending=useRef<AbortController|null>(null),input=useRef<HTMLTextAreaElement>(null);
 useEffect(()=>()=>{pending.current?.abort();pending.current=null},[]);
 async function ask(e:FormEvent){e.preventDefault();const q=question.trim();if(!q||pending.current)return;const controller=new AbortController();pending.current=controller;setBusy(true);setError('');setReply(null);setCopied(false);
  try{const response=await apiFetch('/api/v1/ai/guide',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({question:q,page:'Method guide',dataset_id:datasetId??null,use_provider:remote})});const data=await response.json() as {answer?:unknown;source?:unknown};if(typeof data.answer!=='string'||typeof data.source!=='string')throw Error('Unexpected assistant response.');if(!controller.signal.aborted)setReply({answer:data.answer,source:data.source,question:q,providerRequested:remote});}
  catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Assistant unavailable.');}
  finally{if(pending.current===controller){pending.current=null;setBusy(false)}}
 }
 function cancel(){pending.current?.abort();pending.current=null;setBusy(false);}
 async function copy(){if(!reply)return;try{await navigator.clipboard.writeText(reply.answer);setCopied(true)}catch{setError('Copy unavailable. Select and copy the answer manually.')}}
 return <section className="research-assistant" aria-labelledby={`${id}-title`}>
  <header className="assistant-heading"><AxiomMark/><div><span className="overline">AXIOM / RESEARCH INTELLIGENCE</span><h2 id={`${id}-title`}>AXIOM AI</h2><p>Understand a result, choose a method, or plan your next research step.</p></div></header>
  <div className="assistant-context"><span>{datasetId?'Active dataset · structural context':'General scientific guidance'}</span><span>{remote?'External provider requested':'Built-in guide'}</span></div>
  {!reply&&!busy&&<div className="assistant-prompts">{prompts.map(p=><button key={p} type="button" onClick={()=>{setQuestion(p);input.current?.focus()}}>{p}<span aria-hidden="true">↗</span></button>)}</div>}
  <form className="assistant-form" onSubmit={ask}><label htmlFor={`${id}-q`}>Your research question</label><textarea id={`${id}-q`} ref={input} rows={3} maxLength={500} value={question} disabled={busy} onChange={e=>setQuestion(e.target.value)} placeholder="What assumptions should I check before using a t-test?"/>
   <label className="assistant-optin"><input type="checkbox" checked={remote} disabled={busy} onChange={e=>setRemote(e.target.checked)}/><span><strong>Use external AI</strong><small>Sends your question and limited dataset structure to the configured provider. Avoid confidential information.</small></span></label>
   <div className="assistant-actions"><small>{question.length}/500</small>{busy?<button type="button" className="retry-button" onClick={cancel}>Cancel waiting</button>:<button className="primary-button" type="submit" disabled={!question.trim()}>Ask AXIOM <span aria-hidden="true">↗</span></button>}</div></form>
  {busy&&<div className="assistant-progress" role="status"><AxiomMark small/><span>{remote?'Requesting provider explanation…':'Preparing local guidance…'}</span></div>}
  {error&&<p className="inline-alert error" role="alert">{error}</p>}
  {reply&&<article className="assistant-result"><header><div><span className="overline">{reply.source}</span><h3>{reply.question}</h3></div><button type="button" className="retry-button" onClick={()=>void copy()}>{copied?'Copied':'Copy'}</button></header>{reply.providerRequested&&!reply.source.startsWith('Optional AI')&&<p className="assistant-fallback">External AI was unavailable. Showing built-in guidance.</p>}<AIAnswer text={reply.answer}/></article>}
  <footer>Advisory explanations only. Scientific calculations and saved evidence remain independent.</footer>
 </section>
}
