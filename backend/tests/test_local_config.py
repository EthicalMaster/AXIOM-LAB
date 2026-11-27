from pathlib import Path
import runpy
import os

from app.services.ai_provider import configuration, AIUnavailable
import pytest

ROOT = Path(__file__).resolve().parents[2]
load_environment = runpy.run_path(str(ROOT / 'scripts/start_backend.py'))['load_local_environment']


def test_private_config_loads_before_startup(tmp_path, monkeypatch):
    for name in ('AXIOM_AI_MODEL', 'AXIOM_AI_BASE_URL', 'AXIOM_AI_API_KEY'):
        monkeypatch.setenv(name, 'previous')
        monkeypatch.delenv(name)
    (tmp_path / '.env').write_text('AXIOM_AI_MODEL=test-model\nAXIOM_AI_BASE_URL=https://example.com/v1\nAXIOM_AI_API_KEY=literal-${NAME}\n')
    load_environment(tmp_path)
    assert configuration()['enabled'] is True
    assert os.environ['AXIOM_AI_API_KEY'] == 'literal-${NAME}'


def test_shell_configuration_wins(tmp_path, monkeypatch):
    monkeypatch.setenv('AXIOM_AI_MODEL', 'host-model')
    (tmp_path / '.env').write_text('AXIOM_AI_MODEL=file-model\n')
    load_environment(tmp_path)
    assert os.environ['AXIOM_AI_MODEL'] == 'host-model'


def test_no_config_file_is_optional(tmp_path, monkeypatch):
    monkeypatch.delenv('AXIOM_AI_MODEL', raising=False)
    load_environment(tmp_path)
    assert 'AXIOM_AI_MODEL' not in os.environ


@pytest.mark.parametrize('url', ['https://[broken/v1', 'https://example.com:abc/v1', 'https://example.com:99999/v1', 'https://example.com:0/v1'])
def test_malformed_provider_url_fails_cleanly(url, monkeypatch):
    monkeypatch.setenv('AXIOM_AI_BASE_URL', url)
    monkeypatch.setenv('AXIOM_AI_MODEL', 'test')
    monkeypatch.setenv('AXIOM_AI_API_KEY', 'dummy-key')
    with pytest.raises(AIUnavailable):
        configuration()
