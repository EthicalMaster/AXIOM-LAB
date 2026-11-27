import {Metrics} from './Visuals';
import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import { useEffect, useState } from 'react';
type Diagnostic = { n:number; p_value:number|null; statistic:number|null; status:string; warnings:string[]; note:string };
export function DiagnosticsPanel({datasetId,numericColumns}:{datasetId:string;numericColumns:string[]}) {
  const [column,setColumn]=useState('');
  const [result,setResult]=useState<Diagnostic|null>(null);
  const [error,setError]=useState('');
  const selected=numericColumns.includes(column)?column:(numericColumns[0]??'');
  useEffect(()=>{
    if(!selected) return;
    const controller=new AbortController();setResult(null);setError('');
    void apiFetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/diagnostics?column=${encodeURIComponent(selected)}`,{signal:controller.signal})
      .then(async r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return await r.json() as Diagnostic;})
      .then(setResult).catch(e=>{if((e as Error).name!=='AbortError')setError('Diagnostics unavailable: '+String(e));});
    return ()=>controller.abort();
  },[datasetId,selected]);
  return <section className="science-panel" aria-labelledby="diagnostic-title"><div className="preview-heading"><h3 id="diagnostic-title">Statistical diagnostics</h3><span>PHASE 02D · SHAPIRO-WILK</span></div>
    <p className="profile-description">Normality diagnostic only. It cannot establish independence, representativeness or validity of a hypothesis test.</p>
    {numericColumns.length>0?<label>Numeric column <select value={selected} onChange={e=>setColumn(e.target.value)}>{numericColumns.map(c=><option key={c}>{c}</option>)}</select></label>:<p>No numeric column available.</p>}
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {selected&&!result&&!error&&<Loading label="Checking normality"/>}{result&&<><Metrics items={[{label:"Observations",value:result.n},{label:"Shapiro–Wilk W",value:result.statistic},{label:"p-value",value:result.p_value}]}/><p>Result: <strong>{result.status}</strong>{result.p_value!==null?` · W=${result.statistic?.toFixed(4)} · p=${result.p_value.toPrecision(4)}`:''}</p><p className="preview-note">{result.note}</p><ul>{result.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></>}
  </section>;
}
