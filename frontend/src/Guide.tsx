import {useEffect,useId,useRef,useState,type FormEvent,type CSSProperties} from 'react';
import {apiFetch} from './apiClient';
import {AxiomMark} from './Motion';
import './guide.css';
import {SelectionLens} from './Lens';
import {LENS_EVENT,type LensContext} from './lensContext';

const topics = [
  {title:'Understand p-values',question:'What is a p-value?',answer:'A p-value measures how unusual the observed result (or more extreme results) would be under the null hypothesis. It is not the probability that the null is true.'},
  {title:'Import a dataset',question:'How do I import data?',answer:'Open Overview, select a CSV, XLSX or XLS file and choose Validate and import. Review the Data Lab before selecting a method.'},
  {title:'Interpret R²',question:'How should I read R²?',answer:'Held-out R² compares prediction error against a constant prediction of the test-set mean. It can be negative; a perfect score on artificial data does not prove real-world performance.'},
  {title:'Confidence intervals',question:'What does a confidence interval mean?',answer:'A 95% confidence interval is constructed by a procedure that would cover the true parameter in 95% of repeated samples under its assumptions.'},
  {title:'Reproduce a result',question:'How do I reproduce a result?',answer:'Save a chart experiment, open Experiments, select its history, and choose Reproduce latest run. Compare the new result against the recorded evidence.'},
];
type Reply={answer:string;source:string;question:string;context:string};

function Arrow({up=false}:{up?:boolean}){return <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{up?<path d="M10 16V4m-5 5 5-5 5 5"/>:<path d="M5 15 15 5M6 5h9v9"/>}</svg>}

export function Guide({page,datasetId,numericColumns=[]}:{page:string;datasetId?:string;numericColumns?:string[]}){
  const [open,setOpen]=useState(false),[question,setQuestion]=useState(''),[reply,setReply]=useState<Reply|null>(null);
  const [busy,setBusy]=useState(false),[column,setColumn]=useState(''),[remote,setRemote]=useState(false),[error,setError]=useState('');
  const [optionsOpen,setOptionsOpen]=useState(false);
  const [selection,setSelection]=useState<LensContext|null>(null);
  const id=useId();
  const launcher=useRef<HTMLButtonElement>(null),heading=useRef<HTMLHeadingElement>(null),questionInput=useRef<HTMLTextAreaElement>(null);
  const response=useRef<HTMLDivElement>(null),request=useRef<AbortController|null>(null);
  const selectedColumn=datasetId&&numericColumns.includes(column)?column:'';
  const context=selectedColumn?`${page} · ${selectedColumn}`:page;
  const canAsk=!!question.trim()&&!busy;
  useEffect(()=>()=>{request.current?.abort();request.current=null},[]);
  useEffect(()=>{if(open)heading.current?.focus()},[open]);
  useEffect(()=>{if(open&&(reply||error||busy))response.current?.scrollIntoView({block:'nearest',behavior:'instant'})},[reply,error,busy,open]);
  function close(){setOpen(false);launcher.current?.focus()}
  function clear(){setQuestion('');setSelection(null);setReply(null);setError('');questionInput.current?.focus()}
  async function ask(e?:FormEvent, attached=selection, prompt=question){
    e?.preventDefault();const text=prompt.trim();if(!text||request.current)return;
    const controller=new AbortController();request.current=controller;
    setBusy(true);setError('');setReply(null);
    try{
      const r=await apiFetch('/api/v1/ai/guide',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({question:text,page,dataset_id:datasetId??null,column:attached?null:selectedColumn||null,use_provider:remote,selection:attached})});
      const data=await r.json() as {answer:string;source:string};
      if(typeof data.answer!=='string'||typeof data.source!=='string')throw Error('The guide returned an unexpected response.');
      if(!controller.signal.aborted)setReply({...data,question:text,context:attached?`${page} · ${attached.label}`:context});
    }catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Guide unavailable.');}
    finally{if(request.current===controller){request.current=null;setBusy(false)}}
  }
  useEffect(()=>{setSelection(null)},[page]);
  useEffect(()=>{
    function receive(event:Event){const attached=(event as CustomEvent<LensContext>).detail;if(!attached)return;setOpen(true);if(request.current)return;
      const prompt='Explain this selection, its meaning, and any important limitations.';setSelection(attached);setQuestion(prompt);setOptionsOpen(false);void ask(undefined,attached,prompt);
    }
    window.addEventListener(LENS_EVENT,receive);return()=>window.removeEventListener(LENS_EVENT,receive);
  });
  return <div className="guide-widget"><SelectionLens page={page} busy={busy} remote={remote}/>
    {open&&<aside id={`${id}-drawer`} className="guide-drawer guide-panel" aria-labelledby={`${id}-title`} onKeyDown={e=>{if(e.key==='Escape'){e.stopPropagation();close()}}}>
      <header className="guide-panel-head">
        <div className="guide-brand"><div className="guide-avatar"><AxiomMark small/></div><div><h2 id={`${id}-title`} ref={heading} tabIndex={-1}>AXIOM Guide</h2><p>Research assistant</p></div></div>
        <button className="guide-close" type="button" onClick={close} aria-label="Close guide">×</button>
      </header>
      <form className="guide-form" onSubmit={ask}>
        <div className="guide-scroll">
          <div className="guide-context-row"><span className="guide-context-tag" title={page}><i aria-hidden="true"/>{page}</span><span className="guide-mode-tag">{remote?'External AI opted in':'Local guide'}</span></div>
          {selection&&<section className="lens-attached" aria-label="Attached selection"><div><strong>AXIOM Lens · {selection.kind}</strong><button type="button" disabled={busy} onClick={()=>setSelection(null)} aria-label="Remove selected context">×</button></div><small>{selection.label}</small><p>{selection.excerpt}</p><small>{remote?'External AI receives this selected excerpt.':'Local guidance only · excerpt is not sent to a provider.'}</small><div className="lens-followups">{[['Teach me','Teach me the concept behind this selection in simple steps.'],['Reliability','Explain the assumptions and limitations of this selection.'],['Next step','Suggest an appropriate next analytical step for this selection.']].map(([label,prompt])=><button key={label} type="button" disabled={busy} onClick={()=>{setQuestion(prompt);void ask(undefined,selection,prompt)}}>{label}</button>)}</div></section>}
          <section className="guide-suggestions" aria-label="Quick questions"><div className="guide-section-heading"><h3>Explore a topic</h3><small>Instant local help</small></div><div className="guide-topics">{topics.map((t,i)=><button style={{'--guide-order':i} as CSSProperties} key={t.question} type="button" disabled={busy} onClick={()=>{setSelection(null);setQuestion(t.question);setReply({answer:t.answer,source:'Built-in guide',question:t.question,context:'General guidance'});setError('')}}><span>{t.title}</span><Arrow/></button>)}</div></section>
          {(reply||busy||error)&&<div className="guide-response" ref={response} aria-live="polite" aria-atomic="true">
            {busy&&<div className="guide-thinking" role="status"><div><AxiomMark small/><span>Preparing your explanation<small>{remote?'Checking the optional provider':'Using local scientific guidance'}</small></span></div><i/><i/><i/></div>}
            {error&&<div className="guide-response-error" role="alert"><strong>Couldn't complete this request</strong><p>{error}</p><small>Your question is preserved. Use Ask AXIOM to retry manually, or check System checks.</small></div>}
            {reply&&<article className="guide-answer"><div className="guide-answer-top"><AxiomMark small/><span>{reply.source}</span></div><h3>{reply.question}</h3><p>{reply.answer}</p><small>Context: {reply.context}</small></article>}
          </div>}
          <div className="guide-composer"><div className="guide-section-heading"><label htmlFor={`${id}-question`}>Ask about your research</label><small>{question.length}/500</small></div><textarea id={`${id}-question`} ref={questionInput} rows={2} maxLength={500} value={question} disabled={busy} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();if(canAsk)void ask()}}} placeholder="What does this result mean?"/><small>Enter to send · Shift + Enter for a new line</small></div>
          <details className="guide-options" open={optionsOpen} onToggle={e=>setOptionsOpen(e.currentTarget.open)}><summary><span>Context &amp; AI settings</span><small>{selectedColumn?'Metric attached':remote?'External enabled':'Optional'}</small></summary><div className="guide-options-body">
            {!!datasetId&&numericColumns.length>0&&<label className="guide-select">Attach numeric context<select disabled={busy} value={selectedColumn} onChange={e=>setColumn(e.target.value)}><option value="">Dataset overview only</option>{numericColumns.map(c=><option key={c}>{c}</option>)}</select><small>Attach summary statistics for one column.</small></label>}
            <label className="guide-opt-in"><span><strong>Use external AI</strong><small>Sends your question, workspace, structural summary and selected aggregate statistics to the configured provider. Lens also sends any explicitly selected text or point, which may contain a raw value. No automatic raw-row upload. Do not select or enter private information.</small></span><input type="checkbox" checked={remote} disabled={busy} onChange={e=>setRemote(e.target.checked)}/></label>
            <small>Off by default. If unavailable, the guide can return local guidance.</small>
          </div></details>
        </div>
        <footer className="guide-footer"><div className="guide-footer-actions"><button type="button" className="guide-clear" onClick={clear} disabled={busy||(!question&&!reply&&!error)}>Clear</button><button type="submit" className="primary-button guide-send" disabled={!canAsk}>{busy?<><AxiomMark small/>Explaining…</>:<>Ask AXIOM<Arrow up/></>}</button></div><small>Guidance only · verified calculations remain the source of truth.</small></footer>
      </form>
    </aside>}
    <button ref={launcher} type="button" className="guide-launch" data-busy={busy} aria-expanded={open} aria-controls={open?`${id}-drawer`:undefined} aria-label={open?'Close AXIOM Guide':'Open AXIOM Guide'} onClick={()=>open?close():setOpen(true)}><AxiomMark small/>{open?'Close':'Ask AXIOM'}</button>
  </div>;
}
