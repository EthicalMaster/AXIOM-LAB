/** Current bounded capabilities; release acceptance remains separate from code availability. */
export const phase = '07D' as const;
export const workspaceModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Bounded scientific analysis, experiment lineage, advisory AI, and evidence-only reports' as const;
