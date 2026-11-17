import { describe, it, expect } from 'vitest';
import { phase, plannedModules, implementedCapability } from './phase';

describe('Phase 02A capability manifest', () => {
  it('identifies the dataset inspection milestone', () => {
    expect(phase).toBe('02A');
    expect(implementedCapability).toBe('Dataset import, quality profiling, descriptive statistics and saved chart runs');
  });
  it('lists seven workspaces without claiming scientific analysis exists', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
