import React from 'react';
import ReactDOM from 'react-dom/client';
import LandingPage from './LandingPage';
import {isStudioView} from './landingRoute';
import {WorkspaceBoundary} from './WorkspaceTools';
import {AccessGate} from './AccessGate';
import {GoogleGate} from './GoogleGate';
import './styles.css';
import './studio.css';
import './math-studio.css';
import './release-motion.css';
import './responsive.css';
import {applyTheme,initialTheme} from './Theme';

const App = React.lazy(() => import('./App'));
applyTheme(initialTheme());

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WorkspaceBoundary>{isStudioView(window.location.search) ? <GoogleGate><AccessGate><React.Suspense fallback={<main className="startup-screen" role="status">Loading research studio…</main>}><App /></React.Suspense></AccessGate></GoogleGate> : <LandingPage />}</WorkspaceBoundary>
  </React.StrictMode>,
);
