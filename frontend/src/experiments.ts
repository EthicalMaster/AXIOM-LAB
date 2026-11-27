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
  if (!response.ok) throw new Error(`Experiment not saved (HTTP ${response.status}).`);
  return data as SavedExperiment;
}
export async function reopenExperiment(id: string): Promise<SavedExperiment> {
  const response = await apiFetch(`/api/v1/experiments/${encodeURIComponent(id)}`);
  if (!response.ok) throw new Error(`Cannot reopen experiment (HTTP ${response.status}).`);
  return await response.json() as SavedExperiment;
}
/** Preserve data values; viewBox conversion is for SVG geometry only. */
export function coordinates(points: Point[], width = 720, height = 230): string {
  if (points.length === 0) return '';
  const ys = points.map(p=>p.y); const xs = points.map(p=>p.x);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const scaleX = (x:number) => 36 + (x-minX)/(maxX-minX||1)*(width-56);
  const scaleY = (y:number) => height-28 - (y-minY)/(maxY-minY||1)*(height-50);
  return points.map(p=>`${scaleX(p.x).toFixed(1)},${scaleY(p.y).toFixed(1)}`).join(' ');
}
