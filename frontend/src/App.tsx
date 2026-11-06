import { useEffect, useState } from 'react';
import { phase, plannedModules } from './phase';

type Connection = 'checking' | 'connected' | 'unavailable';
type Health = { status: string; phase: string; scientific_engine: string };

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking');

  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/v1/health', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('HTTP status not OK');
        return response.json() as Promise<Health>;
      })
      .then((data) => {
        setConnection(
          data.status === 'ok' && data.phase === '0' && data.scientific_engine === 'not_implemented'
            ? 'connected'
            : 'unavailable',
        );
      })
      .catch((error: unknown) => {
        if (error instanceof Error && error.name === 'AbortError') return;
        setConnection('unavailable');
      });
    return () => controller.abort();
  }, []);

  return (
    <main className="site-shell">
      <header className="topbar">
        <div className="wordmark"><span className="glyph" aria-hidden="true">∴</span> AXIOM <span className="thin">LAB</span></div>
        <span className="top-label">FOUNDATION / {phase}</span>
      </header>

      <section className="hero" aria-labelledby="project-title">
        <p className="eyebrow">SCIENTIFIC COMPUTING · ENGINEERING FOUNDATION</p>
        <h1 id="project-title">Computation should be <em>understood.</em></h1>
        <p className="lead">An interactive environment for scientific computing and computational discovery. Currently establishing the foundation for real, inspectable, reproducible experiments.</p>
        <div className="statuses">
          <div className="status"><span className="dot" aria-hidden="true" /><span>Phase 0 / Scaffold ready</span></div>
          <div className="status" role="status" aria-live="polite">
            <span className={`dot ${connection}`} aria-hidden="true" />
            <span>API {connection === 'checking' ? 'checking…' : connection === 'connected' ? 'connected' : 'unavailable'}</span>
          </div>
        </div>
      </section>

      <section className="module-section" aria-label="Planned scientific modules">
        <div className="section-topline"><h2>Scientific workspaces</h2><span>PLANNED / NOT YET IMPLEMENTED</span></div>
        <div className="module-list">
          {plannedModules.map((module, index) => (
            <div className="module" key={module}><span className="module-index">{String(index + 1).padStart(2, '0')}</span><span>{module}</span><span className="module-status">Planned</span></div>
          ))}
        </div>
      </section>

      <footer>AXIOM LAB <span>—</span> Verified science before presentation. No computational features are implemented in Phase 0.</footer>
    </main>
  );
}
