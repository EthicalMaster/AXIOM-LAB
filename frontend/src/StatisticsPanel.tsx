import {BoxPlot,Metrics,Details} from './Visuals';
import {Loading} from './WorkspaceTools';
import { useEffect, useState } from 'react';
import { displayNumber, fetchStatistics, type DatasetStatistics } from './statistics';

export function StatisticsPanel({ datasetId }: { datasetId: string }) {
  const [report, setReport] = useState<DatasetStatistics | null>(null);
  const [column,setColumn]=useState('');
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    setReport(null); setError(null);
    void fetchStatistics(datasetId).then(data => { if (active) setReport(data); })
      .catch(e => { if (active) setError(e instanceof Error ? e.message : 'Unknown error'); });
    return () => { active = false; };
  }, [datasetId]);
  const selected=report?.columns.find(c=>c.column===column)??report?.columns[0];
  return <section className="science-panel" aria-labelledby="stat-title">
    <div className="preview-heading"><h3 id="stat-title">Descriptive statistics</h3><span>PHASE 01C · VERIFIED CALCULATIONS</span></div>
    <p className="profile-description">Only entirely numeric columns are analysed. Sample variance uses n−1; population variance uses n. Quartiles use type-7 interpolation. Missing values are excluded, never silently filled.</p>
    {error && <div className="inline-alert error" role="alert">{error}</div>}
    {!report && !error && <Loading label="Computing numerical summaries"/>}
    {selected&&<><label className="distribution-picker">Numeric column<select value={selected.column} onChange={e=>setColumn(e.target.value)}>{report?.columns.map(c=><option key={c.column}>{c.column}</option>)}</select></label><Metrics items={[{label:'Mean',value:selected.mean},{label:'Median',value:selected.median},{label:'Sample SD',value:selected.sample_stddev},{label:'Valid observations',value:selected.count}]}/><BoxPlot label={selected.column} min={selected.minimum} max={selected.maximum} q1={selected.q1} q3={selected.q3} median={selected.median}/></>}
    {report && (!report.columns.length ? <p className="preview-note">No consistently numeric columns found. Inspect the column warnings; AXIOM LAB will not coerce mixed data.</p> :
      <Details title="All column statistics"><div className="table-scroll" tabIndex={0} aria-label="Descriptive statistics results">
        <table className="data-table"><thead><tr>{['Column','Count','Missing','Mean','Median','Min','Max','Q1','Q3','Sample SD'].map(h=><th key={h} scope="col">{h}</th>)}</tr></thead>
          <tbody>{report.columns.map(c=><tr key={c.column}><th scope="row">{c.column}</th>
            {[c.count,c.missing_count,c.mean,c.median,c.minimum,c.maximum,c.q1,c.q3,c.sample_stddev].map((v,i)=><td key={i}>{displayNumber(v)}</td>)}</tr>)}</tbody></table>
      </div></Details>)}
    {report && <p className="preview-note">Method {report.method}. {report.note} {report.columns.flatMap(c=>c.notes.map(n=>`${c.column}: ${n}`)).join(' ')}</p>}
  </section>;
}
