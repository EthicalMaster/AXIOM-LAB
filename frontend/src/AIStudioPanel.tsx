import {useState} from 'react';
type Status={enabled:boolean;model:string|null;reason:string};
export function AIStudioPanel({datasetId}:{datasetId?:string}){
  const [goal,setGoal]=useState('describe');
  const [guidance,setGuidance]=useState<Record<string,unknown>|null>(null);
  const [status,setStatus]=useState<Status|null>(null);
  const [error,setError]=useState('');
  async function refresh(){
    setError('');
    try{const res=await fetch('/api/v1/ai/status');if(!res.ok)throw Error(`HTTP ${res.status}`);setStatus(await res.json() as Status);}
    catch(e){setError(e instanceof Error?e.message:'AI status unavailable');}
  }
  async function recommend(){
    if(!datasetId)return;
    setError('');setGuidance(null);
    try{
      const res=await fetch('/api/v1/ai/guidance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dataset_id:datasetId,goal})});
      if(!res.ok)throw Error(`Guidance failed (HTTP ${res.status})`);
      setGuidance(await res.json() as Record<string,unknown>);
    }catch(e){setError(e instanceof Error?e.message:'Guidance unavailable');}
  }
  return <section className="science-panel" aria-labelledby="ai-title">
    <div className="preview-heading"><h3 id="ai-title">Scientific assistant</h3><span>PHASE 06A–06C · GROUNDED ADVICE</span></div>
    <p className="profile-description">Scientific calculations never depend on an AI subscription. AI commentary is optional, bounded, and separate from verified numerical evidence.</p>
    <button type="button" className="retry-button" onClick={()=>void refresh()}>Check provider status</button>
    {datasetId&&<div className="experiment-controls"><label>Research goal
      <select value={goal} onChange={e=>setGoal(e.target.value)}><option value="describe">Describe data</option><option value="distribution">Examine distributions</option><option value="mean_test">Test a reference mean</option><option value="prediction">Predict outcomes</option></select>
    </label><button type="button" className="primary-button" onClick={()=>void recommend()}>Suggest grounded methods</button></div>}
    {guidance&&<pre className="table-scroll" aria-label="Method guidance">{JSON.stringify(guidance,null,2)}</pre>}
    {status&&<p role="status">{status.enabled?`Advisory model: ${status.model}`:status.reason}</p>}
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
  </section>;
}
