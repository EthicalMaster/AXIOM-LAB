import { describe, it, expect } from 'vitest';
import { phase, plannedModules } from './phase';

describe('phase 0 manifest', () => {
  it('identifies the initial phase', () => {
    expect(phase).toBe('00');
  });
  it('lists seven proposed workspaces without claiming implementation', () => {
    expect(plannedModules).toHaveLength(7);
    expect(new Set(plannedModules).size).toBe(7);
  });
});
