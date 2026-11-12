/** Capability manifest. Phase 01A implements dataset import, not analytics. */
export const phase = '01A' as const;
export const plannedModules = [
  'Data Lab',
  'Statistics Lab',
  'Visualization Studio',
  'Mathematical Workbench',
  'Machine Learning Studio',
  'Experiment Engine',
  'Scientific Reporting',
] as const;
export const implementedCapability = 'Dataset import and validation' as const;
