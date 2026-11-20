import {useState,type FormEvent} from 'react';
type Result={determinant:number;rank:number;condition_number:number|null;inverse:number[][]|null;solution:number[]|null;warnings:string[]};
export function MatrixPanel(){
  const [matrix,setMatrix]=useState('[[2,0],[0,4]]');const [vector,setVector]=useState('[2,8]');
  const [result,setResult]=useState<Result|null>(null);const [error,setError]=useState('');
  async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();setError('');setResult(null);
    try{
      const payload={matrix:JSON.parse(matrix) as unknown,vector:vector.trim()?JSON.parse(vector) as unknown:null};
      const r=await fetch('/api/v1/math/matrix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!r.ok)throw Error(`Matrix calculation rejected (HTTP ${r.status})`);setResult(await r.json() as Result);
    }catch(e){setError(e instanceof Error?e.message:'Invalid matrix');}
  }
  return <section className="science-panel" aria-labelledby="matrix-title"><div className="preview-heading"><h3 id="matrix-title">Linear algebra</h3><span>PHASE 03C · 1–8 ROWS</span></div>
    <form className="experiment-controls" onSubmit={submit}><label>Square matrix (JSON) <input value={matrix} onChange={e=>setMatrix(e.target.value)}/></label>
      <label>Optional right-hand-side vector <input value={vector} onChange={e=>setVector(e.target.value)}/></label><button className="primary-button">Analyse matrix</button></form>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {result&&<div><p>Determinant: {result.determinant.toPrecision(6)} · Rank: {result.rank} · Condition: {result.condition_number?.toPrecision(4)??'unbounded'}</p>
      <p>Inverse: <code>{result.inverse?JSON.stringify(result.inverse):'withheld'}</code></p><p>Solution: <code>{result.solution?JSON.stringify(result.solution):'withheld / not requested'}</code></p>
      {result.warnings.map((w,i)=><p key={i}>{w}</p>)}</div>}
  </section>;
}
