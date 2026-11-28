import {describe,it,expect} from 'vitest';
import {answerBlocks} from './AIAnswer';
describe('scientific answer formatting',()=>{
 it('preserves headings and lists',()=>expect(answerBlocks('## Interpretation\nA result.\n\n- One\n- Two\n\n1. Check\n2. Record').map(b=>b.kind)).toEqual(['heading','paragraph','ul','ol']));
 it('preserves multiline code',()=>expect(answerBlocks('```py\na=1\nb=2\n```')[0]).toEqual({kind:'code',lines:['a=1','b=2']}));
 it('keeps untrusted HTML as text',()=>expect(answerBlocks('<script>alert(1)</script>')[0].lines[0]).toBe('<script>alert(1)</script>'));
});
