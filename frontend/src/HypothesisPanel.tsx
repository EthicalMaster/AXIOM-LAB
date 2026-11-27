import {Interval,Metrics} from './Visuals';
import {Loading} from './WorkspaceTools';
import {apiFetch} from './apiClient';
import { useState, type FormEvent } from 'react';

type TestResult = { null_mean:number; n: number; sample_mean: number; t_statistic: number; degrees_of_freedom: number; p_value: number; alpha: number; confidence_interval: number[]; cohens_d: number; reject_null: boolean; warnings: string[]; note: string };
export function HypothesisPanel({ datasetId, numericColumns }: {datasetId: string; numericColumns: string[]}) {
  const [column,setColumn]=useState('');
  const [mu,setMu]=useState('0');
  const [result,setResult]=useState<TestResult|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const selected=numericColumns.includes(column)?column:(numericColumns[0]??'');
  async function run(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();setResult(null);setError('');setBusy(true);
    try {
      const response=await apiFetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/hypothesis`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({column:selected,null_mean:Number(mu),alpha:0.05})
      });
      setResult(await response.json() as TestResult);
    } catch(e) {setError(e instanceof Error?e.message:'Test failed');}
    finally {setBusy(false);}
  }
  return <section className="science-panel" aria-labelledby="hypothesis-title">
    <div className="preview-heading"><h3 id="hypothesis-title">Hypothesis testing</h3><span>PHASE 02C · ONE-SAMPLE T-TEST</span></div>
    <p className="profile-description">A two-sided test of whether a population mean differs from a specified value. Requires independent observations and an appropriate distribution.</p>
    {numericColumns.length>0?<form className="experiment-controls" onSubmit={run}>
      <label>Numeric column<select value={selected} onChange={e=>setColumn(e.target.value)}>{numericColumns.map(c=><option key={c}>{c}</option>)}</select></label>
      <label>Null mean<input type="number" step="any" required value={mu} onChange={e=>setMu(e.target.value)}/></label>
      <button className="primary-button" disabled={busy||!selected||mu.trim()===''}>{busy?'Testing…':'Run two-sided t-test'}</button>
    </form>:<p>No numeric columns available.</p>}
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {busy&&<Loading label="Testing reference mean"/>}{result&&<><Metrics items={[{label:"Sample mean",value:result.sample_mean},{label:"p-value",value:result.p_value},{label:"Effect size (d)",value:result.cohens_d}]}/><Interval label="95% confidence interval" low={result.confidence_interval[0]} high={result.confidence_interval[1]} center={result.sample_mean} reference={result.null_mean}/><div className="distribution-summary"><span>n <strong>{result.n}</strong></span><span>t <strong>{result.t_statistic.toFixed(4)}</strong></span><span>p <strong>{result.p_value.toPrecision(4)}</strong></span><span>95% CI <strong>{result.confidence_interval.map(v=>v.toFixed(3)).join(' to ')}</strong></span></div>
      <p className="preview-note">{result.reject_null?'Reject':'Do not reject'} H₀ at α={result.alpha}. {result.note}</p><ul>{result.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></>}
  </section>;
}
