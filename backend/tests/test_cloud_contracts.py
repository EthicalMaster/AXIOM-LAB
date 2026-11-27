from pathlib import Path
import pytest
from app.persistence import cloud
from app.persistence import dataset_store, experiment_store


def test_local_is_default(monkeypatch):
    monkeypatch.delenv("AXIOM_STORAGE_MODE", raising=False)
    assert not cloud.enabled()


def test_cloud_configuration_fails_closed(monkeypatch):
    monkeypatch.setenv("AXIOM_STORAGE_MODE", "supabase")
    monkeypatch.delenv("AXIOM_PUBLIC_MODE", raising=False)
    with pytest.raises(ValueError):
        cloud.configuration()


def test_object_path_is_opaque(monkeypatch):
    monkeypatch.setenv("AXIOM_SUPABASE_URL", "https://example.supabase.co")
    assert cloud._object_url("a"*32, ".csv").endswith("/axiom-datasets/"+"a"*32+"/original.csv")
    with pytest.raises(ValueError):
        cloud._object_url("../bad", ".csv")
    with pytest.raises(ValueError):
        cloud._object_url("a"*32, ".exe")


def test_cloud_dispatch(monkeypatch):
    from app.persistence import cloud_dataset, cloud_experiment
    monkeypatch.setenv("AXIOM_STORAGE_MODE", "supabase")
    monkeypatch.setattr(cloud_dataset, "find_dataset", lambda i: {"id": i})
    monkeypatch.setattr(cloud_experiment, "list_experiments", lambda l,o: {"limit":l,"offset":o})
    assert dataset_store.find_dataset("a"*32) == {"id":"a"*32}
    assert experiment_store.list_experiments(3,2) == {"limit":3,"offset":2}


def test_cloud_revision_lock():
    source = Path(__file__).resolve().parents[1]/"app/persistence/cloud_experiment.py"
    assert "FOR UPDATE" in source.read_text()
