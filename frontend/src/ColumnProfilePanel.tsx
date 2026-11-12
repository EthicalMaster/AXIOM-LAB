import { distinctLabel, missingPercent, type DatasetColumnProfile } from './columnProfile';

type Props = { data: DatasetColumnProfile };

export function ColumnProfilePanel({ data }: Props) {
  return (
    <section className="profile-panel" aria-labelledby="column-profile-title">
      <div className="preview-heading profile-heading">
        <h3 id="column-profile-title">Column inspection</h3>
        <span>PHASE 01B · STRUCTURAL INFERENCE</span>
      </div>
      <p className="profile-description">These types are hints based on observed values, not declared measurement types. Empty cells count as missing; literal tokens such as NA remain text.</p>
      <div className="table-scroll" tabIndex={0} aria-label="Column profile table, horizontally scrollable">
        <table className="data-table profile-table">
          <thead><tr><th scope="col">Column</th><th scope="col">Detected type</th><th scope="col">Present</th><th scope="col">Missing</th><th scope="col">Distinct</th><th scope="col">Examples</th></tr></thead>
          <tbody>{data.columns.map((col, index) => (
            <tr key={`${index}-${col.name}`}>
              <th scope="row">{col.name}</th>
              <td><span className={`type-chip type-${col.inferred_type}`}>{col.inferred_type}</span></td>
              <td>{col.non_missing_count.toLocaleString()}</td>
              <td>{col.missing_count.toLocaleString()} <span className="dim-number">({missingPercent(col.missing_count, data.row_count)})</span></td>
              <td>{distinctLabel(col.distinct_count, col.distinct_count_exact)}</td>
              <td>{col.examples.length ? col.examples.join(' · ') : <span className="missing">None</span>}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      {data.columns.some(col => col.warnings.length > 0) && (
        <div className="warning-panel profile-warnings" role="note">
          <strong>Inspection notes</strong>
          <ul>{data.columns.flatMap((col, i) => col.warnings.map((note, j) => <li key={`${i}-${j}`}><strong>{col.name}:</strong> {note}</li>))}</ul>
        </div>
      )}
      <p className="preview-note">{data.method_note} A distinct count shown with &gt; is a lower bound, not an exact total.</p>
    </section>
  );
}
