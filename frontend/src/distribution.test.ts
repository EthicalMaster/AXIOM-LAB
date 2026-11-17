import { expect, it } from 'vitest';
import {histogramHeight} from './distribution';
it('histogram renders bounded heights without altering frequency data',()=>{
  expect(histogramHeight(5,10)).toBe(50);
  expect(histogramHeight(0,0)).toBe(0);
});
