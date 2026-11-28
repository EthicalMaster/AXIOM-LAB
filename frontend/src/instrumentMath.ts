/** Normal density and interval mass for the public, synthetic teaching instrument. */
export function normalDensity(x:number, mean:number, sigma:number):number {
  if(!Number.isFinite(x)||!Number.isFinite(mean)||!Number.isFinite(sigma)||sigma<=0) throw new RangeError('Invalid normal parameters');
  const z=(x-mean)/sigma;
  return Math.exp(-z*z/2)/(sigma*Math.sqrt(2*Math.PI));
}
export function intervalMass(mean:number,sigma:number,lo=-1,hi=1):number {
  if(!Number.isFinite(lo)||!Number.isFinite(hi)||hi<lo) throw new RangeError('Invalid interval');
  // Composite Simpson quadrature, 256 even subdivisions, bounded UI domain.
  const n=256,h=(hi-lo)/n;
  let sum=normalDensity(lo,mean,sigma)+normalDensity(hi,mean,sigma);
  for(let i=1;i<n;i++)sum+=(i%2?4:2)*normalDensity(lo+i*h,mean,sigma);
  return Math.min(1,Math.max(0,sum*h/3));
}
