import {useEffect,useId,useRef,useState,type PointerEvent} from 'react';
import {displayNumber} from './statistics';
import {LensAction} from './Lens';
import {makeLens,type LensContext} from './lensContext';
import {initialViewport,panViewport,zoomViewport,clampViewport,interpolateViewport,pinchViewport,axisTicks,MAX_ZOOM,type Viewport} from './plotViewport';
type Point={x:number;y:number};
type Bin={lower:number;upper:number;count:number};
type Series={label:string;points:Point[];color?:string};
type Props={points:Point[];label:string;xLabel:string;yLabel:string;connected?:boolean;diagonal?:boolean;bins?:Bin[];xDomain?:[number,number];yDomain?:[number,number];series?:Series[];markers?:Point[];shade?:boolean};
const left=76,top=24,width=656,height=290;
const fmt=displayNumber;
const finite=(p:Point)=>Number.isFinite(p.x)&&Number.isFinite(p.y);
function range(values:number[],given?:[number,number]):[number,number]{
 const lo=given?.[0]??Math.min(...values),hi=given?.[1]??Math.max(...values);
 if(!Number.isFinite(lo)||!Number.isFinite(hi))return [0,1];
 if(lo<hi)return [lo,hi];
 const pad=Math.max(1,Math.abs(lo)*.01);return [lo-pad,lo+pad];
}
function useCamera(key:string){
 const [view,setView]=useState(initialViewport);const current=useRef(initialViewport),target=useRef(initialViewport),frame=useRef(0);
 function cancel(){cancelAnimationFrame(frame.current);frame.current=0;target.current=current.current;}
 function publish(v:Viewport){current.current=v;setView(v);}
 function update(fn:(v:Viewport)=>Viewport,animate=false){
  const next=fn(animate?target.current:current.current);cancel();target.current=next;
  if(!animate||window.matchMedia('(prefers-reduced-motion: reduce)').matches){publish(next);return;}
  const start=current.current,t0=performance.now();
  function tick(now:number){const t=Math.min(1,(now-t0)/210);publish(interpolateViewport(start,next,1-(1-t)**3));if(t<1)frame.current=requestAnimationFrame(tick);else frame.current=0;}
  frame.current=requestAnimationFrame(tick);
 }
 useEffect(()=>{cancelAnimationFrame(frame.current);frame.current=0;current.current=initialViewport;target.current=initialViewport;setView(initialViewport);return()=>cancelAnimationFrame(frame.current)},[key]);
 return {view,update,cancel};
}
export function InteractivePlot({points,bins,label,xLabel,yLabel,connected,diagonal,xDomain,yDomain,series=[],markers=[],shade=false}:Props){
 const valid=points.filter(finite),extra=series.map(s=>({...s,points:s.points.filter(finite)})),marks=markers.filter(finite);
 const actualBins=bins?.filter(b=>Number.isFinite(b.lower)&&Number.isFinite(b.upper)&&Number.isFinite(b.count)&&b.upper>b.lower&&b.count>=0)??[];
 const all=[...valid,...extra.flatMap(s=>s.points),...marks];const hasData=all.length>0||actualBins.length>0;
 const valuesX=all.map(p=>p.x),valuesY=all.map(p=>p.y);
 const [xmin,xmax]=range(hasData?[...valuesX,...actualBins.flatMap(b=>[b.lower,b.upper]),...(diagonal?valuesY:[])]:[0,1],xDomain);
 const [ymin,ymax]=range(hasData?[...valuesY,...(actualBins.length?[0,...actualBins.map(b=>b.count)]:[]),...(diagonal?valuesX:[]),...(shade?[0]:[])]:[0,1],yDomain);
 const key=JSON.stringify([label,xLabel,yLabel,xmin,xmax,ymin,ymax]);
 const {view,update,cancel}=useCamera(key);
 const [cursor,setCursor]=useState<{x:number;y:number}|null>(null),[dragging,setDragging]=useState(false),[expanded,setExpanded]=useState(false),[scrollZoom,setScrollZoom]=useState(false);
 const [pinned,setPinned]=useState<LensContext|null>(null);
 const tap=useRef<{id:number;point:Point}|null>(null);
 const contacts=useRef(new Map<number,Point>()),svg=useRef<SVGSVGElement>(null),figure=useRef<HTMLElement>(null);const clip=useId(),gradient=useId();
 const X=(x:number)=>left+((x-xmin)/(xmax-xmin)-view.x)*view.scale*width;
 const Y=(y:number)=>top+height-((y-ymin)/(ymax-ymin)-view.y)*view.scale*height;
 const inside=(p:Point)=>p.x>=left&&p.x<=left+width&&p.y>=top&&p.y<=top+height;
 const normal=(p:Point)=>({x:Math.max(0,Math.min(1,(p.x-left)/width)),y:Math.max(0,Math.min(1,1-(p.y-top)/height))});
 const at=(e:PointerEvent<SVGSVGElement>)=>{const matrix=e.currentTarget.getScreenCTM();return matrix?new DOMPoint(e.clientX,e.clientY).matrixTransform(matrix.inverse()):null;};
 // Native wheel listener prevents page scrolling only during an opted-in plot zoom.
 const updateRef=useRef(update);updateRef.current=update;
 useEffect(()=>{const el=svg.current;if(!el)return;const wheel=(e:WheelEvent)=>{if(!scrollZoom&&!e.ctrlKey&&!e.metaKey)return;const matrix=el.getScreenCTM();if(!matrix)return;const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(matrix.inverse());if(!inside(p))return;e.preventDefault();const a=normal(p),delta=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?180:1);updateRef.current(v=>zoomViewport(v,Math.exp(-Math.max(-200,Math.min(200,delta))*.0035),a.x,a.y),true);};el.addEventListener('wheel',wheel,{passive:false});return()=>el.removeEventListener('wheel',wheel)},[hasData,scrollZoom]);
 useEffect(()=>{setCursor(null);contacts.current.clear();setDragging(false);setPinned(null);tap.current=null},[key]);
 useEffect(()=>{setPinned(null)},[points,bins,label]);
 useEffect(()=>{const change=()=>setExpanded(document.fullscreenElement===figure.current);document.addEventListener('fullscreenchange',change);return()=>document.removeEventListener('fullscreenchange',change)},[]);
 async function toggleExpanded(){if(document.fullscreenElement===figure.current){await document.exitFullscreen().catch(()=>undefined);return;}if(expanded){setExpanded(false);return;}if(figure.current?.requestFullscreen&&document.fullscreenEnabled){try{await figure.current.requestFullscreen();return;}catch{/* Inline fallback when fullscreen is unavailable. */}}setExpanded(true);}

 if(!hasData)return <p className="intel-empty">No plottable values.</p>;
 const lowX=xmin+view.x*(xmax-xmin),highX=xmin+(view.x+1/view.scale)*(xmax-xmin),lowY=ymin+view.y*(ymax-ymin),highY=ymin+(view.y+1/view.scale)*(ymax-ymin);
 const tickX=axisTicks(lowX,highX,7),tickY=axisTicks(lowY,highY,5);
 let hover:Point|null=null,hoverLabel=yLabel;let distance=16;
 if(cursor){for(const [name,group] of [[yLabel,valid],...extra.map(s=>[s.label,s.points] as const),['Marker',marks]] as const){for(const p of group){const d=Math.hypot(X(p.x)-cursor.x,Y(p.y)-cursor.y);if(d<distance&&inside({x:X(p.x),y:Y(p.y)})){hover=p;hoverLabel=name;distance=d;}}}}
 const hoveredBin=cursor?actualBins.find(b=>cursor.x>=X(b.lower)&&cursor.x<=X(b.upper)&&cursor.y>=Y(b.count)&&cursor.y<=Y(0)):undefined;
 function end(e:PointerEvent<SVGSVGElement>){
  const start=tap.current,p=at(e);tap.current=null;
  if(e.type==='pointerup'&&start?.id===e.pointerId&&p&&Math.hypot(p.x-start.point.x,p.y-start.point.y)<8){
   const bin=actualBins.find(b=>p.x>=X(b.lower)&&p.x<=X(b.upper)&&p.y>=Y(b.count)&&p.y<=Y(0));
   if(bin)setPinned(makeLens('bin',label,`${xLabel}: ${bin.lower} to ${bin.upper} · Count: ${bin.count}`));
   else{let nearest:LensContext|null=null,best=18;for(const [name,group] of [[yLabel,valid],...extra.map(s=>[s.label,s.points] as const),['Marker',marks]] as const){for(const point of group){const d=Math.hypot(X(point.x)-p.x,Y(point.y)-p.y);if(d<best&&inside({x:X(point.x),y:Y(point.y)})){best=d;nearest=makeLens('point',label,`${xLabel}: ${point.x} · ${name}: ${point.y}`)}}}setPinned(nearest);}
  }
  contacts.current.delete(e.pointerId);setDragging(contacts.current.size>0)
 }
 const mid=(a:Point,b:Point)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
 return <figure ref={figure} className={`visual-figure interactive-figure camera-figure${expanded?' camera-expanded':''}`}>
 <div className="camera-heading"><div><figcaption>{label}</figcaption><small>{actualBins.length?`${actualBins.length} bins`:`${valid.length} plotted samples`} · Interactive coordinates</small></div><div className="camera-controls" role="group" aria-label="Plot camera">
 <button type="button" title="Zoom out" aria-label="Zoom out" disabled={view.scale<=1.0001} onClick={()=>update(v=>zoomViewport(v,1/1.5),true)}>−</button><output aria-label="Zoom level">{view.scale.toFixed(1)}×</output><button type="button" title="Zoom in" aria-label="Zoom in" disabled={view.scale>=MAX_ZOOM-.001} onClick={()=>update(v=>zoomViewport(v,1.5),true)}>+</button><button type="button" onClick={()=>update(()=>initialViewport,true)}>Fit</button><button type="button" aria-pressed={expanded} onClick={()=>void toggleExpanded()}>{expanded?'Close expanded':'Expand'}</button></div></div>
 <div className="camera-stage"><svg ref={svg} viewBox="0 0 760 370" className={`interactive-plot${view.scale>1?' zoomed':''}${dragging?' dragging':''}${scrollZoom?' gesture-mode':''}`} role="img" aria-label={`${label}: ${xLabel} and ${yLabel}. Use zoom controls, keyboard arrows and Home.`} tabIndex={0}
 onKeyDown={e=>{const directions:Record<string,[number,number]>={ArrowLeft:[.15,0],ArrowRight:[-.15,0],ArrowUp:[0,.15],ArrowDown:[0,-.15]};if(e.key in directions){e.preventDefault();update(v=>panViewport(v,...directions[e.key]),true)}else if(e.key==='+'||e.key==='='){e.preventDefault();update(v=>zoomViewport(v,1.5),true)}else if(e.key==='-'){e.preventDefault();update(v=>zoomViewport(v,1/1.5),true)}else if(e.key==='Home'){e.preventDefault();update(()=>initialViewport,true)}}}
 onDoubleClick={e=>{const m=e.currentTarget.getScreenCTM();if(!m)return;const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(m.inverse());if(inside(p)){const a=normal(p);update(v=>zoomViewport(v,e.shiftKey?1/2:2,a.x,a.y),true)}}}
 onPointerDown={e=>{if(e.button!==0||contacts.current.size>=2)return;const p=at(e);if(!p||!inside(p))return;cancel();tap.current=contacts.current.size===0?{id:e.pointerId,point:p}:null;contacts.current.set(e.pointerId,p);e.currentTarget.setPointerCapture(e.pointerId);setDragging(true);setCursor(null)}}
 onPointerMove={e=>{const p=at(e);if(!p)return;const prev=contacts.current.get(e.pointerId);if(prev){if(tap.current&&Math.hypot(p.x-tap.current.point.x,p.y-tap.current.point.y)>=8)tap.current=null;const other=[...contacts.current.entries()].find(([id])=>id!==e.pointerId)?.[1];contacts.current.set(e.pointerId,p);if(other){const old=normal(mid(prev,other)),next=normal(mid(p,other));const d0=Math.hypot(prev.x-other.x,prev.y-other.y),d1=Math.hypot(p.x-other.x,p.y-other.y);if(d0>2&&d1>2)update(v=>pinchViewport(v,d1/d0,old.x,old.y,next.x,next.y))}else update(v=>panViewport(v,(p.x-prev.x)/width,(p.y-prev.y)/height));return;}setCursor(inside(p)?p:null)}} onPointerUp={end} onPointerCancel={end} onLostPointerCapture={end} onPointerLeave={()=>setCursor(null)}>
 <defs><clipPath id={clip}><rect x={left} y={top} width={width} height={height}/></clipPath><linearGradient id={gradient} x1="0" y1="0" x2="0" y2="1"><stop stopColor="var(--accent)" stopOpacity=".34"/><stop offset="1" stopColor="var(--accent)" stopOpacity=".06"/></linearGradient></defs>
 <rect x={left} y={top} width={width} height={height} rx="3" fill="var(--surface)" stroke="var(--line)"/>
 {tickY.map(t=><g key={t}><line x1={left} x2={left+width} y1={Y(t)} y2={Y(t)} stroke="var(--line)" strokeDasharray="3 5"/><text x={left-9} y={Y(t)+4} textAnchor="end">{fmt(t)}</text></g>)}
 {tickX.map(t=><g key={t}><line x1={X(t)} x2={X(t)} y1={top} y2={top+height} stroke="var(--line)" opacity=".7"/><text x={X(t)} y={top+height+19} textAnchor="middle">{fmt(t)}</text></g>)}
 <g clipPath={`url(#${clip})`}>
 {lowX<=0&&highX>=0&&<line x1={X(0)} x2={X(0)} y1={top} y2={top+height} stroke="var(--muted)" opacity=".65"/>}{lowY<=0&&highY>=0&&<line x1={left} x2={left+width} y1={Y(0)} y2={Y(0)} stroke="var(--muted)" opacity=".65"/>}
 {diagonal&&<line x1={X(xmin)} y1={Y(xmin)} x2={X(xmax)} y2={Y(xmax)} stroke="var(--violet)" strokeDasharray="5 4"/>}
 {shade&&valid.length>1&&<polygon points={`${X(valid[0].x)},${Y(0)} ${valid.map(p=>`${X(p.x)},${Y(p.y)}`).join(' ')} ${X(valid[valid.length-1].x)},${Y(0)}`} fill={`url(#${gradient})`}/>}
 {connected&&<polyline className="camera-trace" pathLength="1" points={valid.map(p=>`${X(p.x)},${Y(p.y)}`).join(' ')} fill="none" stroke="var(--accent)" strokeWidth="2.2" vectorEffect="non-scaling-stroke"/>}
 {extra.map((s,i)=><polyline key={i} points={s.points.map(p=>`${X(p.x)},${Y(p.y)}`).join(' ')} fill="none" stroke={s.color??'var(--cyan)'} strokeWidth="2" strokeDasharray="6 4" vectorEffect="non-scaling-stroke"/>)}
 {!connected&&valid.map((p,i)=><circle key={i} cx={X(p.x)} cy={Y(p.y)} r="3.3" fill="var(--accent)" opacity=".85"><title>{xLabel}: {p.x}; {yLabel}: {p.y}</title></circle>)}
 {actualBins.map((b,i)=><rect key={i} x={X(b.lower)} y={Y(b.count)} width={Math.max(.5,X(b.upper)-X(b.lower)-1)} height={Math.max(0,Y(0)-Y(b.count))} rx="2" fill="var(--cyan)" opacity=".8"><title>{b.lower}–{b.upper}: {b.count}</title></rect>)}
 {marks.map((p,i)=><circle key={i} cx={X(p.x)} cy={Y(p.y)} r="5" fill="var(--amber)" stroke="var(--surface)" strokeWidth="2"><title>Marker: {fmt(p.x)}, {fmt(p.y)}</title></circle>)}
 {cursor&&!dragging&&<g pointerEvents="none"><path d={`M${cursor.x} ${top}V${top+height} M${left} ${cursor.y}H${left+width}`} stroke="var(--muted)" strokeDasharray="4 4" opacity=".6"/>{hover&&<circle cx={X(hover.x)} cy={Y(hover.y)} r="5.5" fill="var(--surface)" stroke="var(--accent)" strokeWidth="2"/>}</g>}
 </g><text x={left} y="14">{yLabel}</text><text x={left+width/2} y="354" textAnchor="middle">{xLabel}</text></svg></div>
 {extra.length>0&&<div className="camera-legend"><span style={{color:'var(--accent)'}}>━ {yLabel}</span>{extra.map(s=><span key={s.label} style={{color:s.color??'var(--cyan)'}}>┄ {s.label}</span>)}</div>}
 <div className="camera-footer"><div className="camera-readout"><b>{hover?`${xLabel}: ${fmt(hover.x)} · ${hoverLabel}: ${fmt(hover.y)}`:hoveredBin?`${fmt(hoveredBin.lower)} – ${fmt(hoveredBin.upper)} · Count: ${hoveredBin.count}`:pinned?`Inspected: ${pinned.excerpt}`:'Explore the plotted coordinates'}</b><small>{fmt(lowX)} ≤ {xLabel} ≤ {fmt(highX)} · {fmt(lowY)} ≤ {yLabel} ≤ {fmt(highY)}</small></div><LensAction context={pinned} label="Ask about point / bin"/><label className="camera-toggle"><input type="checkbox" checked={scrollZoom} onChange={e=>setScrollZoom(e.target.checked)}/> Scroll / touch gestures</label></div>
 {view.scale>1.0001&&<div className="camera-navigator"><span>Viewport</span><svg viewBox="0 0 160 64" role="img" aria-label="Position within original plot bounds"><rect width="160" height="64" rx="3" fill="var(--inset)"/>{connected&&valid.length>1?<polyline points={valid.map(p=>`${(p.x-xmin)/(xmax-xmin)*160},${64-(p.y-ymin)/(ymax-ymin)*64}`).join(' ')} fill="none" stroke="var(--muted)" opacity=".55"/>:valid.map((p,i)=><circle key={i} cx={(p.x-xmin)/(xmax-xmin)*160} cy={64-(p.y-ymin)/(ymax-ymin)*64} r="1" fill="var(--muted)"/>)}<rect x={view.x*160} y={(1-view.y-1/view.scale)*64} width={160/view.scale} height={64/view.scale} fill="var(--accent-wash)" stroke="var(--accent)"/></svg><label>Horizontal <input type="range" min="0" max={1-1/view.scale} step="any" value={view.x} onChange={e=>update(v=>clampViewport({...v,x:Number(e.target.value)}))}/></label><label>Vertical <input type="range" min="0" max={1-1/view.scale} step="any" value={view.y} onChange={e=>update(v=>clampViewport({...v,y:Number(e.target.value)}))}/></label></div>}
 <small className="camera-hint">Click a point or bin to pin it for AXIOM · Double-click to zoom · Ctrl/⌘ + scroll · drag or pinch in gesture mode · Home to fit. Zoom explores the existing samples; it does not generate new observations.</small></figure>
}
