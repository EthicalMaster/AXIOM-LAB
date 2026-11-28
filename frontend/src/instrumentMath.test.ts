import {describe, expect, it} from 'vitest';
import {intervalMass, normalDensity} from './instrumentMath';
describe('public probability instrument',()=>{
  it('matches the standard normal one-sigma probability',()=>expect(intervalMass(0,1)).toBeCloseTo(.682689492,7));
  it('is symmetric when the mean is reflected',()=>expect(intervalMass(2,1)).toBeCloseTo(intervalMass(-2,1),12));
  it('reduces central mass as spread increases',()=>expect(intervalMass(0,.6)).toBeGreaterThan(intervalMass(0,2.5)));
  it('rejects invalid standard deviations',()=>expect(()=>normalDensity(0,0,0)).toThrow(RangeError));
  it('returns zero for a zero-width interval',()=>expect(intervalMass(0,1,1,1)).toBe(0));
});
