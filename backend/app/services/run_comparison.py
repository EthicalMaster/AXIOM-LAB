"""Only compare values when the stored methods and measurement axes match."""
from __future__ import annotations
from math import fsum, isfinite


def compare_runs(left: dict, right: dict) -> dict:
    a, b = left['result'], right['result']
    compatible = (left['method'] == right['method'] and
                  a.get('column') == b.get('column') and
                  a.get('original_point_count') == b.get('original_point_count') and
                  [p['x'] for p in a.get('points', [])] == [p['x'] for p in b.get('points', [])])
    summary = {
        'left_id': left['id'], 'right_id': right['id'],
        'left_revision': left['revision'], 'right_revision': right['revision'],
        'left_configuration': left['configuration'], 'right_configuration': right['configuration'],
        'comparable': compatible, 'method': left['method'] if compatible else None,
        'comparison': None, 'warnings': [],
    }
    if not compatible:
        summary['warnings'].append('Methods, columns, observation counts, or sampled positions differ; numeric comparison withheld.')
        return summary
    differences = [abs(p['y'] - q['y']) for p, q in zip(a['points'], b['points'])]
    if any(not isfinite(d) for d in differences):
        summary['warnings'].append('Difference exceeds floating-point range; numeric comparison withheld.')
        return summary
    if not differences:
        summary['warnings'].append('No chart points are available to compare.')
        return summary
    summary['comparison'] = {
        'points_compared': len(differences),
        'identical_values': all(x == 0 for x in differences),
        'mean_absolute_difference': fsum(d / len(differences) for d in differences),
        'maximum_absolute_difference': max(differences),
        'sampled': a['sampled'] or b['sampled'],
    }
    if summary['comparison']['sampled']:
        summary['warnings'].append('Difference metrics cover only displayed sampled points, not every original observation.')
    return summary
