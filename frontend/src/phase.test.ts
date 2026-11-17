import { describe, it, expect } from 'vitest';
import { phase, plannedModules, implementedCapability } from './phase';

describe('Phase 01D capability manifest', () => {
  it('identifies the dataset inspection milestone', () => {
    expect(phase).toBe('01D');
    expect(implementedCapability).toBe('Dataset import, numerical statistics, charting and minimal experiment persistence');
  });
  it('lists seven workspaces without claiming scientific analysis exists', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
