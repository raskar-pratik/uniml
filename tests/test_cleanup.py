"""Runnable check for item (2): periodic cleanup sweep of stale artifacts."""

import os
import time

from backend.utils.file_utils import sweep_old_artifacts


def test_sweep_removes_old_keeps_new_and_dotfiles(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()

    old_job = base / "old_job"
    old_job.mkdir()
    (old_job / "model.bin").write_bytes(b"x")

    new_job = base / "new_job"
    new_job.mkdir()
    (new_job / "model.bin").write_bytes(b"x")

    gitkeep = base / ".gitkeep"
    gitkeep.write_text("")

    # Age the old job and the dotfile to 48h ago.
    old_ts = time.time() - 48 * 3600
    os.utime(old_job, (old_ts, old_ts))
    os.utime(gitkeep, (old_ts, old_ts))

    removed = sweep_old_artifacts(max_age_hours=24, dirs=[base])

    assert removed == 1
    assert not old_job.exists()      # stale entry removed
    assert new_job.exists()          # fresh entry kept
    assert gitkeep.exists()          # dotfiles always preserved


def test_sweep_disabled_when_max_age_zero(tmp_path):
    base = tmp_path / "generated"
    base.mkdir()
    d = base / "old"
    d.mkdir()
    old_ts = time.time() - 100 * 3600
    os.utime(d, (old_ts, old_ts))

    assert sweep_old_artifacts(max_age_hours=0, dirs=[base]) == 0
    assert d.exists()
