import {googleToken} from './supabaseAuth';

/** Same-origin requests only; never retry a mutation automatically. */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  if (!path.startsWith('/api/v1/')) throw new Error('Invalid API route.');
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (options.signal?.aborted) abort();
  options.signal?.addEventListener('abort', abort, {once:true});
  const timeout = setTimeout(abort, 30000);
  try {
    const token=googleToken();
    const headers=token?new Headers(options.headers):undefined;
    if(headers)headers.set('Authorization',`Bearer ${token}`);
    const response = await fetch(path, {...options, ...(headers?{headers}:{}), signal:controller.signal, credentials:'same-origin', cache:'no-store'});
    if (!response.ok) {
      const payload: unknown = await response.json().catch(()=>null);
      const detail = payload && typeof payload==='object' && 'detail' in payload ? payload.detail : null;
      const message = typeof detail==='string' ? detail : detail && typeof detail==='object' && 'message' in detail && typeof detail.message==='string' ? detail.message : '';
      const hint: Record<number,string> = {401:path==='/api/v1/auth/login'?'Access token rejected.':'Session expired or access required. Reload to unlock.',403:'Request not permitted. Check the configured workspace origin.',413:'File or request exceeds the size limit.',422:message || 'Check the input values and scientific assumptions.',429:'Service is busy or its request allowance is exhausted. Try again later.',503:'Scientific service is unavailable or at capacity. Open System checks.',507:'Dataset storage allowance reached. Contact the workspace administrator.'};
      const id=response.headers.get('X-Request-ID');
      const retry = response.headers.get('Retry-After');
      throw new Error(`${hint[response.status] || message || 'Request failed.'} (HTTP ${response.status}${id?` · ${id}`:''})${retry&&/^\d+$/.test(retry)?` Retry after ${retry} seconds.`:''}`);
    }
    return response;
  } catch(error) {
    if(options.signal?.aborted) throw new DOMException('Cancelled','AbortError');
    if(controller.signal.aborted) {
      const method=(options.method??'GET').toUpperCase();
      throw new Error(method==='GET'||method==='HEAD'?'Request timed out. Check System checks and retry.':'Request timed out. A write may have completed; check saved records before repeating it.');
    }
    if(error instanceof TypeError) throw new Error('Cannot reach the scientific API. Check connectivity in System checks.');
    throw error;
  } finally { clearTimeout(timeout); options.signal?.removeEventListener('abort',abort); }
}
