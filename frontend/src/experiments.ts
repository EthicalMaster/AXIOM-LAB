import {apiFetch} from './apiClient';
export type Point = {x: number; y: number};
export type SequenceChart = {
  method: string; column: string; x_label: string; y_label: string;
  original_point_count: number; shown_point_count: number;
  sampled: boolean; missing_count: number; points: Point[]; note: string;
};
export type SavedExperiment = {
  id: string; name: string; dataset_id: string; dataset_sha256: string; created_at: string;
  run: {
    id: string; created_at: string; status: string; method: string;
    configuration: {column: string; chart_kind: string};
    result: SequenceChart; environment: Record<string, string>;
  };
};
export async function saveExperiment(datasetId: string, column: string, name: string): Promise<SavedExperiment> {
  const response = await apiFetch('/api/v1/experiments', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({dataset_id: datasetId, column, name})
  });
  const data: unknown = await response.json();
  return data as SavedExperiment;
}
export async function reopenExperiment(id: string): Promise<SavedExperiment> {
  const response = await apiFetch(`/api/v1/experiments/${encodeURIComponent(id)}`);
  return await response.json() as SavedExperiment;
}
