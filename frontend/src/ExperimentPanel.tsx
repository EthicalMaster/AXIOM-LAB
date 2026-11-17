import { useState, type FormEvent } from 'react';
import { coordinates, reopenExperiment, saveExperiment, type SavedExperiment } from './experiments';

export function ExperimentPanel({ datasetId, numericColumns }: {datasetId:string; numericColumns:string[]}) {
  const [name,setName] = useState('Observation study');
  const [column,setColumn] = useState(numericColumns[0] ?? '');
  const [working,setWorking] = useState(false);
  const [saved,setSaved] = useState<SavedExperiment | null>(null);
  const [error,setError] = useState<string | null>(null);
  const selected = numericColumns.includes(column) ? column : (numericColumns[0] ?? '');
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); if(!selected || !name.trim() || working) return;
    setWorking(true); setError(null);
    try { setSaved(await saveExperiment(datasetId,selected,name.trim())); }
    catch(e) { setError(e instanceof Error ? e.message : 'Failed to save experiment'); }
    finally { setWorking(false); }
  }
  async function reload() {
    if(!saved) return;
    setWorking(true); setError(null);
    try {setSaved(await reopenExperiment(saved.id));}
    catch(e) {setError(e instanceof Error?e.message:'Could not reload');}
    finally {setWorking(false);}
  }
  const chart = saved?.run.result;
  return <section className="science-panel" aria-labelledby="experiment-title">
    <div className="preview-heading"><h3 id="experiment-title">Experiment &amp; visualization</h3><span>PHASE 01D · PERSISTENT RUN</span></div>
    <p className="profile-description">Create a numerical observation-sequence chart and save a run. This is not a time series: the horizontal axis is the observation index.</p>
    {numericColumns.length ? <form className="experiment-controls" onSubmit={submit}>
      <label>Experiment name<input value={name} maxLength={120} onChange={e=>setName(e.target.value)} required/></label>
      <label>Numeric column<select value={selected} onChange={e=>setColumn(e.target.value)}>{numericColumns.map(c=><option key={c} value={c}>{c}</option>)}</select></label>
      <button type="submit" className="primary-button" disabled={working || !name.trim()}>{working?'Working…':'Compute & save run'} <span aria-hidden="true">↗</span></button>
    </form> : <p className="preview-note">No numeric column available for charting.</p>}
    {error && <p className="inline-alert error" role="alert">{error}</p>}
    {chart && <div className="chart-card">
      <div className="chart-meta"><strong>{saved?.name}</strong><span>{chart.original_point_count} observations · {chart.sampled?'250 selected data points':'All points shown'}</span></div>
      <svg role="img" aria-label={`${chart.column} against valid observation index, ${chart.shown_point_count} points`} viewBox="0 0 720 230" preserveAspectRatio="xMidYMid meet">
        <path d="M36 12V202H700" stroke="#6c7779" fill="none" strokeWidth="1"/>
        <polyline points={coordinates(chart.points)} fill="none" stroke="#d5bf9a" strokeWidth="2" vectorEffect="non-scaling-stroke"/>
        {chart.points.length<=80 && chart.points.map(p=><circle key={p.x} cx={36+(p.x-chart.points[0].x)/(chart.points[chart.points.length-1].x-chart.points[0].x||1)*664} cy={202-(p.y-Math.min(...chart.points.map(q=>q.y)))/(Math.max(...chart.points.map(q=>q.y))-Math.min(...chart.points.map(q=>q.y))||1)*180} r="3" fill="#e6d6ba"/>)}
      </svg>
      <p className="preview-note">{chart.x_label} · {chart.y_label}. {chart.note}</p>
      <p className="preview-note"><strong>Experiment:</strong> <code>{saved?.id}</code> · <strong>Run:</strong> <code>{saved?.run.id}</code></p>
      <button type="button" className="retry-button" onClick={()=>void reload()} disabled={working}>Reload saved run from storage</button>
    </div>}
  </section>;
}
