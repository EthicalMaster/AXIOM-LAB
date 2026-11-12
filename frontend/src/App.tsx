import { ChangeEvent, FormEvent, useEffect, useState } from 'react';
import { phase, plannedModules } from './phase';
import { clientFileError, fileSizeLabel, importDataset, type ImportedDataset } from './datasets';

type Connection = 'checking' | 'connected' | 'unavailable';
type Health = { status: string; phase: string; scientific_engine: string };

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportedDataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/v1/health', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error('Backend not responding');
        return res.json() as Promise<Health>;
      })
      .then((data) => {
        setConnection(data.status === 'ok' && data.scientific_engine === 'not_implemented' ? 'connected' : 'unavailable');
      })
      .catch((e: unknown) => {
        if (e instanceof Error && e.name === 'AbortError') return;
        setConnection('unavailable');
      });
    return () => controller.abort();
  }, []);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setResult(null);
    setError(file ? clientFileError(file.name, file.size) : null);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || uploading) return;
    const validationError = clientFileError(selectedFile.name, selectedFile.size);
    if (validationError) { setError(validationError); return; }
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await importDataset(selectedFile));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Dataset upload could not be completed.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="site-shell">
      <header className="topbar">
        <div className="wordmark"><span className="glyph" aria-hidden="true">∴</span> AXIOM <span className="thin">LAB</span></div>
        <span className="top-label">SCIENTIFIC WORKSPACE <span className="divider-label">/</span> {phase}</span>
      </header>

      <section className="hero" aria-labelledby="project-title">
        <div className="eyebrow"><span className="tiny-line"/> DATA LAB <span className="subtle">/ FIRST COMPUTATIONAL WORKFLOW</span></div>
        <h1 id="project-title">Begin with <em>evidence.</em></h1>
        <p className="lead">A scientific experiment starts with trustworthy input. Import a dataset, check its structure, and preserve the original file before any analysis begins.</p>
        <div className="statuses">
          <span className="status"><span className="dot ready" aria-hidden="true"/>Phase 01A · Import available</span>
          <span className="status" role="status" aria-live="polite"><span className={`dot ${connection}`} aria-hidden="true"/>API {connection === 'checking' ? 'checking…' : connection === 'connected' ? 'connected' : 'unavailable'}</span>
        </div>
      </section>

      <section className="lab-workspace" aria-labelledby="data-lab-title">
        <div className="section-topline"><h2 id="data-lab-title">01 / Data Lab</h2><span>ACTIVE CAPABILITY — FILE VALIDATION</span></div>
        <div className="lab-grid">
          <div className="upload-panel">
            <span className="panel-kicker">INPUT / 01</span>
            <h3>Import a dataset</h3>
            <p className="panel-text">CSV, XLSX or XLS. Maximum 5 MiB, 50,000 data rows and 150 columns. The server validates your file before storing its original bytes.</p>
            <form onSubmit={submit} className="upload-form">
              <label className="input-label" htmlFor="dataset-file">Dataset file</label>
              <input id="dataset-file" className="file-picker" type="file" accept=".csv,.xlsx,.xls" disabled={uploading} onChange={selectFile} aria-describedby="file-hint" />
              <p id="file-hint" className="file-hint">{selectedFile ? `${selectedFile.name} · ${fileSizeLabel(selectedFile.size)}` : 'Select a file from your computer. No sample data is fabricated.'}</p>
              <button className="primary-button" type="submit" disabled={!selectedFile || uploading || connection !== 'connected' || Boolean(error)}>
                {uploading ? 'Validating dataset…' : 'Validate and import'} <span aria-hidden="true">↗</span>
              </button>
            </form>
            {error && <div className="inline-alert error" role="alert"><strong>Import not completed.</strong><p>{error}</p></div>}
            {result && <div className="inline-alert success" role="status"><strong>Dataset preserved.</strong><p>Original file saved with a unique dataset ID and SHA-256 fingerprint.</p></div>}
          </div>

          <aside className="method-panel" aria-label="Import methodology">
            <span className="panel-kicker">PROTOCOL / DATA INTEGRITY</span>
            <h3>Check before you compute.</h3>
            <ol className="protocol-list">
              <li><span>01</span> Confirm supported file format and bounded size</li>
              <li><span>02</span> Read headers and verify consistent dataset structure</li>
              <li><span>03</span> Record file fingerprint and store original bytes</li>
              <li><span>04</span> Preview the first rows without transforming the source</li>
            </ol>
            <div className="method-footnote">No statistical inference, cleaning, or model training occurs in this phase.</div>
          </aside>
        </div>
      </section>

      {result && <section className="results" aria-labelledby="result-title">
        <div className="section-topline"><h2 id="result-title">Validated dataset</h2><span>ORIGINAL / IMMUTABLE</span></div>
        <div className="metadata-grid">
          <div><span>DATA ROWS</span><strong>{result.row_count.toLocaleString()}</strong></div>
          <div><span>COLUMNS</span><strong>{result.column_count}</strong></div>
          <div><span>FORMAT</span><strong>{result.format.toUpperCase()}</strong></div>
          <div><span>SIZE</span><strong>{fileSizeLabel(result.size_bytes)}</strong></div>
        </div>
        <div className="result-identity"><span>Dataset ID</span><code>{result.id}</code><span>SHA-256</span><code className="hash">{result.sha256}</code></div>
        {result.worksheet && <p className="worksheet-note">Selected worksheet: <strong>{result.worksheet}</strong></p>}
        {result.warnings.length > 0 && <div className="warning-panel" role="note"><strong>Validation notes</strong><ul>{result.warnings.map((message, i) => <li key={i}>{message}</li>)}</ul></div>}
        <div className="preview-heading"><h3>Raw preview</h3><span>FIRST {result.preview.length} DATA ROWS · NO INFERRED TYPES</span></div>
        <div className="table-scroll" tabIndex={0} aria-label="Imported dataset preview, horizontally scrollable">
          <table className="data-table"><thead><tr>{result.headers.map((head, i) => <th key={i} scope="col">{head}</th>)}</tr></thead>
            <tbody>{result.preview.map((row, i) => <tr key={i}>{row.map((value, j) => <td key={j}>{value ?? <span className="missing">null</span>}</td>)}</tr>)}</tbody></table>
        </div>
        <p className="preview-note">Preview values are displayed as text. Data profiling, type inference and numerical results are planned for later bundles.</p>
      </section>}

      <section className="module-section" aria-label="Module roadmap">
        <div className="section-topline"><h2>Scientific workspaces</h2><span>DEVELOPMENT ROADMAP</span></div>
        <div className="module-list">{plannedModules.map((module, index) => (
          <div className="module" key={module}><span className="module-index">{String(index + 1).padStart(2, '0')}</span><span>{module}</span><span className={`module-status ${index === 0 ? 'module-active' : ''}`}>{index === 0 ? 'Import active' : 'Planned'}</span></div>
        ))}</div>
      </section>
      <footer>AXIOM LAB <span>—</span> Computation must be understandable, inspectable, and reproducible. <span className="footer-phase">PHASE {phase}</span></footer>
    </main>
  );
}
