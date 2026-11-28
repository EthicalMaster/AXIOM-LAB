"""Aggregate AXIOM request logs without printing raw lines or identifiers."""
import argparse,collections,math,re
from pathlib import Path
PATTERN=re.compile(r'\brequest id=[0-9a-f]+ method=[A-Z]+ status=(\d{3}) elapsed_ms=(\d+(?:\.\d+)?)\b')
def summarize(lines):
    status=collections.Counter();ms=[]
    for line in lines:
        match=PATTERN.search(line)
        if match:status[int(match[1])]+=1;ms.append(float(match[2]))
    ms.sort();n=len(ms)
    return {'requests':n,'status':dict(sorted(status.items())),'p95_ms':round(ms[math.ceil(n*.95)-1],2) if n else None}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);a=p.parse_args()
    with a.log.open(encoding='utf-8',errors='replace') as f:print(summarize(f))
if __name__=='__main__':main()
