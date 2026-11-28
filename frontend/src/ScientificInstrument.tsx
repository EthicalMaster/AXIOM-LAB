import {useId,useMemo,useState} from 'react';
import {intervalMass,normalDensity} from './instrumentMath';

/** Public, client-only illustration. No private data or API calls. */
export function ScientificInstrument(){
  const [mean,setMean]=useState(0);
  const [sigma,setSigma]=useState(1);
  const id=useId();
  const x=(v:number)=>48+(v+8)*31.5;
  const y=(v:number)=>250-v*278;
  const model=useMemo(()=>{
    const path=(lo:number,hi:number,n:number)=>Array.from({length:n+1},(_,i)=>{
      const t=lo+(hi-lo)*i/n;
      return `${i?'L':'M'}${x(t).toFixed(2)} ${y(normalDensity(t,mean,sigma)).toFixed(2)}`;
    }).join(' ');
    return {curve:path(-8,8,160),shade:`${path(-1,1,64)} L${x(1)} 250 H${x(-1)}Z`,mass:intervalMass(mean,sigma)};
  },[mean,sigma]);
  return <section className="signature-instrument" aria-labelledby={`${id}-title`}>
    <header className="instrument-head"><div><span className="instrument-index">AX / 01 · LIVE INSTRUMENT</span><h2 id={`${id}-title`}>Probability field</h2></div><span className="instrument-live"><i/> Interactive demo</span></header>
    <div className="instrument-reading"><div><span>Probability in [−1, 1]</span><strong>{(model.mass*100).toFixed(2)}<small>%</small></strong></div><div className="instrument-equation">X ~ N(μ, σ²)<small>Normal distribution</small></div></div>
    <svg className="instrument-plot" viewBox="0 0 600 288" role="img" aria-label={`Normal density, mean ${mean.toFixed(1)}, standard deviation ${sigma.toFixed(1)}, probability from minus one to one ${(model.mass*100).toFixed(2)} percent`}>
      {[0,.2,.4,.6,.8].map(v=><g key={v}><line x1="48" x2="552" y1={y(v)} y2={y(v)} stroke="var(--line)" strokeDasharray="2 5"/><text x="38" y={y(v)+4} textAnchor="end">{v.toFixed(1)}</text></g>)}
      {[-8,-6,-4,-2,0,2,4,6,8].map(v=><g key={v}><line x1={x(v)} x2={x(v)} y1="27" y2="250" stroke="var(--line)" strokeDasharray="2 5"/><text x={x(v)} y="270" textAnchor="middle">{v}</text></g>)}
      <path d={model.shade} fill="var(--accent)" opacity=".20"/>
      <path d={model.curve} fill="none" stroke="var(--accent)" strokeWidth="2.6" strokeLinejoin="round"/>
      <path d={`M${x(-1)} 27V250 M${x(1)} 27V250`} stroke="var(--accent)" strokeDasharray="4 5" opacity=".65"/>
      <path d={`M${x(mean)} 27V250`} stroke="var(--muted)" strokeDasharray="2 6"/>
      <path d="M48 27V250H552" fill="none" stroke="var(--muted)" opacity=".8"/>
      <circle cx={x(mean)} cy={y(normalDensity(mean,mean,sigma))} r="4" fill="var(--accent)" stroke="var(--surface)" strokeWidth="2"/>
    </svg>
    <div className="instrument-controls">
      <label htmlFor={`${id}-mean`}><span>Mean (μ)<output>{mean.toFixed(1)}</output></span><input id={`${id}-mean`} type="range" min="-3" max="3" step="0.1" value={mean} onChange={e=>setMean(Number(e.target.value))}/></label>
      <label htmlFor={`${id}-sigma`}><span>Spread (σ)<output>{sigma.toFixed(1)}</output></span><input id={`${id}-sigma`} type="range" min="0.6" max="2.5" step="0.1" value={sigma} onChange={e=>setSigma(Number(e.target.value))}/></label>
    </div>
    <footer className="instrument-foot"><span>Computed illustration · no uploaded data</span><button type="button" onClick={()=>{setMean(0);setSigma(1)}}>Reset parameters</button></footer>
  </section>;
}
