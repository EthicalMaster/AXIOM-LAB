import {SourceNotice} from './SourceNotice';
import {ScientificInstrument} from './ScientificInstrument';
import {ThemeSwitch} from './Theme';
import {WorkspaceIcon} from './WorkspaceIcon';
import './landing.css';

const modules = [
  {icon:'Data Lab',title:'Understand your data',copy:'Inspect original observations, missing values, column types and dataset fingerprints.',tag:'CSV / XLS / XLSX'},
  {icon:'Statistics',title:'Test your hypotheses',copy:'Explore distributions, descriptive statistics, relationships and statistical diagnostics.',tag:'STATISTICAL ANALYSIS'},
  {icon:'Mathematics',title:'Work through mathematics',copy:'Explore matrices, polynomials, numerical methods and symbolic computation.',tag:'MATHEMATICAL TOOLS'},
  {icon:'Machine Learning',title:'Build and evaluate models',copy:'Explore supported models and compare results using reproducible configurations.',tag:'MODEL EVALUATION'},
  {icon:'Experiments',title:'Keep a scientific record',copy:'Record experiments, inspect revisions and export supported results.',tag:'EXPERIMENT HISTORY'},
  {icon:'Method guide',title:'Choose a method with care',copy:'Find method explanations and contextual guidance without replacing scientific judgment.',tag:'METHOD GUIDANCE'},
] as const;

export default function LandingPage(){
  return <div className="axiom-landing">
    <a className="landing-skip" href="#landing-main">Skip to content</a>
    <header className="landing-header"><a className="landing-brand" href="./" aria-label="AXIOM LAB home"><span className="landing-brand-mark">∴</span><span>AXIOM<span className="landing-brand-lab"> LAB</span><small>RESEARCH STUDIO</small></span></a><nav aria-label="Main navigation"><a href="#capabilities">Capabilities</a><a href="#method">Method</a></nav><div className="landing-header-actions"><ThemeSwitch/><a className="landing-small-cta" href="?view=studio">Workspace <WorkspaceIcon name="arrow"/></a></div></header>
    <main id="landing-main">
      <section className="landing-hero"><div className="landing-copy"><div className="landing-eyebrow"><span className="landing-rule"/> INDEPENDENT SCIENTIFIC WORKSPACE</div><h1>A research studio<br/>built for <em>evidence.</em></h1><p>Explore datasets, test hypotheses, work through mathematics and evaluate machine learning models. Keep the evidence behind every result.</p><div className="landing-actions"><a className="landing-primary" href="?view=studio">Enter research studio <WorkspaceIcon name="arrow"/></a><a className="landing-secondary" href="#capabilities">Explore capabilities <span aria-hidden="true">↓</span></a></div><div className="landing-note"><span className="landing-rule"/> Built around evidence, not guesswork.</div></div><ScientificInstrument/></section>
      <div className="landing-strip" aria-label="Research workflow"><span>01 / OBSERVE</span><span>02 / ANALYSE</span><span>03 / MODEL</span><span>04 / VALIDATE</span></div>
      <section className="landing-section" id="capabilities"><div className="landing-section-heading"><div><div className="landing-eyebrow">01 / THE INSTRUMENTS</div><h2>One lab.<br/>Many ways to investigate.</h2></div><p>Move from an initial question to an inspectable result with tools built for each stage of the research process.</p></div><div className="landing-module-grid">{modules.map((m,i)=><article key={m.title} className="landing-module"><div className="landing-module-top"><span className="landing-icon"><WorkspaceIcon name={m.icon}/></span><span>0{i+1}</span></div><h3>{m.title}</h3><p>{m.copy}</p><span className="landing-tag">{m.tag}</span></article>)}</div></section>
      <section className="landing-section landing-method" id="method"><div><div className="landing-eyebrow">02 / THE PRINCIPLE</div><h2>Every result should<br/>have a reason.</h2><p>Keep original observations intact, examine the assumptions behind a method, and retain experiment context. AXIOM LAB brings these steps into a single workflow.</p></div><ol className="landing-steps">{[['Import','Preserve the original dataset and its fingerprint.'],['Inspect','Understand quality, types and distributions.'],['Investigate','Choose appropriate mathematical or statistical methods.'],['Record','Keep configurations, outcomes and experiment revisions.']].map(([title,copy],i)=><li key={title}><span>0{i+1}</span><div><h3>{title}</h3><p>{copy}</p></div></li>)}</ol></section>
      <section className="landing-end"><span className="landing-eyebrow">03 / BEGIN YOUR RESEARCH</span><h2>Curiosity is the starting point.</h2><a className="landing-primary" href="?view=studio">Open AXIOM LAB <WorkspaceIcon name="arrow"/></a></section>
    </main>
    <footer className="landing-footer"><span>∴ AXIOM LAB</span><span>Scientific research studio · Evidence first<br/><SourceNotice/></span><a href="#landing-main">Back to top ↑</a></footer>
  </div>;
}
