"""Request-scoped private storage. No client-supplied workspace selector."""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from uuid import UUID
import os

_identity: ContextVar[str | None] = ContextVar('axiom_tenant', default=None)


def multi_user_enabled() -> bool:
    return os.getenv('AXIOM_MULTI_USER','').strip().lower() not in ('','0','false','no','off')


def canonical(value: str) -> str | None:
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        return None


def admitted(user_id: str) -> bool:
    # Explicit beta admission; never authorize from email or user-editable metadata.
    if canonical(user_id) != user_id:
        return False
    candidates = [os.getenv('AXIOM_GOOGLE_OWNER_ID',''), *os.getenv('AXIOM_MULTI_USER_IDS','').split(',')]
    return any(canonical(value.strip()) == user_id for value in candidates)


@contextmanager
def tenant_scope(user_id: str):
    if not admitted(user_id):
        raise PermissionError('Workspace not authorized.')
    token = _identity.set(user_id)
    try:
        yield
    finally:
        _identity.reset(token)


def storage_root(base: Path) -> Path:
    if not multi_user_enabled():
        return base
    identity = _identity.get()
    if identity is None or not admitted(identity):
        raise PermissionError('Verified tenant context required.')
    namespace = base / 'tenants'
    target = namespace / identity
    # No automatic legacy fallback, even for the owner. Reject redirected namespaces.
    if namespace.is_symlink() or target.is_symlink() or target.resolve() != target:
        raise PermissionError('Unsafe workspace storage configuration.')
    return target
