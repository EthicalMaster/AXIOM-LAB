import {Details,Metrics} from './Visuals';
import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import {useState} from 'react';
type Entry={id:string;name:string;created_at:string;run_count:number;dataset_id:string};
type Page={total:number;items:Entry[]};
type Runs={total:number;items:{id:string;method:string;status:string;created_at:string;revision:number;configuration:{column?:string}}[]};
export function HistoryPanel(){
  const [busy,setBusy]=useState(false);
  const [page,setPage]=useState<Page|null>(null);const [runs,setRuns]=useState<Runs|null>(null);
  const [chosen,setChosen]=useState('');const [error,setError]=useState('');
  const [comparison,setComparison]=useState<Record<string,unknown>|null>(null);
  const [explanation,setExplanation]=useState<Record<string,unknown>|null>(null);
  async function refresh(){setBusy(true);setError('');setRuns(null);setChosen('');setComparison(null);setExplanation(null);
    try{const r=await apiFetch('/api/v1/experiments?limit=20&offset=0');setPage(await r.json() as Page);}
    catch(e){setError(e instanceof Error?e.message:'History unavailable');}finally{setBusy(false);}
  }
  async function inspect(id:string){setBusy(true);setChosen(id);setRuns(null);setError('');setComparison(null);setExplanation(null);
    try{const r=await apiFetch(`/api/v1/experiments/${encodeURIComponent(id)}/runs`);setRuns(await r.json() as Runs);}
    catch(e){setError(e instanceof Error?e.message:'Runs unavailable');}finally{setBusy(false);}
  }
  async function rerun(){
    const column=runs?.items[0]?.configuration.column;
    if(!column || !chosen)return;
    setBusy(true);setError('');
    try{
      await apiFetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/runs`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({column})
      });
      await inspect(chosen);
    }catch(e){setError(e instanceof Error?e.message:'Run not saved');}finally{setBusy(false);}
  }
  async function compare(){
    if(busy||!chosen||!runs||runs.items.length<2)return;
    setBusy(true);setError('');
    const [a,b]=runs.items;
    try{
      const response=await apiFetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/compare?left=${encodeURIComponent(a.id)}&right=${encodeURIComponent(b.id)}`);
      setComparison(await response.json() as Record<string,unknown>);
    }catch(e){setError(e instanceof Error?e.message:'Comparison unavailable');}finally{setBusy(false);}
  }
  async function reproduce(){
    const latest=runs?.items[0];
    if(!chosen||!latest)return;
    setBusy(true);setError('');
    try{
      const response=await apiFetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/runs/${encodeURIComponent(latest.id)}/reproduce`,{method:'POST'});
      const report=await response.json() as {exact_result_match:boolean};
      await inspect(chosen);
      if(!report.exact_result_match)setError('Warning: the reproduced numerical result differs from the saved result.');
    }catch(e){setError(e instanceof Error?e.message:'Reproduction unavailable');}finally{setBusy(false);}
  }
  async function explain(){
    const latest=runs?.items[0];
    if(!chosen||!latest)return;
    setBusy(true);setError('');setExplanation(null);
    try{
      const response=await apiFetch('/api/v1/ai/explain',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({experiment_id:chosen,run_id:latest.id})});
      setExplanation(await response.json() as Record<string,unknown>);
    }catch(e){setError(e instanceof Error?e.message:'Explanation unavailable');}finally{setBusy(false);}
  }
  return <section className="science-panel" aria-labelledby="history-title"><div className="preview-heading"><h3 id="history-title">Saved experiment history</h3><span>PHASE 05A–07A · RECORDED EVIDENCE</span></div>
    <p className="profile-description">Append-only, paginated history of saved experiments and runs. History is scoped to the current private workspace in multi-user beta mode.</p>
    <button className="retry-button" type="button" disabled={busy} onClick={()=>void refresh()}>Load recent experiments</button>
    {busy&&<Loading label="Working with saved evidence"/>}{error&&<p className="inline-alert error" role="alert">{error}</p>}
    {page&&<><p>{page.total} saved experiments · displaying latest {page.items.length}</p>
      <ul className="history-list">{page.items.map(e=><li key={e.id}><button className="retry-button" disabled={busy} onClick={()=>void inspect(e.id)}>{e.name} · {e.run_count} runs · {e.created_at}</button></li>)}</ul></>}
    {runs&&<div><p>Selected experiment: <code>{chosen}</code> · {runs.total} runs</p>
      <button className="retry-button" disabled={busy||!runs.items[0]?.configuration.column} onClick={()=>void rerun()}>Repeat most recent run as new version</button>
      <button className="retry-button" disabled={busy||!runs.items.length} onClick={()=>void reproduce()}>Reproduce latest run</button>
      <button className="retry-button" disabled={busy||!runs.items.length} onClick={()=>void explain()}>Explain recorded evidence</button>
      {explanation&&<div className="guide-answer"><span className="micro">{String(explanation.source)}</span><p>{String(explanation.explanation)}</p><Details title="Verified evidence"><pre>{JSON.stringify(explanation.evidence,null,2)}</pre></Details></div>}
      <button className="retry-button" disabled={busy||runs.items.length<2} onClick={()=>void compare()}>Compare two latest runs</button>
      {comparison&&<div><Metrics items={[{label:"Comparable",value:comparison.comparable?"Yes":"No"},...Object.entries((comparison.comparison??{}) as Record<string,unknown>).map(([label,value])=>({label:label.replaceAll("_"," "),value}))]}/>{Array.isArray(comparison.warnings)&&<p>{comparison.warnings.map(String).join(" ")}</p>}<Details title="Comparison evidence"><pre>{JSON.stringify(comparison,null,2)}</pre></Details></div>}
      <ul className="history-list">{runs.items.map(r=><li key={r.id}><code>{r.id}</code> · Revision {r.revision} · {r.status} · {r.method}
        <span> · </span>{(['pdf','csv','json'] as const).map(ext=><a key={ext} className="retry-button" href={`/api/v1/experiments/${chosen}/runs/${r.id}/report?format=${ext}`} download>Export {ext.toUpperCase()}</a>)}
      </li>)}</ul></div>}
  </section>;
}
