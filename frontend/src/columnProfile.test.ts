import { describe, expect, it } from 'vitest';
import { distinctLabel, missingPercent } from './columnProfile';

describe('column inspection display helpers', () => {
  it('reports missing percentages without dividing by zero', () => {
    expect(missingPercent(1, 4)).toBe('25.0%');
    expect(missingPercent(0, 0)).toBe('—');
  });
  it('labels capped distinct counts honestly', () => {
    expect(distinctLabel(3, true)).toBe('3');
    expect(distinctLabel(1000, false)).toBe('>1000');
  });
});
