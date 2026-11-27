import { describe, it, expect } from 'vitest';
import { phase, workspaceModules, implementedCapability } from './phase';

describe('Phase 07D capability manifest', () => {
  it('identifies the current candidate development milestone', () => {
    expect(phase).toBe('07D');
    expect(implementedCapability).toContain('experiment lineage');
  });
  it('lists seven workspaces in the bounded release candidate', () => {
    expect(workspaceModules).toHaveLength(7);
    expect(new Set(workspaceModules).size).toBe(7);
  });
});
