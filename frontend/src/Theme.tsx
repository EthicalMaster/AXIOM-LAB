import {useState} from 'react';
export type Theme = 'dark' | 'light';
const key = 'axiom-theme-v1';
export function initialTheme(): Theme {
  try { const value=localStorage.getItem(key); if(value==='light'||value==='dark') return value; } catch { /* Storage can be disabled. */ }
  return 'dark';
}
export function applyTheme(theme: Theme) {
  document.documentElement.dataset.theme=theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content',theme==='light'?'#f4f5f8':'#0b0d12');
}
export function ThemeSwitch(){
  const [theme,setTheme]=useState(initialTheme);
  function toggle(){const next=theme==='dark'?'light':'dark';applyTheme(next);setTheme(next);try{localStorage.setItem(key,next)}catch{/* Theme still works for this tab. */}}
  return <button type="button" className="theme-switch" onClick={toggle} aria-label={`Switch to ${theme==='dark'?'light':'dark'} theme`} title={`Switch to ${theme==='dark'?'light':'dark'} theme`}>
    <span className={theme==='light'?'selected':''}><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M19 5l-2 2M7 17l-2 2"/></svg></span>
    <span className={theme==='dark'?'selected':''}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5Z"/></svg></span>
  </button>
}
