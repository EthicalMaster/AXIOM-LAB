"""Offline snapshot/restore verification for one AXIOM instance. Stop ALL writers first."""
from argparse import ArgumentParser
from contextlib import closing
import hashlib
import re
from pathlib import Path
import shutil
import sqlite3
import tempfile


def verify(root: Path) -> tuple[int, int]:
    db = root / 'axiom.sqlite3'
    if not db.is_file() or db.is_symlink():
        raise ValueError('Missing database or unsupported symlink.')
    with closing(sqlite3.connect(db.resolve().as_uri()+'?mode=ro', uri=True)) as connection:
        if connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError('Database integrity check failed.')
        if connection.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Database foreign-key check failed.')
        rows = connection.execute('SELECT id,file_format,sha256,size_bytes,storage_relative_path FROM datasets').fetchall()
    total = 0
    for identifier, fmt, digest, size, stored in rows:
        if not re.fullmatch(r'[0-9a-f]{32}',identifier) or fmt not in ('csv','xls','xlsx'):
            raise ValueError('Invalid dataset record.')
        relative = Path('datasets') / identifier / ('original.'+fmt)
        if relative.as_posix() != stored:
            raise ValueError('Unexpected dataset storage path.')
        file = root / relative
        if any((root / p).is_symlink() for p in (relative, relative.parent, relative.parent.parent)):
            raise ValueError('Symlink in dataset storage.')
        if not file.is_file() or file.stat().st_size != size:
            raise ValueError('Dataset size or existence verification failed.')
        with file.open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest() != digest:
                raise ValueError('Dataset fingerprint verification failed.')
        total += size
    return len(rows),total


def snapshot(source: Path, destination: Path) -> tuple[int, int]:
    source, destination = source.resolve(), destination.resolve()
    if destination.exists() or source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Destination must be a new, separate directory.')
    expected = verify(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.axiom-snapshot-',dir=destination.parent) as temp:
        staging = Path(temp)/'snapshot'; staging.mkdir()
        with closing(sqlite3.connect((source/'axiom.sqlite3').as_uri()+'?mode=ro',uri=True)) as src, closing(sqlite3.connect(staging/'axiom.sqlite3')) as dst:
            src.backup(dst)
            rows=dst.execute('SELECT storage_relative_path FROM datasets').fetchall()
        for (relative,) in rows:
            target=staging/relative; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/relative,target)
        if verify(staging)!=expected:
            raise ValueError('Copied data did not match source.')
        if destination.exists():
            raise ValueError('Destination appeared during backup.')
        staging.rename(destination)
    return expected


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('verify','backup','restore-test'))
    parser.add_argument('source',type=Path)
    parser.add_argument('destination',type=Path,nargs='?')
    parser.add_argument('--writers-stopped',action='store_true',help='Confirm the application and all writers are stopped.')
    args=parser.parse_args()
    try:
        if args.action=='verify':
            result=verify(args.source)
        else:
            if not args.writers_stopped or args.destination is None:
                parser.error('A separate destination and --writers-stopped are required.')
            result=snapshot(args.source,args.destination)
        print(f'Verified {result[0]} dataset originals ({result[1]} bytes), SQLite integrity and foreign keys.')
        print('This is an offline integrity check, not encrypted or off-site disaster recovery.')
    except (ValueError,OSError,sqlite3.Error) as exc:
        parser.exit(1,f'Backup/verification failed ({type(exc).__name__}). Inspect storage locally.\n')


if __name__=='__main__': main()
