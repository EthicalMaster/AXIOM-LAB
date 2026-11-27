import {describe,it,expect} from 'vitest';
import {initialViewport,zoomViewport,panViewport} from './plotViewport';
describe('interactive plot camera',()=>{
 it('zooms around centre and resets at full extent',()=>{const v=zoomViewport(initialViewport,2);expect(v).toEqual({scale:2,x:.25,y:.25});expect(zoomViewport(v,.5)).toEqual(initialViewport)});
 it('preserves pointer anchor during zoom',()=>{const v=zoomViewport(initialViewport,4,.25,.75);expect(v.x+.25/v.scale).toBeCloseTo(.25);expect(v.y+.75/v.scale).toBeCloseTo(.75)});
 it('clamps panning to original data bounds',()=>{const v=zoomViewport(initialViewport,2);expect(panViewport(v,99,-99)).toEqual({scale:2,x:0,y:0});expect(panViewport(v,-99,99)).toEqual({scale:2,x:.5,y:.5})});
 it('caps zoom and never zooms below original extent',()=>{expect(zoomViewport(initialViewport,100).scale).toBe(16);expect(zoomViewport(initialViewport,.001)).toEqual(initialViewport)});
});
