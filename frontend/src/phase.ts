/** Capability manifest. Phase 01B adds structural column profiling, not statistics. */
export const phase = '01C' as const;
export const plannedModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Dataset import, profiling and descriptive statistics' as const;
