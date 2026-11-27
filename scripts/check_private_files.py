"""Check the Git index for private runtime files; no contents or credentials are printed."""
import subprocess
from pathlib import PurePosixPath


def private_path(name):
    path=PurePosixPath(name)
    return (any(p in {'.vercel','runtime','backups','release-evidence','.venv','node_modules'} for p in path.parts)
            or any((p=='.env' or p.startswith('.env.')) and p!='.env.example' for p in path.parts)
            or path.suffix.lower() in {'.sqlite','.sqlite3','.db','.pem','.key','.p12','.pfx'})


def main():
    result=subprocess.check_output(['git','ls-files','-z'])
    count=sum(private_path(p.decode('utf-8',errors='replace')) for p in result.split(b'\0') if p)
    if count: raise SystemExit(f'FAIL: {count} tracked private/runtime file(s). Inspect the Git index locally.')
    print('Tracked private-file check passed (path names only; not a secret-content scan).')

if __name__=='__main__': main()
