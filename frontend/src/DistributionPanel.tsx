import {BoxPlot,Details,XYPlot} from './Visuals';
import {Loading} from './WorkspaceTools';
import { useEffect, useState } from 'react';
import { fetchDistribution, type DistributionReport } from './distribution';
import { displayNumber } from './statistics';

export function DistributionPanel({datasetId,numericColumns}:{datasetId:string;numericColumns:string[]}) {
  const [column,setColumn]=useState(numericColumns[0]??'');
  const [report,setReport]=useState<DistributionReport|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [loading,setLoading]=useState(false);
  const selected=numericColumns.includes(column)?column:(numericColumns[0]??'');
  useEffect(()=>{
    if(!selected) {setReport(null);return;}
    let active=true;setLoading(true);setReport(null);setError(null);
    void fetchDistribution(datasetId,selected).then(r=>{if(active)setReport(r);})
      .catch(e=>{if(active)setError(e instanceof Error?e.message:'Distribution unavailable');})
      .finally(()=>{if(active)setLoading(false);});
    return ()=>{active=false;};
  },[datasetId,selected]);
  return <section className="science-panel" aria-labelledby="distribution-title">
    <div className="preview-heading"><h3 id="distribution-title">Distribution explorer</h3><span>PHASE 02B · HISTOGRAM</span></div>
    <p className="profile-description">Equal-width count bins (Sturges heuristic, up to 20). Numeric observations only; chart represents frequency, not a fitted probability distribution.</p>
    {numericColumns.length>0?<label className="distribution-picker">Numeric column <select value={selected} onChange={e=>setColumn(e.target.value)}>{numericColumns.map(c=><option value={c} key={c}>{c}</option>)}</select></label>:<p className="preview-note">No consistently numeric columns available.</p>}
    {loading&&<Loading label="Calculating frequency bins"/>}
    {error&&<div className="inline-alert error" role="alert">{error}</div>}
    {report&&<>
      <XYPlot points={[]} bins={report.bins} label={`Frequency · ${report.column}`} xLabel={report.column} yLabel="Count"/>
      <div className="distribution-summary"><span><strong>{report.count}</strong> observations</span><span><strong>{report.missing_count}</strong> missing</span><span><strong>{displayNumber(report.median)}</strong> median</span><span><strong>{report.outlier_count===null?'N/A':report.outlier_count}</strong> outlier indicators</span></div>
      <BoxPlot label={report.column} min={report.minimum} max={report.maximum} q1={report.q1} q3={report.q3} median={report.median}/><Details title="Exact frequency table"><div className="table-scroll" tabIndex={0} aria-label="Exact distribution frequency table">
        <table className="data-table"><thead><tr><th scope="col">Bin</th><th scope="col">Lower bound</th><th scope="col">Upper bound</th><th scope="col">Count</th><th scope="col">Share</th></tr></thead>
          <tbody>{report.bins.map((b,i)=><tr key={i}><th scope="row">{i+1}</th><td>{displayNumber(b.lower)}</td><td>{displayNumber(b.upper)}</td><td>{b.count}</td><td>{b.percent.toFixed(1)}%</td></tr>)}</tbody></table>
      </div></Details>
      <p className="preview-note">Q1 {displayNumber(report.q1)} · Q3 {displayNumber(report.q3)}. {report.outlier_method}. {report.note}</p>
      {report.warnings.length>0&&<div className="warning-panel profile-warnings" role="note"><strong>Statistical cautions</strong><ul>{report.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></div>}
    </>}
  </section>;
}
