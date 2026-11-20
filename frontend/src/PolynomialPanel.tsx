import { useState, type FormEvent } from 'react';
type Result = {polynomial:string; derivative:string; antiderivative_c0:string; roots_approx:{real:number;imag:number}[]; warnings:string[]};
export function PolynomialPanel(){
  const [source,setSource]=useState('1, 0, -4');
  const [report,setReport]=useState<Result|null>(null);
  const [error,setError]=useState('');
  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();setError('');setReport(null);
    const parts=source.split(',').map(v=>v.trim());const coefficients=parts.map(Number);
    if(parts.some(v=>!v)||coefficients.some(v=>!Number.isFinite(v))){setError('Enter finite numeric coefficients separated by commas.');return;}
    try{const r=await fetch('/api/v1/math/polynomial',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({coefficients})});
      if(!r.ok)throw Error(`Polynomial rejected (HTTP ${r.status})`);
      setReport(await r.json() as Result);
    }catch(e){setError(e instanceof Error?e.message:'Unable to compute polynomial');}
  }
  return <section className="science-panel" aria-labelledby="poly-title"><div className="preview-heading"><h3 id="poly-title">Polynomial calculus</h3><span>PHASE 03B · DEGREE ≤ 6</span></div>
    <p className="profile-description">Coefficients highest degree first. Example 1, 0, -4 represents x²−4; integrals use C=0.</p>
    <form className="experiment-controls" onSubmit={submit}><label>Coefficients <input value={source} onChange={e=>setSource(e.target.value)}/></label><button className="primary-button">Compute polynomial</button></form>
    {error&&<p role="alert" className="inline-alert error">{error}</p>}
    {report&&<div><p>f(x) = {report.polynomial}</p><p>f′(x) = {report.derivative}</p><p>∫f(x)dx (C=0) = {report.antiderivative_c0}</p><p>Approximate roots: {report.roots_approx.map(r=>`${r.real.toPrecision(5)} ${r.imag<0?'-':'+'} ${Math.abs(r.imag).toPrecision(3)}i`).join('; ')}</p><ul>{report.warnings.map((w,i)=><li key={i}>{w}</li>)}</ul></div>}
  </section>;
}
