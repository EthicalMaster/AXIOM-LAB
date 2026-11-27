export type Viewport = {x:number;y:number;scale:number};
export const initialViewport:Viewport={x:0,y:0,scale:1};
export function clampViewport(v:Viewport):Viewport {
 const scale=Math.min(16,Math.max(1,v.scale));
 return {scale,x:Math.min(1-1/scale,Math.max(0,v.x)),y:Math.min(1-1/scale,Math.max(0,v.y))};
}
export function zoomViewport(v:Viewport,factor:number,ax=.5,ay=.5):Viewport {
 const scale=Math.min(16,Math.max(1,v.scale*factor));
 return clampViewport({scale,x:v.x+ax*(1/v.scale-1/scale),y:v.y+ay*(1/v.scale-1/scale)});
}
export function panViewport(v:Viewport,dx:number,dy:number):Viewport {
 return clampViewport({...v,x:v.x-dx/v.scale,y:v.y+dy/v.scale});
}
