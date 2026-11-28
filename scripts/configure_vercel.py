"""Generate static Vercel routing for a known HTTPS backend; does not deploy or contact it."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.hosted import https_origin


def render(origin: str, root: Path=ROOT, supabase_origin: str | None=None) -> dict:
    origin=https_origin(origin)
    if origin.endswith('.example'):
        raise ValueError('Supply the actual hosted backend origin, not the example placeholder.')
    config=json.loads((root/'deploy/vercel.example.json').read_text(encoding='utf-8'))
    config['rewrites']=[{'source':'/api/:path*','destination':origin+'/api/:path*'}]
    if supabase_origin:
        import re
        if not re.fullmatch(r'https://[a-z0-9]+\.supabase\.co',supabase_origin):
            raise ValueError('Use the exact HTTPS Supabase project origin.')
        for rule in config['headers']:
            for header in rule['headers']:
                if header['key']=='Content-Security-Policy':
                    header['value']=header['value'].replace("connect-src 'self';", "connect-src 'self' "+supabase_origin+";")
    return config


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('backend_origin')
    parser.add_argument('--supabase-origin',help='Exact project origin for managed authentication CSP')
    args=parser.parse_args()
    try:
        content=json.dumps(render(args.backend_origin,supabase_origin=args.supabase_origin),indent=2)+'\n'
        path=ROOT/'frontend/vercel.json'
        if path.exists():
            if path.read_text(encoding='utf-8')==content:
                print('Configuration already matches.'); return
            raise ValueError('frontend/vercel.json already exists; review changes manually.')
        with path.open('x',encoding='utf-8') as output: output.write(content)
        print('Created frontend/vercel.json. Review and commit it; no deployment was performed.')
    except (ValueError,OSError) as exc:
        parser.exit(1,f'Configuration failed: {exc}\n')


if __name__=='__main__': main()
