export type NumericalColumnStatistics = {
  column: string; count: number; missing_count: number;
  mean: number; median: number; minimum: number; maximum: number;
  q1: number; q3: number; iqr: number;
  population_variance: number; population_stddev: number;
  sample_variance: number | null; sample_stddev: number | null; notes: string[];
};
export type DatasetStatistics = {
  dataset_id: string; method: string; row_count: number;
  columns: NumericalColumnStatistics[]; note: string;
};
export function displayNumber(value: number | null): string {
  if (value === null) return 'N/A';
  return new Intl.NumberFormat('en-US', {maximumSignificantDigits: 6}).format(value);
}
export async function fetchStatistics(datasetId: string): Promise<DatasetStatistics> {
  if (!/^[0-9a-f]{32}$/.test(datasetId)) throw new Error('Invalid dataset ID.');
  const response = await fetch(`/api/v1/datasets/${datasetId}/statistics`);
  const payload: unknown = await response.json();
  if (!response.ok) throw new Error(`Statistics unavailable (HTTP ${response.status}).`);
  return payload as DatasetStatistics;
}
