import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import {WorkspaceBoundary} from './WorkspaceTools';
import {AccessGate} from './AccessGate';
import './styles.css';
import './studio.css';
import './math-studio.css';
import './release-motion.css';
import {applyTheme,initialTheme} from './Theme';

applyTheme(initialTheme());

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WorkspaceBoundary><AccessGate><App /></AccessGate></WorkspaceBoundary>
  </React.StrictMode>,
);
