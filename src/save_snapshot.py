from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SNAPSHOT_SCHEMA_VERSION = 1
SNAPSHOT_FILE_PREFIX = "snapshot"
MANIFEST_FILE = "manifest.json"


@dataclass(frozen=True)
class SnapshotCompatibility:
    game_version: str
    schema_version: int = SNAPSHOT_SCHEMA_VERSION


@dataclass(frozen=True)
class SnapshotValidationResult:
    is_valid: bool
    message: str


class SnapshotValidationError(Exception):
    pass


class SnapshotVersionError(SnapshotValidationError):
    pass


class SnapshotCorruptionError(SnapshotValidationError):
    pass


class SnapshotManager:
    """Stores compressed save snapshots in a bounded rolling window."""

    def __init__(
        self,
        snapshot_dir: Path,
        compatibility: SnapshotCompatibility,
        window_size: int = 10,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be greater than zero")

        self.snapshot_dir = Path(snapshot_dir)
        self.compatibility = compatibility
        self.window_size = window_size
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def persist_snapshot(self, run_state: dict[str, Any], reason: str) -> Path:
        now_ms = int(time.time() * 1000)
        file_name = f"{SNAPSHOT_FILE_PREFIX}_{now_ms}_{reason}.json.gz"
        destination = self.snapshot_dir / file_name

        payload: dict[str, Any] = {
            "schema_version": self.compatibility.schema_version,
            "game_version": self.compatibility.game_version,
            "saved_at_ms": now_ms,
            "reason": reason,
            "state": run_state,
        }

        canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        checksum = hashlib.sha256(canonical_payload).hexdigest()
        envelope = {
            "checksum_sha256": checksum,
            "payload": payload,
        }

        self._write_atomic_gzip_json(destination, envelope)
        self._prune_snapshots()
        self._refresh_manifest()
        return destination

    def load_latest_valid_snapshot(self) -> dict[str, Any] | None:
        candidates = sorted(self.snapshot_dir.glob(f"{SNAPSHOT_FILE_PREFIX}_*.json.gz"), reverse=True)

        for candidate in candidates:
            try:
                return self.load_snapshot(candidate)
            except SnapshotValidationError:
                continue

        return None

    def load_snapshot(self, path: Path) -> dict[str, Any]:
        envelope = self._read_gzip_json(path)

        if "checksum_sha256" not in envelope or "payload" not in envelope:
            raise SnapshotCorruptionError("Snapshot envelope is incomplete.")

        payload = envelope["payload"]
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        actual_checksum = hashlib.sha256(canonical_payload).hexdigest()
        if actual_checksum != envelope["checksum_sha256"]:
            raise SnapshotCorruptionError("Snapshot checksum mismatch. File may be corrupted.")

        validation = validate_snapshot_payload(payload, self.compatibility)
        if not validation.is_valid:
            raise SnapshotVersionError(validation.message)

        return payload["state"]

    def _write_atomic_gzip_json(self, destination: Path, data: dict[str, Any]) -> None:
        temp_fd, temp_name = tempfile.mkstemp(prefix="snapshot_", suffix=".tmp", dir=self.snapshot_dir)
        os.close(temp_fd)

        try:
            with gzip.open(temp_name, "wt", encoding="utf-8") as handle:
                json.dump(data, handle, separators=(",", ":"), sort_keys=True)
            shutil.move(temp_name, destination)
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    def _read_gzip_json(self, path: Path) -> dict[str, Any]:
        try:
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise SnapshotCorruptionError(f"Snapshot could not be read: {path.name}") from exc

    def _prune_snapshots(self) -> None:
        snapshots = sorted(self.snapshot_dir.glob(f"{SNAPSHOT_FILE_PREFIX}_*.json.gz"), reverse=True)
        for stale in snapshots[self.window_size :]:
            stale.unlink(missing_ok=True)

    def _refresh_manifest(self) -> None:
        snapshots = sorted(self.snapshot_dir.glob(f"{SNAPSHOT_FILE_PREFIX}_*.json.gz"), reverse=True)
        manifest = {
            "latest": snapshots[0].name if snapshots else None,
            "count": len(snapshots),
            "window_size": self.window_size,
            "schema_version": self.compatibility.schema_version,
            "game_version": self.compatibility.game_version,
            "snapshots": [item.name for item in snapshots],
        }

        with (self.snapshot_dir / MANIFEST_FILE).open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)


def validate_snapshot_payload(
    payload: dict[str, Any],
    compatibility: SnapshotCompatibility,
) -> SnapshotValidationResult:
    required = {"schema_version", "game_version", "saved_at_ms", "reason", "state"}
    missing = sorted(required.difference(payload.keys()))
    if missing:
        return SnapshotValidationResult(False, f"Snapshot missing required fields: {', '.join(missing)}")

    snapshot_schema = payload["schema_version"]
    if snapshot_schema != compatibility.schema_version:
        return SnapshotValidationResult(
            False,
            (
                "Snapshot version mismatch: "
                f"snapshot schema={snapshot_schema}, required schema={compatibility.schema_version}. "
                "This snapshot was created by a different build and cannot be restored."
            ),
        )

    snapshot_game_version = str(payload["game_version"])
    if snapshot_game_version.split(".")[0] != compatibility.game_version.split(".")[0]:
        return SnapshotValidationResult(
            False,
            (
                "Snapshot major-version mismatch: "
                f"snapshot={snapshot_game_version}, current={compatibility.game_version}. "
                "Restore requires a compatible major release."
            ),
        )

    state = payload["state"]
    deterministic_fields = {"rng_seed", "rng_frame_index"}
    if not isinstance(state, dict) or deterministic_fields.difference(state.keys()):
        return SnapshotValidationResult(
            False,
            "Snapshot state is missing deterministic replay fields (rng_seed, rng_frame_index).",
        )

    return SnapshotValidationResult(True, "Snapshot is valid.")


def recover_from_crash(
    snapshot_manager: SnapshotManager,
    has_unclean_shutdown: bool,
    prompt_restore: Callable[[str], bool],
) -> dict[str, Any] | None:
    """Startup hook that prompts user to restore the latest valid snapshot."""
    if not has_unclean_shutdown:
        return None

    latest = snapshot_manager.load_latest_valid_snapshot()
    if latest is None:
        return None

    if prompt_restore("The previous session ended unexpectedly. Restore latest snapshot?"):
        return latest
    return None
