import { expect, it } from 'vitest';
import {coordinates} from './experiments';
it('observation series respects input order',()=>{
  const path=coordinates([{x:1,y:10},{x:2,y:15},{x:3,y:20}]);
  expect(path.split(' ')).toHaveLength(3);
  expect(path).toMatch(/^36\.0,202\.0/);
});
it('empty chart draws no geometry',()=>expect(coordinates([])).toBe(''));
