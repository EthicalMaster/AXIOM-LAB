import {useId,useMemo,useState} from 'react';
import {ThemeSwitch} from './Theme';
import {WorkspaceIcon} from './WorkspaceIcon';
import './landing.css';

const modes = ['Surface','Distribution','Model'] as const;
type Mode = typeof modes[number];
const modules = [
  {icon:'Data Lab',title:'Understand your data',copy:'Inspect original observations, missing values, column types and dataset fingerprints.',tag:'CSV / XLS / XLSX'},
  {icon:'Statistics',title:'Test your hypotheses',copy:'Explore distributions, descriptive statistics, relationships and statistical diagnostics.',tag:'STATISTICAL ANALYSIS'},
  {icon:'Mathematics',title:'Work through mathematics',copy:'Explore matrices, polynomials, numerical methods and symbolic computation.',tag:'MATHEMATICAL TOOLS'},
  {icon:'Machine Learning',title:'Build and evaluate models',copy:'Explore supported models and compare results using reproducible configurations.',tag:'MODEL EVALUATION'},
  {icon:'Experiments',title:'Keep a scientific record',copy:'Record experiments, inspect revisions and export supported results.',tag:'EXPERIMENT HISTORY'},
  {icon:'Method guide',title:'Choose a method with care',copy:'Find method explanations and contextual guidance without replacing scientific judgment.',tag:'METHOD GUIDANCE'},
] as const;

function surfacePaths() {
  const project=(u:number,v:number)=>{
    const r=1.6+.55*Math.cos(v);
    const x=r*Math.cos(u),y=r*Math.sin(u),z=.55*Math.sin(v);
    return [300+100*x,192+100*(y*Math.cos(.83)-z*Math.sin(.83))];
  };
  const line=(fixed:number,around:boolean)=>Array.from({length:65},(_,i)=>{
    const t=i*Math.PI/32;
    const [x,y]=around?project(t,fixed):project(fixed,t);
    return (i?'L':'M')+x.toFixed(1)+' '+y.toFixed(1);
  }).join(' ');
  return [...Array.from({length:15},(_,i)=>line(i*2*Math.PI/15,true)),...Array.from({length:26},(_,i)=>line(i*2*Math.PI/26,false))];
}

function ScientificVisual(){
  const [mode,setMode]=useState<Mode>('Surface');
  const id=useId();
  const mesh=useMemo(surfacePaths,[]);
  return <div className="landing-visual">
    <div className="landing-visual-top"><span><i/> CONCEPTUAL FIELD</span><span>FIG. 01 / {String(modes.indexOf(mode)+1).padStart(2,'0')}</span></div>
    <svg className="landing-field" viewBox="0 0 600 390" role="img" aria-label={mode==='Surface'?'Illustrative mathematical torus':mode==='Distribution'?'Illustrative probability density curve':'Illustrative model fit with synthetic observations'}>
      <defs><pattern id={id+'grid'} width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="currentColor" opacity=".12"/></pattern><radialGradient id={id+'glow'}><stop stopColor="var(--accent)" stopOpacity=".13"/><stop offset="1" stopColor="var(--accent)" stopOpacity="0"/></radialGradient></defs>
      <rect width="600" height="390" fill={'url(#'+id+'grid)'}/><ellipse cx="300" cy="190" rx="270" ry="180" fill={'url(#'+id+'glow)'}/>
      {mode==='Surface'&&<g className="landing-surface"><path d="M70 195H530M300 33V345" stroke="currentColor" strokeDasharray="3 8" opacity=".32"/>{mesh.map((d,i)=><path key={i} d={d} fill="none" stroke={i<15?'var(--accent)':'currentColor'} strokeWidth={i<15?1.15:.8} opacity={i<15?.78:.45}/>)}<circle cx="300" cy="192" r="4" fill="var(--accent)"/><text x="320" y="183">∴</text></g>}
      {mode==='Distribution'&&<g className="landing-plot"><path d="M80 58V320H540" fill="none" stroke="currentColor" opacity=".65"/>{Array.from({length:8},(_,i)=><line key={i} x1={105+i*55} x2={105+i*55} y1="80" y2="320" stroke="currentColor" opacity=".12"/>)}<path d="M85 319 C160 319 185 306 223 235 S264 100 300 100 S349 170 377 235 S440 319 535 319 L535 320 H85Z" fill="var(--accent)" opacity=".12"/><path d="M85 319 C160 319 185 306 223 235 S264 100 300 100 S349 170 377 235 S440 319 535 319" stroke="var(--accent)" fill="none" strokeWidth="2.5"/><path d="M300 100V320" stroke="currentColor" strokeDasharray="5 7" opacity=".6"/><text x="310" y="89">μ</text><text x="490" y="344">x</text><text x="88" y="75">p(x)</text></g>}
      {mode==='Model'&&<g className="landing-plot"><path d="M80 58V320H540" fill="none" stroke="currentColor" opacity=".65"/><path d="M100 294L516 82" stroke="var(--accent)" strokeWidth="2.5"/>{Array.from({length:22},(_,i)=>{const x=105+i*19;const y=291-i*9.7+Math.sin(i*7.7)*27;return <circle key={i} cx={x} cy={y} r="4" fill="currentColor" opacity=".8"/>})}<text x="390" y="65">y = mx + c</text><text x="510" y="342">x</text></g>}
    </svg>
    <div className="landing-visual-bottom"><div className="landing-mode-group" role="group" aria-label="Illustration mode">{modes.map(m=><button key={m} type="button" aria-pressed={mode===m} onClick={()=>setMode(m)}>{m}</button>)}</div><span>ILLUSTRATION ONLY</span></div>
  </div>;
}

export default function LandingPage(){
  return <div className="axiom-landing">
    <a className="landing-skip" href="#landing-main">Skip to content</a>
    <header className="landing-header"><a className="landing-brand" href="./" aria-label="AXIOM LAB home"><span className="landing-brand-mark">∴</span><span>AXIOM<span className="landing-brand-lab"> LAB</span><small>RESEARCH STUDIO</small></span></a><nav aria-label="Main navigation"><a href="#capabilities">Capabilities</a><a href="#method">Method</a></nav><div className="landing-header-actions"><ThemeSwitch/><a className="landing-small-cta" href="?view=studio">Workspace <WorkspaceIcon name="arrow"/></a></div></header>
    <main id="landing-main">
      <section className="landing-hero"><div className="landing-copy"><div className="landing-eyebrow"><span className="landing-rule"/> INDEPENDENT SCIENTIFIC WORKSPACE</div><h1>From raw data<br/>to <em>clearer</em><br className="landing-desktop-break"/> understanding.</h1><p>One focused research studio for data exploration, statistics, mathematics, machine learning and reproducible experiments.</p><div className="landing-actions"><a className="landing-primary" href="?view=studio">Enter research studio <WorkspaceIcon name="arrow"/></a><a className="landing-secondary" href="#capabilities">Explore capabilities <span aria-hidden="true">↓</span></a></div><div className="landing-note"><span className="landing-rule"/> Built around evidence, not guesswork.</div></div><ScientificVisual/></section>
      <div className="landing-strip" aria-label="Research workflow"><span>01 / OBSERVE</span><span>02 / ANALYSE</span><span>03 / MODEL</span><span>04 / VALIDATE</span></div>
      <section className="landing-section" id="capabilities"><div className="landing-section-heading"><div><div className="landing-eyebrow">01 / THE INSTRUMENTS</div><h2>One lab.<br/>Many ways to investigate.</h2></div><p>Move from an initial question to an inspectable result with tools built for each stage of the research process.</p></div><div className="landing-module-grid">{modules.map((m,i)=><article key={m.title} className="landing-module"><div className="landing-module-top"><span className="landing-icon"><WorkspaceIcon name={m.icon}/></span><span>0{i+1}</span></div><h3>{m.title}</h3><p>{m.copy}</p><span className="landing-tag">{m.tag}</span></article>)}</div></section>
      <section className="landing-section landing-method" id="method"><div><div className="landing-eyebrow">02 / THE PRINCIPLE</div><h2>Every result should<br/>have a reason.</h2><p>Keep original observations intact, examine the assumptions behind a method, and retain experiment context. AXIOM LAB brings these steps into a single workflow.</p></div><ol className="landing-steps">{[['Import','Preserve the original dataset and its fingerprint.'],['Inspect','Understand quality, types and distributions.'],['Investigate','Choose appropriate mathematical or statistical methods.'],['Record','Keep configurations, outcomes and experiment revisions.']].map(([title,copy],i)=><li key={title}><span>0{i+1}</span><div><h3>{title}</h3><p>{copy}</p></div></li>)}</ol></section>
      <section className="landing-end"><span className="landing-eyebrow">03 / BEGIN YOUR RESEARCH</span><h2>Curiosity is the starting point.</h2><a className="landing-primary" href="?view=studio">Open AXIOM LAB <WorkspaceIcon name="arrow"/></a></section>
    </main>
    <footer className="landing-footer"><span>∴ AXIOM LAB</span><span>Scientific research studio · Evidence first</span><a href="#landing-main">Back to top ↑</a></footer>
  </div>;
}
