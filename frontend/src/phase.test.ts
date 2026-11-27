import { describe, it, expect } from 'vitest';
import { phase, plannedModules, implementedCapability } from './phase';

describe('Phase 05A capability manifest', () => {
  it('identifies the current candidate development milestone', () => {
    expect(phase).toBe('05A');
    expect(implementedCapability).toBe('Dataset analysis, guarded inference, bounded mathematics, ML baselines, and experiment history');
  });
  it('lists seven workspaces with reporting still planned', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
