import type {ImportedDataset} from './datasets';
import type {DatasetColumnProfile} from './columnProfile';
import {WorkspaceIcon} from './WorkspaceIcon';

type Props={dataset:ImportedDataset|null;profile:DatasetColumnProfile|null;profiling:boolean;onInspect:()=>void;onAnalyze:()=>void;onRecord:()=>void};
export function EvidenceTrail({dataset,profile,profiling,onInspect,onAnalyze,onRecord}:Props){
  const verifiedProfile=!!dataset&&profile?.dataset_id===dataset.id;
  return <section className="evidence-trail" aria-labelledby="evidence-trail-title">
    <div className="evidence-head"><div><span className="overline">AX / 02 · EVIDENCE TRAIL</span><h2 id="evidence-trail-title">{dataset?'Your active research':'Begin with evidence'}</h2><p>{dataset?dataset.original_name:'Import an original dataset, inspect its structure, then choose a method.'}</p></div>{dataset?<div className="evidence-fingerprint"><span>SHA-256 · stored fingerprint</span><code title={dataset.sha256}>{dataset.sha256.slice(0,12)}…</code></div>:<a href="#dataset-file" className="evidence-import"><WorkspaceIcon name="upload"/> Import dataset</a>}</div>
    <div className="evidence-stages">
      <a href="#dataset-file" className="evidence-step" data-done={!!dataset}><span className="evidence-number">01</span><div><strong>Source</strong><small>{dataset?`${dataset.row_count.toLocaleString()} rows · ${dataset.column_count} variables`:'Choose original data'}</small></div><span className="evidence-status">{dataset?'Imported':'Start'}</span></a>
      <button type="button" className="evidence-step" data-done={verifiedProfile} disabled={!dataset} onClick={onInspect}><span className="evidence-number">02</span><div><strong>Inspect</strong><small>{verifiedProfile?'Column profile available':profiling?'Inspecting variables…':'Review structure and quality'}</small></div><span className="evidence-status">{verifiedProfile?'Ready':'Review'}</span></button>
      <button type="button" className="evidence-step" disabled={!verifiedProfile} onClick={onAnalyze}><span className="evidence-number">03</span><div><strong>Investigate</strong><small>Explore statistical methods</small></div><WorkspaceIcon name="arrow"/></button>
      <button type="button" className="evidence-step" onClick={onRecord}><span className="evidence-number">04</span><div><strong>Record</strong><small>Open experiment history</small></div><WorkspaceIcon name="arrow"/></button>
    </div>
    <p className="evidence-foot">Import and inspection reflect the current dataset. Investigation and recording are workflow links, not completion claims.</p>
  </section>;
}
