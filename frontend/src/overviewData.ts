import type { ImportedDataset } from './datasets';
import type { DatasetColumnProfile } from './columnProfile';

/** Preserve row positions and skip blanks; do not coerce missing cells to zero. */
export function previewPoints(dataset: Pick<ImportedDataset,'headers'|'preview'>, column: string) {
  const index = dataset.headers.indexOf(column);
  if (index < 0) return [];
  return dataset.preview.flatMap((row,i) => {
    const raw = row[index];
    const y = raw == null || raw.trim() === '' ? NaN : Number(raw);
    return Number.isFinite(y) ? [{x:i+1,y}] : [];
  });
}
export function profileSummary(profile: DatasetColumnProfile | null) {
  if (!profile) return {missing:0, completeness:null, types:[] as [string,number][]};
  let missing=0, total=0;
  const types:Record<string,number> = {};
  for (const c of profile.columns) {
    missing += c.missing_count;
    total += c.missing_count + c.non_missing_count;
    types[c.inferred_type] = (types[c.inferred_type] ?? 0) + 1;
  }
  return {missing, completeness:total ? 100*(total-missing)/total : null, types:Object.entries(types)};
}
