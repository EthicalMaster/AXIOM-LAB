export type HistogramBin = {lower:number;upper:number;count:number;percent:number};
export type DistributionReport = {
  dataset_id:string;column:string;method:string;count:number;missing_count:number;
  minimum:number; maximum:number; median:number;q1:number;q3:number;
  bin_count:number; bins:HistogramBin[]; outlier_count:number|null;
  outlier_method:string;warnings:string[];note:string;
};
export async function fetchDistribution(datasetId:string,column:string):Promise<DistributionReport> {
  const request=`/api/v1/datasets/${encodeURIComponent(datasetId)}/distribution?column=${encodeURIComponent(column)}`;
  const response=await fetch(request);
  const payload:unknown=await response.json();
  if(!response.ok) throw new Error(`Distribution unavailable (HTTP ${response.status}).`);
  return payload as DistributionReport;
}
export function histogramHeight(count:number,maxCount:number):number {
  return maxCount>0?Math.round(100*count/maxCount):0;
}
