export type Viewport = {x:number;y:number;scale:number};
export const initialViewport:Viewport={x:0,y:0,scale:1};
export const MAX_ZOOM=64;
export function clampViewport(v:Viewport):Viewport {
 const scale=Math.min(MAX_ZOOM,Math.max(1,v.scale));
 return {scale,x:Math.min(1-1/scale,Math.max(0,v.x)),y:Math.min(1-1/scale,Math.max(0,v.y))};
}
export function zoomViewport(v:Viewport,factor:number,ax=.5,ay=.5):Viewport {
 const scale=Math.min(MAX_ZOOM,Math.max(1,v.scale*factor));
 return clampViewport({scale,x:v.x+ax*(1/v.scale-1/scale),y:v.y+ay*(1/v.scale-1/scale)});
}
export function panViewport(v:Viewport,dx:number,dy:number):Viewport {
 return clampViewport({...v,x:v.x-dx/v.scale,y:v.y+dy/v.scale});
}
// Interpolate the visible extent, not the magnification: this keeps an anchored zoom stable.
export function interpolateViewport(a:Viewport,b:Viewport,t:number):Viewport {
 const mix=(x:number,y:number)=>x+(y-x)*t;
 return clampViewport({x:mix(a.x,b.x),y:mix(a.y,b.y),scale:1/mix(1/a.scale,1/b.scale)});
}
export function pinchViewport(v:Viewport,factor:number,fromX:number,fromY:number,toX:number,toY:number):Viewport {
 const next=zoomViewport(v,factor,fromX,fromY);
 return clampViewport({...next,x:v.x+fromX/v.scale-toX/next.scale,y:v.y+fromY/v.scale-toY/next.scale});
}
export function axisTicks(low:number,high:number,count=5):number[]{
 const raw=(high-low)/count;if(!(raw>0)||!Number.isFinite(raw))return [low];
 const power=10**Math.floor(Math.log10(raw));
 const step=([1,2,2.5,5,10].find(n=>n*power>=raw)??10)*power;
 if(!(step>0)||!Number.isFinite(step))return [low];
 const start=Math.ceil(low/step),end=Math.floor(high/step);
 return Array.from({length:Math.max(0,Math.min(20,end-start+1))},(_,i)=>(start+i)*step);
}
