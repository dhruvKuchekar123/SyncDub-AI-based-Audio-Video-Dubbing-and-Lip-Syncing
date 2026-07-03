"""API-surface tests: FastAPI TestClient with the pipeline subprocess mocked."""
import importlib
import json

import pytest
from fastapi.testclient import TestClient

import config
import jobs


@pytest.fixture
def client(tmp_path, monkeypatch):
    for name in ("TEMP_DIR", "OUTPUT_DIR", "UPLOAD_DIR", "PROGRESS_DIR", "JOBS_DIR"):
        monkeypatch.setattr(config, name, tmp_path / name.lower())
    monkeypatch.setattr(jobs, "LOCK_PATH", tmp_path / ".pipeline.lock")
    config.ensure_dirs()

    import server
    server = importlib.reload(server)  # re-mount /outputs onto the tmp dir

    spawned = []
    monkeypatch.setattr(
        server.subprocess, "Popen",
        lambda cmd, **kw: spawned.append(cmd) or None,
    )
    c = TestClient(server.app)
    c.spawned = spawned
    return c


def _upload(client, **data):
    data.setdefault("uploader_attestation", "true")
    return client.post(
        "/jobs",
        files={"file": ("clip.mp4", b"fake-video-bytes", "video/mp4")},
        data=data,
    )


def test_create_job_returns_id_and_spawns_pipeline(client):
    res = _upload(client)
    assert res.status_code == 200
    job_id = res.json()["job_id"]
    assert len(job_id) == 12

    # initial progress written before the process starts
    data = jobs.read_progress(jobs.job_paths(job_id).progress_path)
    assert data["state"] == "running"
    assert data["progress"] == 0

    assert len(client.spawned) == 1
    assert "--job-id" in client.spawned[0]
    # upload saved under a job-scoped name
    uploads = list(config.UPLOAD_DIR.iterdir())
    assert uploads[0].name == f"{job_id}_clip.mp4"


def test_two_jobs_get_distinct_ids_and_files(client):
    id1 = _upload(client).json()["job_id"]
    id2 = _upload(client).json()["job_id"]
    assert id1 != id2
    assert len(list(config.UPLOAD_DIR.iterdir())) == 2


def test_create_job_refused_while_lock_held_by_live_pid(client, monkeypatch):
    assert jobs.acquire_pipeline_lock("busyjob") is True  # our own live pid
    try:
        res = _upload(client)
        assert res.status_code == 409
        assert "busyjob" in res.json()["detail"]
    finally:
        jobs.release_pipeline_lock("busyjob")


def test_progress_unknown_job_404(client):
    assert client.get("/progress/deadbeef0000").status_code == 404


def test_progress_roundtrip(client):
    job_id = _upload(client).json()["job_id"]
    res = client.get(f"/progress/{job_id}")
    assert res.status_code == 200
    assert res.json()["job_id"] == job_id


def test_video_404_until_done(client):
    job_id = _upload(client).json()["job_id"]
    assert client.get(f"/video/{job_id}").status_code == 404

    # simulate pipeline completion
    paths = jobs.job_paths(job_id)
    w = jobs.ProgressWriter(paths.progress_path, job_id)
    w.done()
    paths.output_path.parent.mkdir(parents=True, exist_ok=True)
    paths.output_path.write_bytes(b"mp4")

    res = client.get(f"/video/{job_id}")
    assert res.status_code == 200
    assert res.json()["video_url"] == f"/outputs/{job_id}.mp4"


def test_video_unknown_job_404(client):
    assert client.get("/video/deadbeef0000").status_code == 404


def test_languages_endpoint_lists_registry(client):
    res = client.get("/languages")
    assert res.status_code == 200
    codes = {e["code"] for e in res.json()["languages"]}
    assert {"hi", "mr", "en"} <= codes


def test_create_job_rejects_unknown_language(client):
    res = _upload(client, source_lang="hi", target_lang="xx")
    assert res.status_code == 422
    assert client.spawned == []


def test_create_job_requires_uploader_attestation(client):
    res = _upload(client, uploader_attestation="false")
    assert res.status_code == 400
    assert "attestation_text" in res.json()["detail"]
    assert client.spawned == []


def test_cloning_without_speaker_consent_is_400(client):
    res = _upload(client, enable_cloning="true")
    assert res.status_code == 400
    assert "consent_text" in res.json()["detail"]
    assert client.spawned == []


def test_consent_record_written_per_job(client):
    import hashlib
    res = _upload(client, enable_cloning="true", speaker_cloning_consent="true")
    assert res.status_code == 200
    job_id = res.json()["job_id"]

    record = jobs.read_consent_record(jobs.job_paths(job_id))
    assert record["uploader_attestation"] is True
    assert record["voice_cloning_requested"] is True
    assert record["speaker_cloning_consent"] is True
    assert record["speaker_consent_text"] == jobs.SPEAKER_CONSENT_TEXT
    assert record["recorded_at"]
    assert record["input_sha256"] == hashlib.sha256(b"fake-video-bytes").hexdigest()


def test_cloning_denied_without_clone_env_but_job_proceeds(client, monkeypatch):
    monkeypatch.setattr(config, "CLONE_PYTHON", None)
    res = _upload(client, enable_cloning="true", speaker_cloning_consent="true")
    assert res.status_code == 200
    cloning = res.json()["cloning"]
    assert cloning["requested"] is True
    assert cloning["granted"] is False
    assert "SYNCDUB_CLONE_PYTHON" in cloning["reason"]
    # pipeline spawned WITHOUT --clone
    assert "--clone" not in client.spawned[0]


def test_cloning_granted_passes_clone_flag(client, monkeypatch):
    monkeypatch.setattr(config, "CLONE_PYTHON", "/fake/clone/python")
    res = _upload(client, target_lang="mr",
                  enable_cloning="true", speaker_cloning_consent="true")
    assert res.status_code == 200
    assert res.json()["cloning"]["granted"] is True
    assert "--clone" in client.spawned[0]


def test_stock_voice_job_never_gets_clone_flag(client, monkeypatch):
    monkeypatch.setattr(config, "CLONE_PYTHON", "/fake/clone/python")
    res = _upload(client)
    assert res.status_code == 200
    assert res.json()["cloning"] == {"requested": False, "granted": False, "reason": None}
    assert "--clone" not in client.spawned[0]


def test_create_job_records_language_pair_in_progress(client):
    job_id = _upload(client, source_lang="hi", target_lang="en").json()["job_id"]
    data = jobs.read_progress(jobs.job_paths(job_id).progress_path)
    assert data["source_lang"] == "hi"
    assert data["target_lang"] == "en"
    cmd = client.spawned[0]
    assert cmd[cmd.index("--target-lang") + 1] == "en"
