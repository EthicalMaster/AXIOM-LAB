import {useRef,useState,type FormEvent} from 'react';
import {MathShell,MathAction,useMathRequest} from './MathControls';
import {nfmt} from './Visuals';
type Result={expression:string;value:number;note:string};
const keys=[['7','7'],['8','8'],['9','9'],['÷','/'],['4','4'],['5','5'],['6','6'],['×','*'],['1','1'],['2','2'],['3','3'],['−','-'],['0','0'],['.','.'],['π','pi'],['+','+'],['sin','sin('],['cos','cos('],['√','sqrt('],['ln','log('],['(', '('],[')', ')'],['xʸ','**'],['e','e']];
export function MathWorkbenchPanel(){
 const [expression,setExpression]=useState('2 * (3 + 4)');const input=useRef<HTMLInputElement>(null);const req=useMathRequest<Result>();
 function insert(value:string){const el=input.current,start=el?.selectionStart??expression.length,end=el?.selectionEnd??start;const next=expression.slice(0,start)+value+expression.slice(end);if(next.length>120)return;setExpression(next);requestAnimationFrame(()=>{el?.focus();el?.setSelectionRange(start+value.length,start+value.length)})}
 function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();void req.run('evaluate',{expression})}
 return <MathShell title="Scientific expression" subtitle="Arithmetic, constants and whitelisted functions. Angles in radians; log is natural logarithm." onSubmit={submit} busy={req.busy} error={req.error} result={req.result&&<div className="math-result"><span className="math-kicker">RESULT / NUMERIC</span><div className="math-equation">{req.result.expression}</div><div className="math-big-number">{nfmt(req.result.value)}</div><button type="button" className="retry-button" onClick={()=>setExpression(String(req.result!.value))}>Use result as input</button><p>{req.result.note}</p></div>}>
 <label className="math-field">Expression<input ref={input} className="math-display" value={expression} maxLength={120} required onChange={e=>setExpression(e.target.value)} autoComplete="off"/></label><div className="math-keypad">{keys.map(([label,value])=><button key={label} type="button" onClick={()=>insert(value)}>{label}</button>)}</div><div className="math-presets"><button type="button" onClick={()=>setExpression('')}>Clear</button><button type="button" onClick={()=>setExpression('sin(pi / 2)')}>sin(π/2)</button><button type="button" onClick={()=>setExpression('sqrt(49) + 2**3')}>√49 + 2³</button></div><MathAction busy={req.busy}>Evaluate expression</MathAction>
 </MathShell>;
}
