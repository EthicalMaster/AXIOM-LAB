"""Small offline artifact audit. Does not replace build, threat model, or deployment test."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[
    'compose.yaml','deploy/Dockerfile.backend','deploy/Dockerfile.frontend','deploy/nginx.conf',
    'docs/DEPLOYMENT.md','.env.example','frontend/package-lock.json',
    'backend/app/api/reports.py','backend/app/core/access.py',
]


def main() -> int:
    missing=[p for p in REQUIRED if not (ROOT/p).is_file()]
    compose=(ROOT/'compose.yaml').read_text(encoding='utf-8') if not missing else ''
    if missing:
        print('Missing release assets:',', '.join(missing))
        return 1
    if '127.0.0.1:8080:8080' not in compose:
        print('Unsafe or missing loopback Compose port binding; inspect compose.yaml')
        return 1
    if 'AXIOM_PUBLIC_MODE' not in compose:
        print('Public-mode security configuration missing')
        return 1
    print('Local release artifact checks passed. Runtime, Docker and user acceptance remain unverified.')
    return 0


if __name__=='__main__': sys.exit(main())
