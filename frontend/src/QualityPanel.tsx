import { useEffect, useState } from 'react';
import { fetchQuality, percent, type QualityReport } from './quality';

export function QualityPanel({datasetId}:{datasetId:string}) {
  const [data,setData]=useState<QualityReport|null>(null);
  const [error,setError]=useState<string|null>(null);
  useEffect(()=>{
    let active=true;setData(null);setError(null);
    void fetchQuality(datasetId).then(result=>{if(active)setData(result);})
      .catch(e=>{if(active)setError(e instanceof Error?e.message:'Quality check failed');});
    return ()=>{active=false;};
  },[datasetId]);
  return <section className="science-panel" aria-labelledby="quality-title">
    <div className="preview-heading"><h3 id="quality-title">Data quality audit</h3><span>PHASE 02A · NO CLEANING</span></div>
    <p className="profile-description">Checks missing cells and exact duplicate rows without modifying or deleting anything. Duplicate measurements may be scientifically legitimate.</p>
    {error && <p className="inline-alert error" role="alert">{error}</p>}
    {!data&&!error&&<p role="status" className="profile-status">Auditing original rows…</p>}
    {data&&<>
      <div className="quality-metrics"><div><span>COMPLETENESS</span><strong>{percent(data.completeness_percent)}</strong></div><div><span>MISSING CELLS</span><strong>{data.missing_cells}</strong></div><div><span>REPEATED ROWS</span><strong>{data.duplicate_count_exact?'':'>='}{data.duplicate_rows}</strong></div></div>
      <div className="quality-columns">{data.columns.map(c=><div key={c.column} className="quality-row">
        <span>{c.column}</span><div className="quality-track" aria-label={`${percent(c.missing_percent)} missing in ${c.column}`}><span style={{width:`${Math.max(0,Math.min(100,c.missing_percent))}%`}}/></div><strong>{percent(c.missing_percent)} missing</strong>
      </div>)}</div>
      {data.warnings.length>0&&<div className="warning-panel profile-warnings" role="note"><strong>Audit notes</strong><ul>{data.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></div>}
      <p className="preview-note">{data.note} {data.duplicate_count_exact?'Duplicate count exact under the tracking cap.':'Duplicate count is a lower bound.'}</p>
    </>}
  </section>;
}
