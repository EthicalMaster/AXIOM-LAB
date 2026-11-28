"""Process-local per-admitted-user rate and concurrency budget, in addition to global guard."""
from collections import deque
from contextlib import contextmanager
from threading import Lock
from time import monotonic
from app.core.request_guard import setting

_lock=Lock()
_states={}

@contextmanager
def admit_request(identity):
    now=monotonic()
    with _lock:
        for key,(active,events) in list(_states.items()):
            if not active and (not events or events[-1]<=now-60): del _states[key]
        if identity not in _states and len(_states)>=2048:
            allowed=False
        else:
            active,events=_states.setdefault(identity,[0,deque()])
            while events and events[0]<=now-60: events.popleft()
            allowed=active<setting('AXIOM_USER_INFLIGHT',2,16) and len(events)<setting('AXIOM_USER_RPM',60,1200)
            if allowed:
                events.append(now); _states[identity][0]+=1
    try:
        yield allowed
    finally:
        if allowed:
            with _lock: _states[identity][0]-=1
