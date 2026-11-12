import { describe, expect, it } from 'vitest';
import { clientFileError, fileSizeLabel } from './datasets';

describe('file selection guidance (server remains authoritative)', () => {
  it('recognises supported formats case insensitively', () => {
    expect(clientFileError('experiment.CSV', 100)).toBeNull();
    expect(clientFileError('experiment.xlsx', 100)).toBeNull();
    expect(clientFileError('experiment.xls', 100)).toBeNull();
  });
  it('rejects unsupported/empty/oversized files early', () => {
    expect(clientFileError('x.exe', 100)).toContain('CSV');
    expect(clientFileError('x.csv', 0)).toContain('empty');
    expect(clientFileError('x.csv', 5 * 1024 * 1024 + 1)).toContain('5 MiB');
  });
  it('formats byte sizes for the upload panel', () => {
    expect(fileSizeLabel(512)).toBe('512 B');
    expect(fileSizeLabel(2048)).toBe('2.0 KiB');
  });
});
