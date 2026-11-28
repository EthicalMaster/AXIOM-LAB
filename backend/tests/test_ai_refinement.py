import json
import httpx
import pytest
from app.services import ai_provider, guide


def test_provider_prompt_answers_question(monkeypatch):
    monkeypatch.setenv('AXIOM_AI_MODEL','test')
    monkeypatch.setenv('AXIOM_AI_BASE_URL','https://example.org/v1')
    monkeypatch.setenv('AXIOM_AI_API_KEY','test-secret')
    def respond(request):
        payload=json.loads(request.content)
        assert payload['max_tokens']==650
        assert 'Answer the explicit question' in payload['messages'][0]['content']
        assert 'What is a p-value?' in payload['messages'][1]['content']
        return httpx.Response(200,json={'choices':[{'message':{'content':'## Interpretation\nA focused explanation.','finish_reason':None},'finish_reason':'stop'}]})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert ai_provider.chat_from_evidence('{"question":"What is a p-value?"}',client=client).startswith('## Interpretation')


def test_guide_matches_whole_terms_and_structures_context():
    answer=guide.explain('What is the meaning of this?', 'Overview', {'row_count':10,'column_count':2},False)['answer']
    assert 'no exact answer' in answer
    assert '## Active dataset' in answer
    assert '10 rows' in answer


def test_provider_failure_is_explicit(monkeypatch):
    def fail(_):raise ai_provider.AIUnavailable('offline')
    monkeypatch.setattr(guide,'chat_from_evidence',fail)
    reply=guide.explain('What is a p-value?','Statistics',None,True)
    assert reply['source']=='Built-in scientific guide'
    assert 'Provider unavailable' in reply['answer']
    assert 'null hypothesis' in reply['answer']
