const repository = 'https://github.com/EthicalMaster/AXIOM-LAB';
const revision = import.meta.env.VITE_VERCEL_GIT_COMMIT_SHA;
const valid = typeof revision === 'string' && /^[a-f0-9]{40}$/i.test(revision);
const ref = valid ? revision : 'main';

export function SourceNotice() {
  return <span className="source-notice" style={{lineHeight: 1.6, overflowWrap: 'anywhere'}}>
    {"© 2026 EthicalMaster"} · <a href={`${repository}/blob/${ref}/LICENSE`} style={{color:'inherit',textDecoration:'underline'}}>AGPL-3.0</a> · <a href={valid ? `${repository}/tree/${ref}` : repository} style={{color:'inherit',textDecoration:'underline'}}>Source code</a>
  </span>;
}
