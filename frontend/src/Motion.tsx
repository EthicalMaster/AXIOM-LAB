import {useLayoutEffect,useRef,type ReactNode} from 'react';

/** Measure the actual active item, including changes to the sidebar width. */
export function MotionNav({active,children}:{active:string;children:ReactNode}) {
  const nav=useRef<HTMLElement>(null);
  useLayoutEffect(()=>{
    const el=nav.current;
    if(!el)return;
    function update(){
      if(!el)return;
      const selected=el.querySelector<HTMLElement>('[aria-current="page"]');
      if(!selected)return;
      el.style.setProperty('--nav-y',`${selected.offsetTop}px`);
      el.style.setProperty('--nav-height',`${selected.offsetHeight}px`);
      el.dataset.indicator='ready';
    }
    update();
    if(typeof ResizeObserver==='undefined'){window.addEventListener('resize',update);return ()=>window.removeEventListener('resize',update);}
    const observer=new ResizeObserver(update);
    observer.observe(el);
    for(const item of el.querySelectorAll('button'))observer.observe(item);
    return ()=>observer.disconnect();
  },[active]);
  return <nav ref={nav} className="motion-nav" aria-label="Workspaces"><span className="nav-marker" aria-hidden="true"/>{children}</nav>;
}

/** Decorative geometry, never a measurement or an estimated progress percentage. */
export function AxiomMark({small=false}:{small?:boolean}){
  return <svg className={`axiom-mark${small?' axiom-mark-small':''}`} viewBox="0 0 120 120" fill="none" aria-hidden="true">
    <circle cx="60" cy="60" r="53" className="mark-track"/>
    <g className="mark-orbit"><circle cx="60" cy="60" r="47" stroke="currentColor" strokeDasharray="36 260" strokeWidth="1.5"/><circle cx="107" cy="60" r="3" fill="currentColor"/></g>
    <g className="mark-orbit reverse"><ellipse cx="60" cy="60" rx="31" ry="43" stroke="var(--cyan)" strokeWidth="1.25" strokeDasharray="42 200"/><circle cx="60" cy="17" r="2.5" fill="var(--cyan)"/></g>
    <path d="M60 35 82 78 38 78Z" stroke="currentColor" strokeOpacity=".3" strokeWidth="1"/>
    <g className="mark-core" fill="currentColor"><circle cx="60" cy="43" r="5"/><circle cx="42" cy="76" r="5"/><circle cx="78" cy="76" r="5"/></g>
  </svg>;
}
