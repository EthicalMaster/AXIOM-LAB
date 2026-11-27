import {useState} from 'react';
type Entry={id:string;name:string;created_at:string;run_count:number;dataset_id:string};
type Page={total:number;items:Entry[]};
type Runs={total:number;items:{id:string;method:string;status:string;created_at:string}[]};
export function HistoryPanel(){
  const [page,setPage]=useState<Page|null>(null);const [runs,setRuns]=useState<Runs|null>(null);
  const [chosen,setChosen]=useState('');const [error,setError]=useState('');
  async function refresh(){setError('');setRuns(null);setChosen('');
    try{const r=await fetch('/api/v1/experiments?limit=20&offset=0');if(!r.ok)throw Error(`HTTP ${r.status}`);setPage(await r.json() as Page);}
    catch(e){setError(e instanceof Error?e.message:'History unavailable');}
  }
  async function inspect(id:string){setChosen(id);setRuns(null);setError('');
    try{const r=await fetch(`/api/v1/experiments/${encodeURIComponent(id)}/runs`);if(!r.ok)throw Error(`HTTP ${r.status}`);setRuns(await r.json() as Runs);}
    catch(e){setError(e instanceof Error?e.message:'Runs unavailable');}
  }
  return <section className="science-panel" aria-labelledby="history-title"><div className="preview-heading"><h3 id="history-title">Saved experiment history</h3><span>PHASE 05A · LOCAL HISTORY</span></div>
    <p className="profile-description">Read-only, paginated history of saved experiments and run IDs. Local single-user storage; accounts and access controls are not yet implemented.</p>
    <button className="retry-button" type="button" onClick={()=>void refresh()}>Load recent experiments</button>
    {error&&<p className="inline-alert error" role="alert">{error}</p>}
    {page&&<><p>{page.total} saved experiments · displaying latest {page.items.length}</p>
      <ul>{page.items.map(e=><li key={e.id}><button className="retry-button" onClick={()=>void inspect(e.id)}>{e.name} · {e.run_count} runs · {e.created_at}</button></li>)}</ul></>}
    {runs&&<div><p>Selected experiment: <code>{chosen}</code> · {runs.total} runs</p>
      <ul>{runs.items.map(r=><li key={r.id}><code>{r.id}</code> · {r.status} · {r.method}</li>)}</ul></div>}
  </section>;
}
