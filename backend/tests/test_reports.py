import json
from io import BytesIO
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def setup(tmp_path,monkeypatch): monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_export_reports_contain_only_stored_evidence():
    d=client.post('/api/v1/datasets/import',files={'file':('x.csv',b'x\n10\n20\n')}).json()
    e=client.post('/api/v1/experiments',json={'name':'Evidence','dataset_id':d['id'],'column':'x'}).json()
    url=f"/api/v1/experiments/{e['id']}/runs/{e['run']['id']}/report"
    j=client.get(url+'?format=json')
    assert j.status_code==200 and j.json()['run']['result']==e['run']['result']
    assert j.json()['experiment']['dataset_sha256']==d['sha256']
    csv=client.get(url+'?format=csv')
    assert csv.status_code==200 and b'10' in csv.content
    pdf=client.get(url+'?format=pdf')
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
    text=''.join(page.extract_text() for page in PdfReader(BytesIO(pdf.content)).pages)
    assert 'AXIOM LAB' in text and d['sha256'] in text
    assert client.get(url+'?format=html').status_code==422
    assert client.get('/api/v1/experiments/'+'f'*32+'/runs/'+'f'*32+'/report').status_code==404
