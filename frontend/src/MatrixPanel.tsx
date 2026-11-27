import {Loading} from './WorkspaceTools';
import {MatrixView,Metrics} from './Visuals';
import {apiFetch} from './apiClient';
import {useState,type FormEvent} from 'react';
type Result={determinant:number;rank:number;condition_number:number|null;inverse:number[][]|null;solution:number[]|null;warnings:string[]};
export function MatrixPanel(){
  const [matrix,setMatrix]=useState('[[2,0],[0,4]]');const [vector,setVector]=useState('[2,8]');
  const [result,setResult]=useState<Result|null>(null);const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();if(busy)return;setError('');setResult(null);
    setBusy(true);try{
      const payload={matrix:JSON.parse(matrix) as unknown,vector:vector.trim()?JSON.parse(vector) as unknown:null};
      const r=await apiFetch('/api/v1/math/matrix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!r.ok)throw Error(`Matrix calculation rejected (HTTP ${r.status})`);setResult(await r.json() as Result);
    }catch(e){setError(e instanceof Error?e.message:'Invalid matrix');}finally{setBusy(false);}
  }
  return <section className="science-panel" aria-labelledby="matrix-title"><div className="preview-heading"><h3 id="matrix-title">Linear algebra</h3><span>PHASE 03C · 1–8 ROWS</span></div>
    <form className="experiment-controls" onSubmit={submit}><label>Square matrix (JSON) <input value={matrix} onChange={e=>setMatrix(e.target.value)}/></label>
      <label>Optional right-hand-side vector <input value={vector} onChange={e=>setVector(e.target.value)}/></label><button className="primary-button" disabled={busy}>Analyse matrix</button></form>
    {busy&&<Loading label="Computing result"/>}{error&&<p role="alert" className="inline-alert error">{error}</p>}
    {result&&<div><Metrics items={[{label:"Determinant",value:result.determinant},{label:"Rank",value:result.rank},{label:"Condition number",value:result.condition_number}]}/>{result.inverse&&<MatrixView matrix={result.inverse} label="Inverse matrix · signed magnitude"/>}<p>Determinant: {result.determinant.toPrecision(6)} · Rank: {result.rank} · Condition: {result.condition_number?.toPrecision(4)??'unbounded'}</p>
      <p>Inverse: <code>{result.inverse?JSON.stringify(result.inverse):'withheld'}</code></p><p>Solution: <code>{result.solution?JSON.stringify(result.solution):'withheld / not requested'}</code></p>
      {result.warnings.map((w,i)=><p key={i}>{w}</p>)}</div>}
  </section>;
}
