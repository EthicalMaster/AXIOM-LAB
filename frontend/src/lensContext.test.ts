import {describe,it,expect} from 'vitest';
import {makeLens,boundedText} from './lensContext';
describe('Lens context',()=>{
 it('bounds excerpts and labels',()=>{expect(makeLens('text','x'.repeat(150),'y'.repeat(400))).toEqual({kind:'text',label:'x'.repeat(120),excerpt:'y'.repeat(320)})});
 it('rejects empty selections',()=>expect(makeLens('text','label','  \n ')).toBeNull());
 it('preserves complete Unicode code points',()=>expect(boundedText('🧪🧪',1)).toBe('🧪'));
});
