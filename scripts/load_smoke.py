"""Explicit, bounded local-only read-only smoke load test; not a scalability certificate.

Run after starting the backend:
  python scripts/load_smoke.py --requests 30 --concurrency 3
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from statistics import median
from time import perf_counter
from urllib.parse import urlsplit
import httpx


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError('No successful requests')
    return ordered[min(len(ordered)-1, max(0,int((len(ordered)-1)*fraction+0.5)))]


def measure(url: str) -> tuple[int, float]:
    started=perf_counter()
    try:
        with httpx.Client(timeout=5,follow_redirects=False,trust_env=False) as session:
            response=session.get(url)
            return response.status_code, (perf_counter()-started)*1000
    except httpx.RequestError:
        return 0,(perf_counter()-started)*1000


def main() -> None:
    parser=argparse.ArgumentParser(description='Bounded local-only health endpoint smoke load')
    parser.add_argument('--url',default='http://127.0.0.1:8898/api/v1/health')
    parser.add_argument('--requests',type=int,default=30)
    parser.add_argument('--concurrency',type=int,default=3)
    args=parser.parse_args()
    host=urlsplit(args.url)
    if host.hostname not in ('127.0.0.1','localhost') or host.scheme != 'http' or host.path != '/api/v1/health':
        parser.error('Only local HTTP /api/v1/health may be targeted')
    if not 1<=args.requests<=80 or not 1<=args.concurrency<=5:
        parser.error('Requests must be 1..80 and concurrency 1..5')
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        samples=list(pool.map(lambda _:measure(args.url),range(args.requests)))
    okay=[duration for status,duration in samples if status==200]
    print({'requests':args.requests,'successes':len(okay),'failures':len(samples)-len(okay),
           'median_ms':round(median(okay),2) if okay else None,
           'p95_ms':round(percentile(okay,.95),2) if okay else None,
           'limit':'Local smoke observations only; not a production concurrency claim.'})
    if len(okay)<len(samples):
        raise SystemExit(1)


if __name__=='__main__': main()
