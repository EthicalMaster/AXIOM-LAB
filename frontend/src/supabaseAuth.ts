import {createClient} from '@supabase/supabase-js';
const url = (import.meta.env.VITE_SUPABASE_URL ?? '').trim();
const key = (import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ?? '').trim();
export const googleConfigured = Boolean(url || key);
export const googleConfigError = googleConfigured && (!/^https:\/\/[a-z0-9]+\.supabase\.co$/.test(url) || !key.startsWith('sb_publishable_'));
export const supabase = googleConfigured && !googleConfigError ? createClient(url,key,{
  auth:{flowType:'pkce',persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}
}) : null;
let accessToken: string | null = null;
export function setGoogleToken(token:string|null){ accessToken=token; }
export function googleToken(){return accessToken;}
