import {Fragment,type ReactNode} from 'react';
import './ai-refinement.css';

type Block={kind:'heading'|'paragraph'|'ul'|'ol'|'code';lines:string[]};
// Small, deliberately limited Markdown subset. React escapes all provider text.
export function answerBlocks(text:string):Block[]{
  const blocks:Block[]=[];let code=false;
  for(const raw of text.replace(/\r\n?/g,'\n').split('\n')){
    if(/^\s*```/.test(raw)){if(!code)blocks.push({kind:'code',lines:[]});code=!code;continue;}
    if(code){blocks[blocks.length-1].lines.push(raw);continue;}
    const line=raw.trim();if(!line){if(blocks.at(-1)?.kind==='paragraph')blocks.at(-1)!.lines.push('');continue;}
    const heading=line.match(/^#{1,6}\s+(.+)$/),bullet=line.match(/^[-*+]\s+(.+)$/),number=line.match(/^\d+[.)]\s+(.+)$/);
    const kind=heading?'heading':bullet?'ul':number?'ol':'paragraph';const content=(heading||bullet||number)?.[1]??line;
    const previous=blocks.at(-1);
    if(kind!=='heading'&&previous?.kind===kind&&previous.lines.at(-1)!=='')previous.lines.push(content);
    else blocks.push({kind,lines:[content]});
  }
  return blocks.filter(b=>b.lines.some(Boolean));
}
function inline(text:string):ReactNode[]{return text.split(/(\*\*[^*\n]+\*\*|`[^`\n]+`)/g).map((part,i)=>part.startsWith('**')&&part.endsWith('**')&&part.length>4?<strong key={i}>{part.slice(2,-2)}</strong>:part.startsWith('`')&&part.endsWith('`')&&part.length>2?<code key={i}>{part.slice(1,-1)}</code>:<Fragment key={i}>{part}</Fragment>);}
export function AIAnswer({text}:{text:string}){return <div className="axiom-answer-body">{answerBlocks(text).map((b,i)=>{
  if(b.kind==='heading')return <h4 key={i}>{inline(b.lines[0])}</h4>;
  if(b.kind==='code')return <pre key={i}><code>{b.lines.join('\n')}</code></pre>;
  if(b.kind==='ul'||b.kind==='ol'){const Tag=b.kind;return <Tag key={i}>{b.lines.map((line,j)=><li key={j}>{inline(line)}</li>)}</Tag>;}
  return <p key={i}>{inline(b.lines.join('\n').trim())}</p>;
})}</div>}
