"""Unit tests for job identity, progress reporting, and the single-run lock."""
import json
import os

import pytest

import config
import jobs


@pytest.fixture
def tmp_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "TEMP_DIR", tmp_path / "temp")
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setattr(config, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(config, "PROGRESS_DIR", tmp_path / "progress")
    monkeypatch.setattr(config, "JOBS_DIR", tmp_path / "jobs")
    monkeypatch.setattr(jobs, "LOCK_PATH", tmp_path / ".pipeline.lock")
    return tmp_path


# ---------------- job ids & paths ----------------

def test_new_job_ids_are_unique_and_short():
    ids = {jobs.new_job_id() for _ in range(100)}
    assert len(ids) == 100
    assert all(len(i) == 12 and i.isalnum() for i in ids)


def test_job_paths_are_scoped_by_job_id(tmp_dirs):
    p = jobs.job_paths("abc123")
    assert p.temp_dir.name == "abc123"
    assert p.output_path.name == "abc123.mp4"
    assert p.progress_path.name == "abc123.json"
    assert p.consent_path.parent == p.job_dir
    assert p.metrics_path.parent == p.job_dir
    assert p.log_path.parent == p.job_dir


# ---------------- ProgressWriter ----------------

def test_progress_writer_update_and_done(tmp_dirs):
    p = jobs.job_paths("j1")
    w = jobs.ProgressWriter(p.progress_path, "j1", fields={"cloning_requested": True})
    w.update(10, "Extracting audio")

    data = json.loads(p.progress_path.read_text(encoding="utf-8"))
    assert data == {
        "job_id": "j1", "progress": 10, "status": "Extracting audio",
        "state": "running", "error": None, "cloning_requested": True,
    }

    w.done(video_url="/outputs/j1.mp4")
    data = json.loads(p.progress_path.read_text(encoding="utf-8"))
    assert data["state"] == "done"
    assert data["progress"] == 100
    assert data["video_url"] == "/outputs/j1.mp4"


def test_progress_writer_fail_records_error_and_keeps_progress(tmp_dirs):
    p = jobs.job_paths("j2")
    w = jobs.ProgressWriter(p.progress_path, "j2")
    w.update(50, "Translating")
    w.fail("boom")

    data = json.loads(p.progress_path.read_text(encoding="utf-8"))
    assert data["state"] == "error"
    assert data["error"] == "boom"
    assert data["progress"] == 50


def test_progress_writer_set_fields_merges(tmp_dirs):
    p = jobs.job_paths("j3")
    w = jobs.ProgressWriter(p.progress_path, "j3")
    w.update(70, "Synthesizing")
    w.set_fields(synthesizer_used="edge_tts", fallback_reason="no consent")

    data = json.loads(p.progress_path.read_text(encoding="utf-8"))
    assert data["synthesizer_used"] == "edge_tts"
    assert data["fallback_reason"] == "no consent"
    assert data["progress"] == 70


def test_progress_writer_leaves_no_tmp_file(tmp_dirs):
    p = jobs.job_paths("j4")
    w = jobs.ProgressWriter(p.progress_path, "j4")
    w.update(1, "x")
    leftovers = [f for f in os.listdir(p.progress_path.parent) if f.endswith(".tmp")]
    assert leftovers == []


def test_read_progress_unknown_job_returns_none(tmp_dirs):
    assert jobs.read_progress(jobs.job_paths("nope").progress_path) is None


def test_read_progress_tolerates_mid_write_empty_file(tmp_dirs):
    p = jobs.job_paths("j5")
    p.progress_path.parent.mkdir(parents=True)
    p.progress_path.write_text("")
    data = jobs.read_progress(p.progress_path)
    assert data["state"] == "running"


# ---------------- pipeline lock ----------------

def test_lock_acquire_release_cycle(tmp_dirs):
    assert jobs.acquire_pipeline_lock("a") is True
    assert jobs.lock_holder() == "a"
    assert jobs.acquire_pipeline_lock("b") is False
    jobs.release_pipeline_lock("a")
    assert jobs.lock_holder() is None
    assert jobs.acquire_pipeline_lock("b") is True
    jobs.release_pipeline_lock("b")


def test_lock_release_ignores_non_owner(tmp_dirs):
    assert jobs.acquire_pipeline_lock("owner") is True
    jobs.release_pipeline_lock("intruder")
    assert jobs.lock_holder() == "owner"
    jobs.release_pipeline_lock("owner")


def test_stale_lock_from_dead_pid_is_stolen(tmp_dirs, monkeypatch):
    ghost_pid = 2 ** 22 + 12345
    jobs.LOCK_PATH.write_text(json.dumps({"pid": ghost_pid, "job_id": "ghost"}))
    monkeypatch.setattr(jobs, "_pid_alive", lambda pid: pid != ghost_pid)
    assert jobs.lock_holder() is None
    assert jobs.acquire_pipeline_lock("fresh") is True
    assert jobs.lock_holder() == "fresh"
    jobs.release_pipeline_lock("fresh")


def test_corrupt_lock_file_is_treated_as_stale(tmp_dirs):
    jobs.LOCK_PATH.write_text("{not json")
    assert jobs.lock_holder() is None
    assert jobs.acquire_pipeline_lock("fresh") is True
    jobs.release_pipeline_lock("fresh")
