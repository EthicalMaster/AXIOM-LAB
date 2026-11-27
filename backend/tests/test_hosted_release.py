from pathlib import Path
import runpy
import pytest
from app.hosted import preflight, https_origin

ROOT=Path(__file__).resolve().parents[2]
render=runpy.run_path(str(ROOT/'scripts/configure_vercel.py'))['render']
private_path=runpy.run_path(str(ROOT/'scripts/check_private_files.py'))['private_path']

@pytest.fixture
def hosted(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_HOSTED_MODE','1')
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','1')
    monkeypatch.setenv('AXIOM_ACCESS_TOKEN','synthetic-fixture-'+'x'*32)
    monkeypatch.setenv('AXIOM_PUBLIC_ORIGIN','https://studio.example.org')
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('PORT','8001')


def test_hosted_preflight(hosted):
    assert preflight()==8001

@pytest.mark.parametrize('key,value', [('AXIOM_PUBLIC_MODE','0'),('AXIOM_ACCESS_TOKEN','short'),('AXIOM_PUBLIC_ORIGIN','http://studio.example.org'),('AXIOM_DATA_DIR','relative'),('PORT','0'),('AXIOM_HOSTED_MODE','maybe')])
def test_hosted_preflight_fails_closed(hosted,monkeypatch,key,value):
    monkeypatch.setenv(key,value)
    with pytest.raises(ValueError): preflight()


def test_local_container_opt_out(monkeypatch):
    monkeypatch.setenv('AXIOM_HOSTED_MODE','0'); monkeypatch.setenv('PORT','8000')
    monkeypatch.delenv('AXIOM_ACCESS_TOKEN',raising=False)
    assert preflight()==8000

@pytest.mark.parametrize('value',['http://api.example.org','https://api.example.org/v1','https://api.example.org?x=1','https://localhost','https://[broken'])
def test_bad_deployment_origins(value):
    with pytest.raises(ValueError): https_origin(value)


def test_vercel_template():
    config=render('https://api.example.org')
    assert config['rewrites']==[{'source':'/api/:path*','destination':'https://api.example.org/api/:path*'}]
    assert config['outputDirectory']=='dist'
    assert any(x['source']=='/api/:path*' and {'key':'Cache-Control','value':'no-store'} in x['headers'] for x in config['headers'])
    with pytest.raises(ValueError): render('https://YOUR-BACKEND.example')


def test_private_paths():
    for p in ('.env','frontend/.env.local','runtime/data.csv','backups/db','frontend/.vercel/project.json','private.key'):
        assert private_path(p)
    assert not private_path('.env.example')
    assert not private_path('frontend/public/examples/practice.csv')
