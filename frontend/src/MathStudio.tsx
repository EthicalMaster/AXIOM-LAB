import {useState} from 'react';
import {MathWorkbenchPanel} from './MathWorkbenchPanel';
import {PolynomialPanel} from './PolynomialPanel';
import {MatrixPanel} from './MatrixPanel';
import {NumericalPanel} from './NumericalPanel';
const tools=[{name:'Expression',symbol:'ƒ',description:'Evaluate an arithmetic expression',detail:'Safe numeric calculator'}, {name:'Calculus',symbol:'∂',description:'Explore functions and derivatives',detail:'Polynomials · degree 1–6'}, {name:'Linear algebra',symbol:'▦',description:'Solve systems and inspect matrices',detail:'Square matrices · 1–8'}, {name:'Numerical methods',symbol:'∫',description:'Estimate roots and signed integrals',detail:'Bounded interval'}] as const;
export function MathStudio(){
 const [active,setActive]=useState(0),[visited,setVisited]=useState([0]);
 function select(i:number){setActive(i);setVisited(v=>v.includes(i)?v:[...v,i]);}
 return <div className="math-studio"><header className="math-hero"><div><span className="math-kicker">COMPUTATIONAL WORKSPACE / 04 TOOLS</span><h2>Make mathematics visible.</h2><p>Evaluate, differentiate, solve and integrate. Every result comes from the bounded scientific engine.</p></div><svg viewBox="0 0 180 106" aria-hidden="true"><path d="M12 52H168M90 8V98" stroke="var(--line)" fill="none"/><path className="math-hero-wave" d="M12 83C35 83 47 20 68 20S105 83 126 83S153 22 168 22" fill="none" stroke="var(--accent)" strokeWidth="2"/><path d="M12 20C35 20 47 83 68 83S105 20 126 20S153 83 168 83" fill="none" stroke="var(--cyan)" strokeWidth="1.5" opacity=".55"/><circle cx="90" cy="52" r="22" fill="none" stroke="var(--accent)" opacity=".25"/><circle cx="90" cy="52" r="3" fill="var(--accent)"/></svg></header>
 <nav className="math-tools" aria-label="Mathematics tools">{tools.map((t,i)=><button key={t.name} type="button" aria-pressed={active===i} title={t.description} onClick={()=>select(i)}><span className="math-symbol" aria-hidden="true">{t.symbol}</span><span><strong>{t.name}</strong><small>{t.detail}</small></span><span className="math-tool-arrow" aria-hidden="true">↗</span></button>)}</nav>
 {tools.map((t,i)=>visited.includes(i)&&<div key={t.name} className="math-tool-panel" hidden={active!==i}>{i===0?<MathWorkbenchPanel/>:i===1?<PolynomialPanel/>:i===2?<MatrixPanel/>:<NumericalPanel/>}</div>)}
 </div>;
}
