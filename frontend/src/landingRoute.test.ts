import {describe,expect,it} from 'vitest';
import {isStudioView} from './landingRoute';
describe('landing route',()=>{
  it('defaults to public landing and only enters studio on its explicit route',()=>{
    expect(isStudioView('')).toBe(false);
    expect(isStudioView('?view=landing')).toBe(false);
    expect(isStudioView('?view=studio')).toBe(true);
    expect(isStudioView('?other=1&view=studio')).toBe(true);
  });
});
