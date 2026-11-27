"""Bounded in-process capacity check with synthetic local data, never a remote target."""
from __future__ import annotations
import asyncio
import os
from collections import Counter
from pathlib import Path
from statistics import median
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

os.environ.update(AXIOM_PUBLIC_MODE='0', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import httpx
from app.main import app

async def probe() -> None:
    with TemporaryDirectory(prefix='axiom-probe-') as root:
        os.environ['AXIOM_DATA_DIR'] = root
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://local-probe') as client:
            csv = 'x,y\n' + ''.join(f'{i},{3*i+2}\n' for i in range(1, 401))
            uploaded = await client.post('/api/v1/datasets/import', files={'file': ('synthetic.csv', csv.encode())})
            uploaded.raise_for_status()
            dataset_id = uploaded.json()['id']
            async def request(index):
                started = perf_counter()
                if index % 2:
                    response = await client.get(f'/api/v1/datasets/{dataset_id}/statistics')
                else:
                    response = await client.post(f'/api/v1/datasets/{dataset_id}/ml/regression', json={'task':'regression','features':['x'],'target':'y','time_dependent':False})
                return response.status_code, (perf_counter()-started)*1000
            for concurrency in (1, 2, 4, 8):
                results = []
                started = perf_counter()
                for offset in range(0, 16, concurrency):
                    results.extend(await asyncio.gather(*(request(i) for i in range(offset, min(offset+concurrency,16)))))
                success = sorted(ms for status,ms in results if status == 200)
                counts = dict(Counter(status for status,_ in results))
                print({'concurrent_requests':concurrency,'status_counts':counts,'successful_p50_ms':round(median(success),2) if success else None,'successful_p95_ms':round(success[min(len(success)-1,int(.95*len(success)))],2) if success else None,'wall_ms':round((perf_counter()-started)*1000,2)})
                if any(code not in (200,503) for code in counts):
                    raise RuntimeError('Unexpected application status')
    print('Synthetic in-process measurements only; no deployed HTTPS, network, browser, RAM or multi-user capacity claim.')

if __name__=='__main__':
    asyncio.run(probe())
