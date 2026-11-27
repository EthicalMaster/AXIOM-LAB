/** Capability manifest. Phase 01B adds structural column profiling, not statistics. */
export const phase = '04B' as const;
export const plannedModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Dataset import, statistics, quality profiling, histogram distributions and saved chart runs' as const;
