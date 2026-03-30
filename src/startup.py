from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.save_snapshot import SnapshotCompatibility, SnapshotManager, recover_from_crash


class StartupCoordinator:
    def __init__(
        self,
        save_root: Path,
        game_version: str,
        prompt_restore: Callable[[str], bool],
    ) -> None:
        self.snapshot_manager = SnapshotManager(
            snapshot_dir=save_root / "snapshots",
            compatibility=SnapshotCompatibility(game_version=game_version),
            window_size=10,
        )
        self.prompt_restore = prompt_restore

    def bootstrap_run_state(self, has_unclean_shutdown: bool, active_save: dict[str, Any]) -> dict[str, Any]:
        restored = recover_from_crash(
            snapshot_manager=self.snapshot_manager,
            has_unclean_shutdown=has_unclean_shutdown,
            prompt_restore=self.prompt_restore,
        )
        if restored is not None:
            return restored
        return active_save

    def snapshot_after_room(self, run_state: dict[str, Any]) -> None:
        self.snapshot_manager.persist_snapshot(run_state=run_state, reason="room_end")

    def snapshot_after_combat(self, run_state: dict[str, Any]) -> None:
        self.snapshot_manager.persist_snapshot(run_state=run_state, reason="combat_end")
