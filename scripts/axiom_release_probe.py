"""Bounded readiness probe for an AXIOM LAB instance you own. Health only; not a science load test."""
import argparse, asyncio, math, statistics, time
from urllib.parse import urlsplit
import httpx

def validate(origin):
    u=urlsplit(origin)
    if u.username or u.password or u.path or u.query or u.fragment or not u.hostname or not (u.scheme=='https' or (u.scheme=='http' and u.hostname in ('localhost','127.0.0.1'))):
        raise ValueError('Use an owned HTTPS origin or local HTTP origin, without a path.')
    return origin

async def run(origin,count,parallel):
    times=[]; failures=0
    async with httpx.AsyncClient(timeout=8,follow_redirects=False,trust_env=False) as client:
        async def ping():
            start=time.perf_counter()
            try:
                r=await client.get(origin+'/api/v1/health');ok=r.status_code==200 and r.json().get('status')=='ok'
            except (httpx.HTTPError,ValueError):ok=False
            return (time.perf_counter()-start)*1000,ok
        for start in range(0,count,parallel):
            for elapsed,ok in await asyncio.gather(*(ping() for _ in range(min(parallel,count-start)))):
                times.append(elapsed);failures+=not ok
            await asyncio.sleep(.25)
    ordered=sorted(times)
    print(f'Health only: {count-failures}/{count} OK; median {statistics.median(times):.1f} ms; p95 {ordered[math.ceil(.95*count)-1]:.1f} ms')
    return int(failures>0)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('origin');p.add_argument('--count',type=int,choices=range(1,41),default=12);p.add_argument('--parallel',type=int,choices=range(1,5),default=2);a=p.parse_args()
    try:origin=validate(a.origin.rstrip('/'))
    except ValueError as e:p.error(str(e))
    raise SystemExit(asyncio.run(run(origin,a.count,a.parallel)))
if __name__=='__main__':main()
