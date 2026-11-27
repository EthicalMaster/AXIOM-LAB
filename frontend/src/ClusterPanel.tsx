import {useState} from 'react';
type ClusterReport={rows:number;found_clusters:number;cluster_counts:Record<string,number>;inertia:number;silhouette:number|null;warnings:string[]};
export function ClusterPanel({datasetId,numericColumns}:{datasetId:string;numericColumns:string[]}){
  const [feature,setFeature]=useState('');const [count,setCount]=useState('2');const [report,setReport]=useState<ClusterReport|null>(null);const [error,setError]=useState('');
  const selected=numericColumns.includes(feature)?feature:(numericColumns[0]??'');
  async function run(){setError('');setReport(null);
    try{const r=await fetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/ml/clustering`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({features:[selected],n_clusters:Number(count)})});
      if(!r.ok)throw Error(`Clustering rejected (HTTP ${r.status})`);setReport(await r.json() as ClusterReport);
    }catch(e){setError(e instanceof Error?e.message:'Clustering failed');}
  }
  return <section className="science-panel" aria-labelledby="cluster-title"><div className="preview-heading"><h3 id="cluster-title">Clustering</h3><span>PHASE 04D · K-MEANS</span></div>
    <p className="profile-description">Unsupervised grouping on standardized numeric features. Group IDs are arbitrary, not class predictions.</p>
    <div className="experiment-controls"><label>Numeric feature <select value={selected} onChange={e=>setFeature(e.target.value)}>{numericColumns.map(c=><option key={c}>{c}</option>)}</select></label>
      <label>Number of clusters <select value={count} onChange={e=>setCount(e.target.value)}>{[2,3,4,5,6,7,8].map(n=><option key={n}>{n}</option>)}</select></label><button className="primary-button" disabled={!selected} onClick={()=>void run()}>Run K-means</button></div>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {report&&<div><p>Rows: {report.rows} · Groups found: {report.found_clusters} · Inertia: {report.inertia.toPrecision(5)} · Silhouette: {report.silhouette?.toPrecision(4)??'N/A'}</p>
      <p>Group counts: {JSON.stringify(report.cluster_counts)}</p><ul>{report.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></div>}
  </section>;
}
