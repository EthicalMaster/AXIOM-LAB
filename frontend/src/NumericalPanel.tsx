import {useState,type FormEvent} from 'react';
type Result={root:number|null;root_residual:number|null;integral:number;estimated_absolute_error:number;warnings:string[];note:string};
export function NumericalPanel(){
  const [coeff,setCoeff]=useState('1,0,-4');const [a,setA]=useState('0');const [b,setB]=useState('3');
  const [result,setResult]=useState<Result|null>(null);const [error,setError]=useState('');
  async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();setError('');setResult(null);
    const items=coeff.split(',').map(v=>v.trim());
    if(items.some(v=>!v||!Number.isFinite(Number(v)))||a.trim()===''||b.trim()===''){setError('Use finite coefficients and bounds.');return;}
    try{const r=await fetch('/api/v1/math/numerical',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({coefficients:items.map(Number),lower:Number(a),upper:Number(b)})});
      if(!r.ok)throw Error(`Interval calculation rejected (HTTP ${r.status})`);setResult(await r.json() as Result);
    }catch(e){setError(e instanceof Error?e.message:'Numerical calculation failed');}
  }
  return <section className="science-panel" aria-labelledby="numeric-title"><div className="preview-heading"><h3 id="numeric-title">Numerical methods</h3><span>PHASE 03D · 1D POLYNOMIAL</span></div>
    <form className="experiment-controls" onSubmit={submit}><label>Coefficients <input value={coeff} onChange={e=>setCoeff(e.target.value)}/></label>
      <label>Lower bound <input type="number" step="any" value={a} onChange={e=>setA(e.target.value)}/></label>
      <label>Upper bound <input type="number" step="any" value={b} onChange={e=>setB(e.target.value)}/></label><button className="primary-button">Calculate interval</button></form>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {result&&<div><p>Bracketed root: {result.root??'Not established'} · Integral: {result.integral.toPrecision(8)} ± {result.estimated_absolute_error.toPrecision(3)} estimated numerical error</p>
      <p className="preview-note">{result.note}</p>{result.warnings.map((w,i)=><p key={i}>{w}</p>)}</div>}
  </section>;
}
