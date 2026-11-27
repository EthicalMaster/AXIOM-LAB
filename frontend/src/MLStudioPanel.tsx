import {MLResult} from './MLResult';
import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import {useState} from 'react';
export type Task='regression'|'classification';
export function MLStudioPanel({datasetId,numericColumns,targetColumns,task}:{datasetId:string;numericColumns:string[];targetColumns:string[];task:Task}){
 const [features,setFeatures]=useState<string[]>([]),[target,setTarget]=useState('');
 const [report,setReport]=useState<Record<string,unknown>|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const classification=task==='classification';
 const targets=classification?targetColumns:numericColumns;
 const actualTarget=targets.includes(target)?target:targets[0]??'';
 const choices=numericColumns.filter(c=>c!==actualTarget);
 const selected=features.filter(c=>choices.includes(c));
 const actualFeatures=features.length===0&&choices.length?[choices[0]]:selected;
 const canTrain=!!actualTarget&&actualFeatures.length>0&&!busy;
 function reset(){setReport(null);setError('')}
 async function run(operation:string){if(!canTrain)return;setBusy(true);reset();try{
  const r=await apiFetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/ml/${operation}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task,features:actualFeatures,target:actualTarget,time_dependent:false})});setReport(await r.json() as Record<string,unknown>);
 }catch(e){setError(e instanceof Error?e.message:'Model execution failed')}finally{setBusy(false)}}
 return <section className="science-panel ml-workflow" aria-labelledby="ml-title"><div className="preview-heading"><h3 id="ml-title">{classification?'Classification · logistic regression':'Regression · linear baseline'}</h3><span>SUPERVISED LEARNING</span></div>
 <p className="profile-description">{classification?'Learn from labeled examples and predict a category. Example: classify an item as pass or fail using measured features.':'Learn the relationship between measured variables and a numeric outcome. Example: estimate energy demand from independent observations.'}</p>
 {!targets.length?<div className="lab-empty"><strong>No eligible target column</strong><p>{classification?'Classification requires a text category or boolean label. This dataset contains no such column.':'Regression requires a numeric outcome.'}</p><a className="retry-button" href="/examples/ml-demo.csv" download>Download practice dataset ↓</a></div>:!choices.length?<div className="lab-empty">Import a dataset with at least one numeric predictor separate from the target.</div>:<>
 <fieldset disabled={busy} className="ml-fields"><legend>Configure model</legend><label>Target · outcome to predict<select value={actualTarget} onChange={e=>{setTarget(e.target.value);setFeatures([]);reset()}}>{targets.map(c=><option key={c}>{c}</option>)}</select></label><div><span className="input-label">Predictors · choose 1–8 numeric features</span><div className="feature-options">{choices.map(c=><label key={c}><input type="checkbox" checked={actualFeatures.includes(c)} disabled={actualFeatures.length>=8&&!actualFeatures.includes(c)} onChange={e=>{const next=e.target.checked?[...actualFeatures,c]:actualFeatures.filter(x=>x!==c);if(next.length){setFeatures(next);reset()}}}/>{c}</label>)}</div></div></fieldset>
 <div className="lab-actions"><button type="button" className="primary-button" disabled={!canTrain} onClick={()=>void run(task)}>{classification?'Train classifier':'Train regression'} <span aria-hidden="true">↗</span></button><button type="button" className="retry-button" disabled={!canTrain} onClick={()=>void run('preview')}>Preview training split</button><button type="button" className="retry-button" disabled={!canTrain} onClick={()=>void run('compare')}>Compare baselines</button></div>
 <details className="lab-details"><summary>Requirements and interpretation</summary><p>16–2,000 labeled observations, independent rows and a separate target. Training-only preprocessing with 75/25 holdout. {classification?'2–8 classes with at least 4 observations per class and sufficient test rows. Inspect confusion matrix and macro F1, not only accuracy.':'Inspect held-out MAE, RMSE and R². A prediction relationship is not causal evidence.'} Time-series and grouped samples are not supported. This is a research evaluation tool, not a deployed prediction service.</p></details></>}
 {error&&<p role="alert" className="inline-alert error">{error}</p>}{busy&&<Loading label="Fitting and evaluating model"/>}{report&&<MLResult report={report}/>}
 </section>
}
