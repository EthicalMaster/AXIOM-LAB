export type DatasetMetadata = {
  id: string;
  original_name: string;
  format: string;
  sha256: string;
  size_bytes: number;
  uploaded_at: string;
  row_count: number;
  column_count: number;
  headers: string[];
  worksheet: string | null;
  sheet_names: string[];
  warnings: string[];
};
export type ImportedDataset = DatasetMetadata & { preview: (string | null)[][] };

const MAX_FILE_BYTES = 5 * 1024 * 1024;

export function clientFileError(filename: string, size: number): string | null {
  if (!/\.(csv|xlsx|xls)$/i.test(filename)) return 'Choose a CSV, XLSX or XLS file.';
  if (size === 0) return 'The selected file is empty.';
  if (size > MAX_FILE_BYTES) return 'This file exceeds the 5 MiB upload limit.';
  return null;
}

export function fileSizeLabel(bytes: number): string {
  return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KiB`;
}

export async function importDataset(file: File): Promise<ImportedDataset> {
  const form = new FormData();
  form.append('file', file);
  const response = await fetch('/api/v1/datasets/import', { method: 'POST', body: form });
  const payload: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload
      ? (payload as { detail?: unknown }).detail : undefined;
    if (typeof detail === 'object' && detail !== null && 'message' in detail && typeof detail.message === 'string') {
      throw new Error(detail.message);
    }
    throw new Error(`Upload failed (HTTP ${response.status}).`);
  }
  return payload as ImportedDataset;
}
