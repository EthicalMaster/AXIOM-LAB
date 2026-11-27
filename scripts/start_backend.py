"""Local development launcher. Load private settings before importing the ASGI app."""
from argparse import ArgumentParser
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def load_local_environment(root: Path = ROOT) -> None:
    # Hosting/terminal environment wins; do not expand secret values as templates.
    load_dotenv(root / '.env', override=False, interpolate=False)


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8898)
    parser.add_argument('--no-reload', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535.')
    os.chdir(ROOT)
    load_local_environment()
    import uvicorn
    uvicorn.run('app.main:app', app_dir=str(ROOT / 'backend'), host='127.0.0.1',
                port=args.port, reload=not args.no_reload,
                reload_dirs=None if args.no_reload else [str(ROOT / 'backend')])


if __name__ == '__main__':
    main()
