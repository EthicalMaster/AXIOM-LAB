from pathlib import Path

def test_release_files_and_safe_defaults():
    root=Path(__file__).resolve().parents[2]
    assert (root/'deploy/nginx.conf').is_file()
    assert '127.0.0.1:8080:8080' in (root/'compose.yaml').read_text()
    assert 'USER axiom' in (root/'deploy/Dockerfile.backend').read_text()
    assert 'USER nginx' in (root/'deploy/Dockerfile.frontend').read_text()
    assert (root/'docs/DEPLOYMENT.md').is_file()
