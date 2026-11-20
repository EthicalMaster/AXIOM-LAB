import { useState, type FormEvent } from 'react';
type MathResult = {value:number; note:string};
export function MathWorkbenchPanel(){
  const [expression,setExpression]=useState('2 * (3 + 4)');
  const [answer,setAnswer]=useState<MathResult|null>(null);
  const [error,setError]=useState('');
  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();setError('');setAnswer(null);
    try{const r=await fetch('/api/v1/math/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expression})});
      if(!r.ok)throw Error(`Expression rejected (HTTP ${r.status})`);
      setAnswer(await r.json() as MathResult);
    }catch(e){setError(e instanceof Error?e.message:'Evaluation failed');}
  }
  return <section className="science-panel" aria-labelledby="math-title">
    <div className="preview-heading"><h3 id="math-title">Mathematical Workbench</h3><span>PHASE 03A · SAFE NUMERIC EXPRESSIONS</span></div>
    <p className="profile-description">Restricted arithmetic, pi/e and sin, cos, sqrt, log. No unrestricted Python code.</p>
    <form className="experiment-controls" onSubmit={submit}>
      <label>Expression <input value={expression} maxLength={120} required onChange={e=>setExpression(e.target.value)}/></label>
      <button className="primary-button">Evaluate</button>
    </form>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {answer&&<p role="status">Result: <strong>{answer.value}</strong>. {answer.note}</p>}
  </section>;
}
