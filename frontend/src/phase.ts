/** Capability manifest. Phase 01B adds structural column profiling, not statistics. */
export const phase = '02A' as const;
export const plannedModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Dataset import, quality profiling, descriptive statistics and saved chart runs' as const;
