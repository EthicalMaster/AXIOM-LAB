import { describe, it, expect } from 'vitest';
import { displayNumber } from './statistics';
describe('scientific display conventions', () => {
  it('distinguishes undefined sample measures from zeros', () => {
    expect(displayNumber(null)).toBe('N/A');
    expect(displayNumber(0)).toBe('0');
  });
  it('formats results without altering backend numeric data', () => {
    expect(displayNumber(2.5)).toBe('2.5');
  });
});
