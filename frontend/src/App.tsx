import {apiFetch} from './apiClient';
import { AIStudioPanel } from './AIStudioPanel';
import { HistoryPanel } from './HistoryPanel';
import {MachineLearning} from './MachineLearning';
import {ImportPanel} from './ImportPanel';
import {MathStudio} from './MathStudio';
import { DiagnosticsPanel } from './DiagnosticsPanel';
import { HypothesisPanel } from './HypothesisPanel';
import { FormEvent, useEffect, useRef, useState } from 'react';
import {Overview} from './Overview';
import {ThemeSwitch} from './Theme';
import {WorkspaceIcon} from './WorkspaceIcon';
import {Guide, SystemChecks, Loading, WorkspaceBoundary, RecoveryScreen} from './WorkspaceTools';
import {Details} from './Visuals';
import { clientFileError, importDataset, type ImportedDataset } from './datasets';
import { fetchColumnProfile, type DatasetColumnProfile } from './columnProfile';
import { ColumnProfilePanel } from './ColumnProfilePanel';
import { StatisticsPanel } from './StatisticsPanel';
import { ExperimentPanel } from './ExperimentPanel';
import { QualityPanel } from './QualityPanel';
import { DistributionPanel } from './DistributionPanel';

type Connection = 'checking' | 'connected' | 'unavailable';
type Health = { status: string; phase: string; scientific_engine: string };

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking');
  const [healthAttempt,setHealthAttempt]=useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportedDataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [profile, setProfile] = useState<DatasetColumnProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const profileRequest = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    apiFetch('/api/v1/health', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error('Backend not responding');
        return res.json() as Promise<Health>;
      })
      .then((data) => {
        setConnection(data.status === 'ok' ? 'connected' : 'unavailable');
      })
      .catch((e: unknown) => {
        if (e instanceof Error && e.name === 'AbortError') return;
        setConnection('unavailable');
      });
    return () => controller.abort();
  }, [healthAttempt]);

  function selectFile(file:File|null) {
    if(uploading)return;
    setSelectedFile(file);
    setError(null);
  }

  async function loadProfile(datasetId: string) {
    const request = ++profileRequest.current;
    setProfileLoading(true);
    setProfileError(null);
    try {
      const loaded = await fetchColumnProfile(datasetId);
      if (request === profileRequest.current) setProfile(loaded);
    } catch (e: unknown) {
      if (request === profileRequest.current) setProfileError(e instanceof Error ? e.message : 'Profile unavailable.');
    } finally {
      if (request === profileRequest.current) setProfileLoading(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || uploading) return;
    const validationError = clientFileError(selectedFile.name, selectedFile.size);
    if (validationError) { setError(validationError); return; }
    setUploading(true);
    setError(null);
    try {
      const imported = await importDataset(selectedFile);
      setProfile(null);
      setResult(imported);
      setSelectedFile(null);
      void loadProfile(imported.id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Dataset upload could not be completed.');
    } finally {
      setUploading(false);
    }
  }

  const pages = ['Overview','Data Lab','Statistics','Mathematics','Machine Learning','Experiments','Method guide','System checks'] as const;
  type Page = typeof pages[number];
  const [page,setPage]=useState<Page>('Overview');
  const [collapsed,setCollapsed]=useState(false);
  const [visited,setVisited]=useState<Page[]>(['Overview']);
  function navigate(next:Page){setPage(next);setVisited(v=>v.includes(next)?v:[...v,next]);}
  const numeric=profile?.columns.filter(c=>c.inferred_type==='numeric').map(c=>c.name)??[];
  const target=profile?.columns.filter(c=>c.inferred_type==='categorical'||c.inferred_type==='boolean').map(c=>c.name)??[];
  const empty=<section className="bento-card"><h2>Start with a dataset</h2><p>Import your original observations in Overview to unlock this workspace.</p><button className="retry-button" onClick={()=>navigate('Overview')}>Import dataset</button></section>;
  return <div className={`workspace-shell${collapsed?' nav-collapsed':''}`}>
    <aside className="workspace-nav"><div className="nav-brand"><span className="brand-glyph">∴</span><div className="brand-name">AXIOM<span>LAB</span><small>RESEARCH STUDIO</small></div></div><button className="nav-collapse" type="button" aria-label={collapsed?'Expand sidebar':'Collapse sidebar'} aria-expanded={!collapsed} onClick={()=>setCollapsed(v=>!v)}><WorkspaceIcon name={collapsed?'expand':'collapse'}/><span>{collapsed?'Expand':'Collapse'}</span></button><span className="nav-section-label">WORKSPACE</span><nav aria-label="Workspaces">{pages.map(p=><button key={p} title={p} aria-label={p} aria-current={p===page?'page':undefined} onClick={()=>navigate(p)}><WorkspaceIcon name={p}/><span className="nav-text">{p}</span></button>)}</nav><div className="nav-footer"><span className={`dot ${connection}`}/><span className="nav-text">{connection==='connected'?'Engine connected':connection==='checking'?'Connecting':'Engine unavailable'}</span></div></aside>
    <main className="workspace-main" id="workspace"><header className="workspace-top"><div><span className="micro">Research studio <span className="breadcrumb-separator">/</span> {page}</span><h1>{page}</h1></div><div className="top-controls"><span className="workspace-state" role="status"><i className={`dot ${connection}`}/>{connection==='connected'?'API online':connection==='checking'?'Connecting':'API unavailable'}</span><ThemeSwitch/></div></header>
    {connection==='unavailable'&&<RecoveryScreen detail="Scientific engine not reachable. Your imported view remains available, but new calculations require the API." onRetry={()=>{setConnection('checking');setHealthAttempt(n=>n+1)}} onTroubleshoot={()=>navigate('System checks')}/>}
    {visited.includes('Overview')&&<div hidden={page!=='Overview'} className="workspace-page"><Overview dataset={result} profile={profile} onNavigate={navigate}/><ImportPanel file={selectedFile} onSelect={selectFile} onSubmit={submit} uploading={uploading} profiling={profileLoading} connected={connection==='connected'} error={error} hasDataset={!!result} onInspect={()=>navigate('Data Lab')}/></div>}
    {visited.includes('Data Lab')&&<div hidden={page!=='Data Lab'} className="workspace-page"><WorkspaceBoundary>{result?<><section className="bento-card"><h2>{result.original_name}</h2><p>{result.row_count} rows · {result.column_count} columns</p>{result.warnings.length>0&&<div className="warning-panel">{result.warnings.join(' ')}</div>}<Details title="Original data preview and fingerprint"><div className="result-identity"><span>Dataset ID</span><code>{result.id}</code><span>SHA-256</span><code>{result.sha256}</code></div><div className="table-scroll" tabIndex={0}><table className="data-table"><thead><tr>{result.headers.map((h,i)=><th key={i} scope="col">{h}</th>)}</tr></thead><tbody>{result.preview.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{v??'null'}</td>)}</tr>)}</tbody></table></div></Details></section>{profileLoading&&<Loading label="Inspecting columns"/>}{profileError&&<div role="alert" className="inline-alert error">{profileError}<button className="retry-button" onClick={()=>void loadProfile(result.id)}>Retry inspection</button></div>}{profile&&<ColumnProfilePanel data={profile}/>}<QualityPanel key={result.id} datasetId={result.id}/></>:empty}</WorkspaceBoundary></div>}
    {visited.includes('Statistics')&&<div hidden={page!=='Statistics'} className="workspace-page scientific-grid"><WorkspaceBoundary>{result?<><StatisticsPanel key={result.id} datasetId={result.id}/>{profile&&<><DistributionPanel key={result.id+'dist'} datasetId={result.id} numericColumns={numeric}/><HypothesisPanel key={result.id+'hyp'} datasetId={result.id} numericColumns={numeric}/><DiagnosticsPanel key={result.id+'diag'} datasetId={result.id} numericColumns={numeric}/></>}</>:empty}</WorkspaceBoundary></div>}
    {visited.includes('Mathematics')&&<div hidden={page!=='Mathematics'} className="workspace-page scientific-grid"><WorkspaceBoundary><MathStudio/></WorkspaceBoundary></div>}
    {visited.includes('Machine Learning')&&<div hidden={page!=='Machine Learning'} className="workspace-page"><WorkspaceBoundary><MachineLearning datasetId={profile?result?.id:undefined} numericColumns={numeric} targetColumns={target} onImport={()=>navigate('Overview')}/>{profileLoading&&<Loading label="Inspecting model inputs"/>}</WorkspaceBoundary></div>}
    {visited.includes('Experiments')&&<div hidden={page!=='Experiments'} className="workspace-page"><WorkspaceBoundary>{result&&profile&&<ExperimentPanel key={result.id} datasetId={result.id} numericColumns={numeric}/>}<HistoryPanel/></WorkspaceBoundary></div>}
    {visited.includes('Method guide')&&<div hidden={page!=='Method guide'} className="workspace-page"><AIStudioPanel datasetId={result?.id}/></div>}
    {visited.includes('System checks')&&<div hidden={page!=='System checks'} className="workspace-page"><SystemChecks/></div>}
    <footer>AXIOM LAB · Results are computed from evidence. Advisory explanations do not replace scientific validation.</footer></main><Guide key={result?.id??"no-data"} page={page} datasetId={result?.id} numericColumns={numeric}/>
    </div>;
}
