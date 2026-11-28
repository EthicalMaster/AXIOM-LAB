/** Explicit URL state keeps the landing and protected studio separate. */
export function isStudioView(search:string):boolean {
  return new URLSearchParams(search).get('view')==='studio';
}
