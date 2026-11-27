import {apiFetch} from './apiClient';
export type InferredType = 'numeric' | 'boolean' | 'datetime' | 'categorical' | 'mixed' | 'empty';

export type ColumnInformation = {
  name: string;
  inferred_type: InferredType;
  non_missing_count: number;
  missing_count: number;
  distinct_count: number;
  distinct_count_exact: boolean;
  examples: string[];
  warnings: string[];
};

export type DatasetColumnProfile = {
  dataset_id: string;
  row_count: number;
  column_count: number;
  worksheet: string | null;
  columns: ColumnInformation[];
  method_note: string;
};

export function missingPercent(missing: number, total: number): string {
  return total > 0 ? `${((missing / total) * 100).toFixed(1)}%` : '—';
}

export function distinctLabel(count: number, exact: boolean): string {
  return exact ? String(count) : `>${count}`;
}

export async function fetchColumnProfile(datasetId: string): Promise<DatasetColumnProfile> {
  if (!/^[0-9a-f]{32}$/.test(datasetId)) throw new Error('Invalid dataset ID.');
  const response = await apiFetch(`/api/v1/datasets/${datasetId}/profile`);
  const payload: unknown = await response.json();
  return payload as DatasetColumnProfile;
}
