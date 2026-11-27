import {useState} from 'react';
type Entry={id:string;name:string;created_at:string;run_count:number;dataset_id:string};
type Page={total:number;items:Entry[]};
type Runs={total:number;items:{id:string;method:string;status:string;created_at:string;revision:number;configuration:{column?:string}}[]};
export function HistoryPanel(){
  const [page,setPage]=useState<Page|null>(null);const [runs,setRuns]=useState<Runs|null>(null);
  const [chosen,setChosen]=useState('');const [error,setError]=useState('');
  const [comparison,setComparison]=useState<Record<string,unknown>|null>(null);
  const [explanation,setExplanation]=useState<Record<string,unknown>|null>(null);
  async function refresh(){setError('');setRuns(null);setChosen('');setComparison(null);
    try{const r=await fetch('/api/v1/experiments?limit=20&offset=0');if(!r.ok)throw Error(`HTTP ${r.status}`);setPage(await r.json() as Page);}
    catch(e){setError(e instanceof Error?e.message:'History unavailable');}
  }
  async function inspect(id:string){setChosen(id);setRuns(null);setError('');setComparison(null);
    try{const r=await fetch(`/api/v1/experiments/${encodeURIComponent(id)}/runs`);if(!r.ok)throw Error(`HTTP ${r.status}`);setRuns(await r.json() as Runs);}
    catch(e){setError(e instanceof Error?e.message:'Runs unavailable');}
  }
  async function rerun(){
    const column=runs?.items[0]?.configuration.column;
    if(!column || !chosen)return;
    setError('');
    try{
      const response=await fetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/runs`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({column})
      });
      if(!response.ok)throw Error(`Run could not be saved (HTTP ${response.status})`);
      await inspect(chosen);
    }catch(e){setError(e instanceof Error?e.message:'Run not saved');}
  }
  async function compare(){
    if(!chosen||!runs||runs.items.length<2)return;
    const [a,b]=runs.items;
    try{
      const response=await fetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/compare?left=${encodeURIComponent(a.id)}&right=${encodeURIComponent(b.id)}`);
      if(!response.ok)throw Error(`Comparison failed (HTTP ${response.status})`);
      setComparison(await response.json() as Record<string,unknown>);
    }catch(e){setError(e instanceof Error?e.message:'Comparison unavailable');}
  }
  async function reproduce(){
    const latest=runs?.items[0];
    if(!chosen||!latest)return;
    setError('');
    try{
      const response=await fetch(`/api/v1/experiments/${encodeURIComponent(chosen)}/runs/${encodeURIComponent(latest.id)}/reproduce`,{method:'POST'});
      if(!response.ok)throw Error(`Reproduction failed (HTTP ${response.status})`);
      const report=await response.json() as {exact_result_match:boolean};
      await inspect(chosen);
      if(!report.exact_result_match)setError('Warning: the reproduced numerical result differs from the saved result.');
    }catch(e){setError(e instanceof Error?e.message:'Reproduction unavailable');}
  }
  async function explain(){
    const latest=runs?.items[0];
    if(!chosen||!latest)return;
    setError('');setExplanation(null);
    try{
      const response=await fetch('/api/v1/ai/explain',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({experiment_id:chosen,run_id:latest.id})});
      if(!response.ok)throw Error(`Explanation failed (HTTP ${response.status})`);
      setExplanation(await response.json() as Record<string,unknown>);
    }catch(e){setError(e instanceof Error?e.message:'Explanation unavailable');}
  }
  return <section className="science-panel" aria-labelledby="history-title"><div className="preview-heading"><h3 id="history-title">Saved experiment history</h3><span>PHASE 05A–07A · RECORDED EVIDENCE</span></div>
    <p className="profile-description">Append-only, paginated history of saved experiments and runs. Optional single-user access protection is available; independent user accounts and dataset isolation are not.</p>
    <button className="retry-button" type="button" onClick={()=>void refresh()}>Load recent experiments</button>
    {error&&<p className="inline-alert error" role="alert">{error}</p>}
    {page&&<><p>{page.total} saved experiments · displaying latest {page.items.length}</p>
      <ul>{page.items.map(e=><li key={e.id}><button className="retry-button" onClick={()=>void inspect(e.id)}>{e.name} · {e.run_count} runs · {e.created_at}</button></li>)}</ul></>}
    {runs&&<div><p>Selected experiment: <code>{chosen}</code> · {runs.total} runs</p>
      <button className="retry-button" disabled={!runs.items[0]?.configuration.column} onClick={()=>void rerun()}>Repeat most recent run as new version</button>
      <button className="retry-button" disabled={!runs.items.length} onClick={()=>void reproduce()}>Reproduce latest run</button>
      <button className="retry-button" disabled={!runs.items.length} onClick={()=>void explain()}>Explain recorded evidence</button>
      {explanation&&<pre className="table-scroll" aria-label="Verified evidence and advisory explanation">{JSON.stringify(explanation,null,2)}</pre>}
      <button className="retry-button" disabled={runs.items.length<2} onClick={()=>void compare()}>Compare two latest runs</button>
      {comparison&&<pre className="table-scroll" aria-label="Run comparison">{JSON.stringify(comparison,null,2)}</pre>}
      <ul>{runs.items.map(r=><li key={r.id}><code>{r.id}</code> · Revision {r.revision} · {r.status} · {r.method}
        <span> · </span>{(['pdf','csv','json'] as const).map(ext=><a key={ext} className="retry-button" href={`/api/v1/experiments/${chosen}/runs/${r.id}/report?format=${ext}`} download>Export {ext.toUpperCase()}</a>)}
      </li>)}</ul></div>}
  </section>;
}
