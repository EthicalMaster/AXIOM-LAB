import { describe, it, expect } from 'vitest';
import { phase, plannedModules, implementedCapability } from './phase';

describe('Phase 01B capability manifest', () => {
  it('identifies the dataset inspection milestone', () => {
    expect(phase).toBe('01B');
    expect(implementedCapability).toBe('Dataset import, validation and column profiling');
  });
  it('lists seven workspaces without claiming scientific analysis exists', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
