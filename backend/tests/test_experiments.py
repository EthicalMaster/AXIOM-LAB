import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))

def upload(content=b'row,reading\n1,10\n2,15\n3,20\n'):
    res = client.post('/api/v1/datasets/import', files={'file': ('d.csv', io.BytesIO(content))})
    assert res.status_code == 201
    return res.json()

def test_create_and_restore_immutable_chart_run():
    d = upload()
    res = client.post('/api/v1/experiments', json={'name':'Calibration','dataset_id':d['id'],'column':'reading'})
    assert res.status_code == 201, res.text
    obj = res.json()
    assert obj['dataset_sha256'] == d['sha256']
    assert obj['run']['status'] == 'completed' and obj['run']['environment']['algorithm'] == 'observation-sequence-v1'
    assert obj['run']['result']['points'] == [{'x':1,'y':10},{'x':2,'y':15},{'x':3,'y':20}]
    assert client.get('/api/v1/experiments/' + obj['id']).json() == obj

def test_no_silent_coercion():
    d = upload(b'code,v\n001,1\n002,2\n')
    assert client.post('/api/v1/experiments',json={'name':'Bad','dataset_id':d['id'],'column':'code'}).status_code == 422

def test_ids_and_name_are_checked():
    d = upload()
    assert client.post('/api/v1/experiments', json={'name':'  ','dataset_id':d['id'],'column':'reading'}).status_code == 422
    assert client.post('/api/v1/experiments', json={'name':'Experiment','dataset_id':'bad','column':'reading'}).status_code == 422
    assert client.get('/api/v1/experiments/not-an-id').status_code == 404

def test_source_integrity_is_required(tmp_path:Path):
    d=upload()
    (tmp_path/'datasets'/d['id']/'original.csv').write_bytes(b'broken')
    res=client.post('/api/v1/experiments',json={'name':'No','dataset_id':d['id'],'column':'reading'})
    assert res.status_code == 409

def test_chart_bounded_sampling_is_truthful():
    from app.services.experiment_visualization import sequence_chart
    content = ('v\n' + ''.join(f'{i}\n' for i in range(1001))).encode()
    result = sequence_chart(content, '.csv', 'v')
    assert result['sampled'] is True and result['original_point_count'] == 1001
    assert result['shown_point_count'] == 250 and result['points'][0]['x'] == 1
    assert result['points'][-1]['x'] == 1001
    assert len({p['x'] for p in result['points']}) == 250

def test_single_point_chart():
    from app.services.experiment_visualization import sequence_chart
    chart = sequence_chart(b'v\n5\n', '.csv', 'v')
    assert chart['points'] == [{'x':1,'y':5}]
