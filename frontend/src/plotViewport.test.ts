import {describe,it,expect} from 'vitest';
import {initialViewport,zoomViewport,panViewport,interpolateViewport,pinchViewport,axisTicks} from './plotViewport';
describe('interactive plot camera',()=>{
 it('zooms around centre and resets at full extent',()=>{const v=zoomViewport(initialViewport,2);expect(v).toEqual({scale:2,x:.25,y:.25});expect(zoomViewport(v,.5)).toEqual(initialViewport)});
 it('preserves pointer anchor during zoom',()=>{const v=zoomViewport(initialViewport,4,.25,.75);expect(v.x+.25/v.scale).toBeCloseTo(.25);expect(v.y+.75/v.scale).toBeCloseTo(.75)});
 it('clamps panning to original data bounds',()=>{const v=zoomViewport(initialViewport,2);expect(panViewport(v,99,-99)).toEqual({scale:2,x:0,y:0});expect(panViewport(v,-99,99)).toEqual({scale:2,x:.5,y:.5})});
 it('caps zoom and never zooms below original extent',()=>{expect(zoomViewport(initialViewport,100).scale).toBe(64);expect(zoomViewport(initialViewport,.001)).toEqual(initialViewport)});
});

describe('smooth camera',()=>{
 it('preserves anchored coordinates during the transition',()=>{const end=zoomViewport(initialViewport,4,.3,.7);const half=interpolateViewport(initialViewport,end,.5);expect(half.x+.3/half.scale).toBeCloseTo(.3);expect(half.y+.7/half.scale).toBeCloseTo(.7)});
 it('moves the data point under a translating pinch midpoint',()=>{const v=zoomViewport(initialViewport,2);const p=pinchViewport(v,1.5,.5,.5,.6,.4);expect(p.x+.6/p.scale).toBeCloseTo(v.x+.5/v.scale);expect(p.y+.4/p.scale).toBeCloseTo(v.y+.5/v.scale)});
 it('returns readable bounded ticks',()=>{expect(axisTicks(-3,7)).toEqual([-2,0,2,4,6]);expect(axisTicks(1,1)).toEqual([1]);expect(axisTicks(.001,.009).every(n=>n>=.001&&n<=.009)).toBe(true)});
});
