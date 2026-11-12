import { describe, it, expect } from 'vitest';
import { phase, plannedModules, implementedCapability } from './phase';

describe('Phase 01A capability manifest', () => {
  it('identifies the dataset import milestone', () => {
    expect(phase).toBe('01A');
    expect(implementedCapability).toBe('Dataset import and validation');
  });
  it('lists seven workspaces without claiming scientific analysis exists', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
