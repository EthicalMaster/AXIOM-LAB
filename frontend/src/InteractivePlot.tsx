import {useEffect,useId,useRef,useState,type PointerEvent} from 'react';
import {displayNumber} from './statistics';
import {initialViewport,panViewport,zoomViewport} from './plotViewport';
type Point={x:number;y:number};
type Bin={lower:number;upper:number;count:number};
type Props={points:Point[];label:string;xLabel:string;yLabel:string;connected?:boolean;diagonal?:boolean;bins?:Bin[];xDomain?:[number,number];yDomain?:[number,number]};
const left=65,top=24,width=505,height=188;
const fmt=displayNumber;
function range(values:number[],given?:[number,number]):[number,number]{
 const lo=given?.[0]??Math.min(...values),hi=given?.[1]??Math.max(...values);
 if(lo!==hi)return [lo,hi];
 const pad=Math.max(1,Math.abs(lo)*.01);return [lo-pad,hi+pad];
}
export function InteractivePlot(props:Props){
 const {points,bins,label,xLabel,yLabel,connected,diagonal,xDomain,yDomain}=props;
 const valid=points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y));
 const actualBins=bins?.filter(b=>Number.isFinite(b.lower)&&Number.isFinite(b.upper)&&Number.isFinite(b.count))??[];
 const valuesX=valid.map(p=>p.x),valuesY=valid.map(p=>p.y);
 const hasData=valid.length>0||actualBins.length>0;
 const [xmin,xmax]=range(hasData?[...valuesX,...actualBins.flatMap(b=>[b.lower,b.upper]),...(diagonal?valuesY:[])]:[0,1],xDomain);
 const [ymin,ymax]=range(hasData?[...valuesY,...(actualBins.length?[0,...actualBins.map(b=>b.count)]:[]),...(diagonal?valuesX:[])]:[0,1],yDomain);
 const [view,setView]=useState(initialViewport);
 const [hover,setHover]=useState<Point|null>(null);
 const [dragging,setDragging]=useState(false);
 const drag=useRef<{id:number;x:number;y:number}|null>(null);
 const svg=useRef<SVGSVGElement>(null);const clip=useId();
 useEffect(()=>{setView(initialViewport);setHover(null)},[label,xLabel,yLabel,xmin,xmax,ymin,ymax]);
 const X=(x:number)=>left+((x-xmin)/(xmax-xmin)-view.x)*view.scale*width;
 const Y=(y:number)=>top+height-((y-ymin)/(ymax-ymin)-view.y)*view.scale*height;
 const at=(e:PointerEvent<SVGSVGElement>)=>{const matrix=e.currentTarget.getScreenCTM();return matrix?new DOMPoint(e.clientX,e.clientY).matrixTransform(matrix.inverse()):null;};
 useEffect(()=>{const el=svg.current;if(!el)return;const wheel=(e:WheelEvent)=>{if(!e.ctrlKey&&!e.metaKey)return;e.preventDefault();const matrix=el.getScreenCTM();if(!matrix)return;const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(matrix.inverse());setView(v=>zoomViewport(v,Math.exp(-e.deltaY*.005),Math.max(0,Math.min(1,(p.x-left)/width)),Math.max(0,Math.min(1,1-(p.y-top)/height))));};el.addEventListener('wheel',wheel,{passive:false});return()=>el.removeEventListener('wheel',wheel)},[hasData]);
 if(!hasData)return <p className="intel-empty">No plottable values.</p>;
 function end(){drag.current=null;setDragging(false)}
 return <figure className="visual-figure interactive-figure"><div className="plot-header"><figcaption>{label}</figcaption><div className="plot-tools" role="group" aria-label="Plot controls"><button type="button" title="Zoom out" aria-label="Zoom out" disabled={view.scale===1} onClick={()=>setView(v=>zoomViewport(v,1/1.5))}>−</button><output aria-label="Zoom level">{view.scale.toFixed(1)}×</output><button type="button" title="Zoom in" aria-label="Zoom in" disabled={view.scale>=16} onClick={()=>setView(v=>zoomViewport(v,1.5))}>+</button><button type="button" title="Reset plot" onClick={()=>setView(initialViewport)}>Reset</button></div></div>
 <svg ref={svg} viewBox="0 0 600 260" className={`interactive-plot${view.scale>1?' zoomed':''}${dragging?' dragging':''}`} role="img" aria-label={`${label}. ${xLabel} and ${yLabel}. Zoom with controls, pan with arrow keys.`} tabIndex={0}
 onKeyDown={e=>{const directions:Record<string,[number,number]>={ArrowLeft:[.15,0],ArrowRight:[-.15,0],ArrowUp:[0,.15],ArrowDown:[0,-.15]};if(e.key in directions){e.preventDefault();setView(v=>panViewport(v,...directions[e.key]));}else if(e.key==='+'||e.key==='='){e.preventDefault();setView(v=>zoomViewport(v,1.5))}else if(e.key==='-'){e.preventDefault();setView(v=>zoomViewport(v,1/1.5))}else if(e.key==='Home'){e.preventDefault();setView(initialViewport)}}}
 onPointerDown={e=>{if(e.button!==0||view.scale===1)return;const p=at(e);if(!p||p.x<left||p.x>left+width||p.y<top||p.y>top+height)return;drag.current={id:e.pointerId,x:p.x,y:p.y};e.currentTarget.setPointerCapture(e.pointerId);setDragging(true);setHover(null)}}
 onPointerMove={e=>{const p=at(e);if(!p)return;const d=drag.current;if(d&&d.id===e.pointerId){const dx=(p.x-d.x)/width,dy=(p.y-d.y)/height;drag.current={id:d.id,x:p.x,y:p.y};setView(v=>panViewport(v,dx,dy));return}if(p.x<left||p.x>left+width||p.y<top||p.y>top+height){setHover(null);return}let closest:Point|null=null;let best=12;for(const v of valid){const dist=Math.hypot(X(v.x)-p.x,Y(v.y)-p.y);if(dist<best){best=dist;closest=v}}setHover(closest)}} onPointerUp={end} onPointerCancel={end} onLostPointerCapture={end} onPointerLeave={()=>setHover(null)}>
 <defs><clipPath id={clip}><rect x={left} y={top} width={width} height={height}/></clipPath></defs>
 {[0,.25,.5,.75,1].map(t=><g key={t}><line x1={left} x2={left+width} y1={top+height-t*height} y2={top+height-t*height} stroke="var(--line)" strokeDasharray="3 4"/><line x1={left+t*width} x2={left+t*width} y1={top} y2={top+height} stroke="var(--line)" opacity=".35"/><text x={left-5} y={top+height-t*height+4} textAnchor="end">{fmt(ymin+(view.y+t/view.scale)*(ymax-ymin))}</text><text x={left+t*width} y={top+height+17} textAnchor={t===0?'start':t===1?'end':'middle'}>{fmt(xmin+(view.x+t/view.scale)*(xmax-xmin))}</text></g>)}
 <g clipPath={`url(#${clip})`}>{diagonal&&<line x1={X(xmin)} y1={Y(xmin)} x2={X(xmax)} y2={Y(xmax)} stroke="var(--violet)" strokeDasharray="5 4"/>}{connected&&<polyline points={valid.map(p=>`${X(p.x)},${Y(p.y)}`).join(' ')} fill="none" stroke="var(--accent)" strokeWidth="2"/>}{valid.map((p,i)=><circle key={i} cx={X(p.x)} cy={Y(p.y)} r={connected?2:4} fill="var(--accent)"><title>{xLabel}: {p.x}; {yLabel}: {p.y}</title></circle>)}{actualBins.map((b,i)=><rect key={i} x={X(b.lower)} y={Y(b.count)} width={Math.max(1,X(b.upper)-X(b.lower)-1)} height={Math.max(0,Y(0)-Y(b.count))} fill="var(--cyan)" opacity=".8"><title>{b.lower}–{b.upper}: {b.count}</title></rect>)}{hover&&<circle cx={X(hover.x)} cy={Y(hover.y)} r="6" fill="var(--accent)" stroke="var(--ink)"/>}</g><text x={left} y="13">{yLabel}</text><text x={left+width/2} y="253" textAnchor="middle">{xLabel}</text></svg>
 <div className="plot-note">{hover?`${xLabel}: ${fmt(hover.x)} · ${yLabel}: ${fmt(hover.y)}`:'Zoom + / −, drag to pan; Ctrl/⌘ + scroll or arrow keys.'}</div></figure>
}
