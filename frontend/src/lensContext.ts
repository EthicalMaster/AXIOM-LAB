export type LensContext={kind:'text'|'metric'|'point'|'bin'|'matrix';label:string;excerpt:string};
export const LENS_EVENT='axiom:lens';
export function boundedText(value:string,limit:number){return Array.from(value.replace(/\s+/g,' ').trim()).slice(0,limit).join('');}
export function makeLens(kind:LensContext['kind'],label:string,excerpt:string):LensContext|null{
 const text=boundedText(excerpt,320);return text?{kind,label:boundedText(label,120)||'Selected content',excerpt:text}:null;
}
export function sendLens(context:LensContext){window.dispatchEvent(new CustomEvent<LensContext>(LENS_EVENT,{detail:context}));}
