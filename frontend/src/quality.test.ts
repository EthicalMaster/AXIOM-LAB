import { expect, it } from 'vitest';
import {percent} from './quality';
it('displays missing percentage with an explicit denominator convention',()=>{
  expect(percent(0)).toBe('0.0%'); expect(percent(12.345)).toBe('12.3%');
});
