/** Current candidate capabilities; future phases remain in plannedModules. */
export const phase = '05A' as const;
export const plannedModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Dataset analysis, guarded inference, bounded mathematics, ML baselines, and experiment history' as const;
