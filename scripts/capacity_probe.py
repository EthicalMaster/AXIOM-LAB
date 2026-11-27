"""Fixed, bounded, synthetic in-process probe. Never sends traffic to an external host."""
from __future__ import annotations
import asyncio
import json
import math
import os
import platform
from collections import Counter
from pathlib import Path
from statistics import median
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

os.environ.update(AXIOM_PUBLIC_MODE='0', AXIOM_MAX_INFLIGHT='4', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import httpx
from app.main import app


def percentile(values, fraction):
    ordered=sorted(values)
    return round(ordered[max(0,math.ceil(len(ordered)*fraction)-1)],2) if ordered else None


async def probe():
    stages=[]
    with TemporaryDirectory(prefix='axiom-probe-') as root:
        os.environ['AXIOM_DATA_DIR']=root
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://local-probe') as client:
            csv='x,y\n'+''.join(f'{i},{3*i+2}\n' for i in range(1,401))
            uploaded=await client.post('/api/v1/datasets/import',files={'file':('synthetic.csv',csv.encode())})
            uploaded.raise_for_status(); dataset_id=uploaded.json()['id']
            async def request(index):
                start=perf_counter()
                if index%2:
                    response=await client.get(f'/api/v1/datasets/{dataset_id}/statistics')
                else:
                    response=await client.post(f'/api/v1/datasets/{dataset_id}/ml/regression',json={'task':'regression','features':['x'],'target':'y','time_dependent':False})
                return response.status_code,(perf_counter()-start)*1000
            # Warm up imports, SQLite and scientific kernels outside measurements.
            for i in range(2):
                assert (await request(i))[0]==200
            for concurrency in (1,2,4,8):
                start=perf_counter(); results=[]
                for offset in range(0,24,concurrency):
                    results.extend(await asyncio.gather(*(request(i) for i in range(offset,min(offset+concurrency,24)))))
                elapsed=perf_counter()-start
                counts=Counter(code for code,_ in results)
                success=[ms for code,ms in results if code==200]
                stage={'concurrency':concurrency,'requests':len(results),'statuses':dict(counts),
                       'successful_p50_ms':round(median(success),2) if success else None,
                       'successful_p95_ms':percentile(success,.95),'successful_p99_ms':percentile(success,.99),
                       'all_p95_ms':percentile([ms for _,ms in results],.95),
                       'successful_requests_per_second':round(len(success)/elapsed,2),'wall_ms':round(elapsed*1000,2)}
                stages.append(stage)
                if not success or any(code not in (200,503) for code in counts) or (concurrency<=4 and counts[503]):
                    raise RuntimeError('Unexpected admission result')
            assert (await client.get('/api/v1/health')).status_code==200
            assert (await request(0))[0]==200  # capacity returned after the burst
    print(json.dumps({'scope':'synthetic in-process ASGI, single worker, no network', 'python':platform.python_version(),
                      'dataset_rows':400,'max_inflight':4,'stages':stages,
                      'limitations':'Not a live hosting, CPU/RAM, AI quota, or simultaneous user capacity measurement.'},indent=2))


if __name__=='__main__': asyncio.run(probe())
