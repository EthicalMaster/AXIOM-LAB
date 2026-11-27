import {apiFetch} from './apiClient';
export type QualityColumn = {column:string; inferred_type:string; missing_count:number; present_count:number; missing_percent:number; warnings:string[]};
export type QualityReport = {
  dataset_id:string; method:string; row_count:number; column_count:number;
  missing_cells:number; total_cells:number; completeness_percent:number;
  duplicate_rows:number; duplicate_count_exact:boolean; unique_rows_tracked:number;
  columns:QualityColumn[]; warnings:string[]; note:string;
};
export function percent(value:number):string {return `${value.toFixed(1)}%`;}
export async function fetchQuality(datasetId:string): Promise<QualityReport> {
  const response=await apiFetch(`/api/v1/datasets/${encodeURIComponent(datasetId)}/quality`);
  if(!response.ok) throw new Error(`Data quality check failed (HTTP ${response.status}).`);
  return await response.json() as QualityReport;
}
