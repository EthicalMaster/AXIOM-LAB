import {useEffect,useState} from 'react';
import {makeLens,sendLens,type LensContext} from './lensContext';
import './lens.css';
const excluded='input,textarea,select,button,a,pre,code,table:not([data-lens-result]),[contenteditable],.guide-widget,[data-private]';
function element(n:Node|null){return n instanceof Element?n:n?.parentElement??null;}
export function LensAction({context,label='Ask AXIOM'}:{context:LensContext|null;label?:string}){
 return context?<button type="button" className="lens-action" aria-label={`${label}: ${context.label}`} onClick={()=>{if(document.fullscreenElement){void document.exitFullscreen().then(()=>sendLens(context)).catch(()=>undefined);}else sendLens(context);}}><span aria-hidden="true">✳</span>{label}</button>:null;
}
export function SelectionLens({page,busy,remote}:{page:string;busy:boolean;remote:boolean}){
 const [pick,setPick]=useState<{context:LensContext;x:number;y:number;above:boolean;page:string}|null>(null);
 useEffect(()=>{
  function inspect(){const s=window.getSelection();if(!s||s.isCollapsed||s.rangeCount!==1){setPick(null);return;}
   const r=s.getRangeAt(0),a=element(r.startContainer),b=element(r.endContainer),main=document.getElementById('workspace');
   if(!main||!a||!b||!main.contains(a)||!main.contains(b)||a.closest(excluded)||b.closest(excluded)||r.cloneContents().querySelector(excluded)){setPick(null);return;}
   const region=a.closest('.science-panel,.bento-card,.intel-card,.metric-card,.visual-figure')??main;
   if(!region.contains(b)){setPick(null);return;}
   const label=region.querySelector('h2,h3,figcaption')?.textContent??page;
   const ctx=makeLens('text',label,s.toString()),rect=r.getBoundingClientRect();if(!ctx||!rect.width||!rect.height){setPick(null);return;}
   setPick({context:ctx,x:Math.max(12,Math.min(innerWidth-12,rect.left+rect.width/2)),y:rect.top>110?rect.top-8:rect.bottom+8,above:rect.top>110,page});
  }
  const dismiss=()=>setPick(null);
  function down(e:PointerEvent){if(!(e.target instanceof Element)||!e.target.closest('.lens-toolbar'))dismiss();}
  function key(e:KeyboardEvent){if(e.key==='Escape')dismiss();else if(e.shiftKey&&e.key.startsWith('Arrow'))inspect();}
  function up(e:PointerEvent){if(!(e.target instanceof Element)||!e.target.closest('.lens-toolbar'))inspect();}
  document.addEventListener('pointerup',up);document.addEventListener('pointerdown',down);document.addEventListener('keyup',key);window.addEventListener('resize',dismiss);window.addEventListener('scroll',dismiss,true);
  return()=>{document.removeEventListener('pointerup',up);document.removeEventListener('pointerdown',down);document.removeEventListener('keyup',key);window.removeEventListener('resize',dismiss);window.removeEventListener('scroll',dismiss,true);};
 },[page]);
 if(!pick||pick.page!==page)return null;
 return <div className="lens-toolbar" role="group" aria-label="Selected text actions" style={{left:`clamp(150px, ${pick.x}px, calc(100vw - 150px))`,top:pick.y,transform:pick.above?'translate(-50%,-100%)':'translateX(-50%)'}}><small>{remote?'Selected excerpt will be sent to external AI':'Local guidance · selected excerpt'}</small><div><button type="button" disabled={busy} onPointerDown={e=>e.preventDefault()} onClick={()=>{sendLens(pick.context);window.getSelection()?.removeAllRanges();setPick(null)}}><span aria-hidden="true">✳</span> Ask AXIOM</button><button type="button" aria-label="Dismiss selection toolbar" onClick={()=>setPick(null)}>×</button></div></div>;
}
