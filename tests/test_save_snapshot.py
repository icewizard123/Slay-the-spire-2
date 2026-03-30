from __future__ import annotations

import gzip
import json
import tempfile
import unittest
from pathlib import Path

from src.save_snapshot import (
    SnapshotCompatibility,
    SnapshotCorruptionError,
    SnapshotManager,
    SnapshotVersionError,
    recover_from_crash,
)


class SnapshotManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.snapshot_dir = Path(self.temp_dir.name)
        self.manager = SnapshotManager(
            snapshot_dir=self.snapshot_dir,
            compatibility=SnapshotCompatibility(game_version="1.2.3"),
            window_size=3,
        )
        self.base_state = {
            "hp": 70,
            "gold": 99,
            "rng_seed": 12345,
            "rng_frame_index": 42,
        }

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_rolling_window_prunes_old_snapshots(self) -> None:
        for i in range(6):
            state = {**self.base_state, "rng_frame_index": i}
            self.manager.persist_snapshot(state, reason="room_end")

        snapshots = list(self.snapshot_dir.glob("snapshot_*.json.gz"))
        self.assertEqual(3, len(snapshots))

    def test_corrupted_snapshot_does_not_brick_active_save(self) -> None:
        good = self.manager.persist_snapshot(self.base_state, reason="combat_end")
        with good.open("wb") as handle:
            handle.write(b"not-gzip")

        fallback = self.manager.load_latest_valid_snapshot()
        self.assertIsNone(fallback)

    def test_version_mismatch_message_is_user_facing(self) -> None:
        snapshot = self.manager.persist_snapshot(self.base_state, reason="room_end")

        with gzip.open(snapshot, "rt", encoding="utf-8") as handle:
            envelope = json.load(handle)
        envelope["payload"]["schema_version"] = 999
        canonical = json.dumps(envelope["payload"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        import hashlib
        envelope["checksum_sha256"] = hashlib.sha256(canonical).hexdigest()
        with gzip.open(snapshot, "wt", encoding="utf-8") as handle:
            json.dump(envelope, handle)

        with self.assertRaises(SnapshotVersionError) as ctx:
            self.manager.load_snapshot(snapshot)

        self.assertIn("Snapshot version mismatch", str(ctx.exception))
        self.assertIn("cannot be restored", str(ctx.exception))

    def test_restore_preserves_deterministic_replay_state(self) -> None:
        state = {**self.base_state, "rng_seed": 1337, "rng_frame_index": 777}
        self.manager.persist_snapshot(state, reason="combat_end")

        restored = recover_from_crash(
            snapshot_manager=self.manager,
            has_unclean_shutdown=True,
            prompt_restore=lambda _: True,
        )

        self.assertIsNotNone(restored)
        self.assertEqual(1337, restored["rng_seed"])
        self.assertEqual(777, restored["rng_frame_index"])

    def test_checksum_failure_raises_corruption_error(self) -> None:
        snapshot = self.manager.persist_snapshot(self.base_state, reason="combat_end")
        with gzip.open(snapshot, "rt", encoding="utf-8") as handle:
            envelope = json.load(handle)
        envelope["payload"]["state"]["gold"] = 9000
        with gzip.open(snapshot, "wt", encoding="utf-8") as handle:
            json.dump(envelope, handle)

        with self.assertRaises(SnapshotCorruptionError):
            self.manager.load_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
