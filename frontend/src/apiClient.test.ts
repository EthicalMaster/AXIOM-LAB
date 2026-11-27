import {afterEach,describe,expect,it,vi} from 'vitest';
import {apiFetch} from './apiClient';

afterEach(()=>vi.unstubAllGlobals());

describe('shared scientific request contract',()=>{
  it('returns a successful response and uses same-origin credentials',async()=>{
    const fetcher=vi.fn(async()=>new Response('{"status":"ok"}'));
    vi.stubGlobal('fetch',fetcher);
    expect(await (await apiFetch('/api/v1/health')).json()).toEqual({status:'ok'});
    expect(fetcher).toHaveBeenCalledWith('/api/v1/health',expect.objectContaining({credentials:'same-origin',cache:'no-store'}));
  });
  it('rejects invalid paths without any network request',async()=>{
    const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);
    await expect(apiFetch('https://example.com/api/v1/health')).rejects.toThrow('Invalid API route');
    expect(fetcher).not.toHaveBeenCalled();
  });
  it('keeps actionable validation details and request IDs',async()=>{
    vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({detail:{message:'Choose two different columns'}}),{status:422,headers:{'X-Request-ID':'abc123'}})));
    await expect(apiFetch('/api/v1/datasets/test')).rejects.toThrow('Choose two different columns (HTTP 422 · abc123)');
  });
  it('honors retry information without retrying a mutation',async()=>{
    const fetcher=vi.fn(async()=>new Response('{}',{status:429,headers:{'Retry-After':'12'}}));vi.stubGlobal('fetch',fetcher);
    await expect(apiFetch('/api/v1/experiments',{method:'POST'})).rejects.toThrow('Retry after 12 seconds');
    expect(fetcher).toHaveBeenCalledTimes(1);
  });
  it('reports a rejected access token clearly',async()=>{
    vi.stubGlobal('fetch',vi.fn(async()=>new Response('{}',{status:401})));
    await expect(apiFetch('/api/v1/auth/login',{method:'POST'})).rejects.toThrow('Access token rejected');
  });
  it('preserves cancellation as AbortError',async()=>{
    const controller=new AbortController();controller.abort();
    vi.stubGlobal('fetch',vi.fn(async()=>{throw new DOMException('Cancelled','AbortError')}));
    await expect(apiFetch('/api/v1/health',{signal:controller.signal})).rejects.toMatchObject({name:'AbortError'});
  });
});
