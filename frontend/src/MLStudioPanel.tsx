import {MLResult} from './MLResult';
import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import {useState} from 'react';
type Task = 'regression'|'classification';
type Output = Record<string,unknown>;
export function MLStudioPanel({datasetId,numericColumns,targetColumns}:{datasetId:string;numericColumns:string[];targetColumns:string[]}){
  const [task,setTask]=useState<Task>('regression');
  const [feature,setFeature]=useState('');const [target,setTarget]=useState('');
  const [report,setReport]=useState<Output|null>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
  const candidateTargets=task==='regression'?numericColumns:targetColumns;
  const actualTarget=candidateTargets.includes(target)?target:(candidateTargets[0]??'');
  const actualFeature=numericColumns.includes(feature)&&feature!==actualTarget?feature:(numericColumns.find(f=>f!==actualTarget)??'');
  async function run(operation:string){
    setError('');setReport(null);setBusy(true);
    try{
      const r=await apiFetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/ml/${operation}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task,features:[actualFeature],target:actualTarget,time_dependent:false})
      });
      if(!r.ok)throw Error(`ML request rejected (HTTP ${r.status}).`);
      setReport(await r.json() as Output);
    }catch(e){setError(e instanceof Error?e.message:'Model execution failed');}
    finally{setBusy(false);}
  }
  return <section className="science-panel" aria-labelledby="ml-title"><div className="preview-heading"><h3 id="ml-title">Machine Learning Studio</h3><span>PHASE 04A · TRAIN-ONLY PREPROCESSING</span></div>
    <p className="profile-description">Bounded CPU-only experiments. Explicit 75/25 holdout. Time-dependent and dependent/grouped observations are not supported yet.</p>
    <div className="experiment-controls"><label>Task <select value={task} onChange={e=>{setTask(e.target.value as Task);setTarget('');setReport(null);}}><option value="regression">Regression</option><option value="classification">Classification</option></select></label>
      <label>Numeric predictor <select value={actualFeature} onChange={e=>setFeature(e.target.value)}>{numericColumns.filter(c=>c!==actualTarget).map(c=><option key={c}>{c}</option>)}</select></label>
      <label>Target <select value={actualTarget} onChange={e=>setTarget(e.target.value)}>{candidateTargets.map(c=><option key={c}>{c}</option>)}</select></label>
      <button className="primary-button" disabled={busy||!actualFeature||!actualTarget} onClick={()=>void run('preview')}>Preview training split</button>
      {task==='regression'&&<button className="primary-button" disabled={busy||!actualFeature||!actualTarget} onClick={()=>void run('regression')}>Train linear regression</button>}
      {task==='classification'&&<button className="primary-button" disabled={busy||!actualFeature||!actualTarget} onClick={()=>void run('classification')}>Train classifier</button>}
      <button className="primary-button" disabled={busy||!actualFeature||!actualTarget} onClick={()=>void run('compare')}>Compare two baselines</button>
    </div>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {busy&&<Loading label="Fitting and evaluating model"/>}{report&&<MLResult report={report}/>}
  </section>;
}
