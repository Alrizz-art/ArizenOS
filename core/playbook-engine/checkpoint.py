"""
Checkpoint Manager — SQLite-backed execution state persistence.

Checkpoints allow a failed or interrupted playbook to resume from the
last known-good state rather than restarting from scratch.

Schema:
    checkpoints(run_id, playbook_name, step_id, outputs, created_at, ttl_sec)

Usage:
    mgr = CheckpointManager("memory/persistent/checkpoints.db")
    mgr.save(run_id, "scaffold_structure", outputs={"files": [...]})
    # ... later on resume ...
    state = mgr.load(run_id)
    completed_steps = state.completed_step_ids
"""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("arizen.playbook.checkpoint")

DB_PATH = "memory/persistent/checkpoints.db"


@dataclass
class CheckpointState:
    run_id:              str
    playbook_name:       str
    completed_step_ids:  list[str]                = field(default_factory=list)
    step_outputs:        dict[str, Any]           = field(default_factory=dict)
    variables:           dict[str, Any]           = field(default_factory=dict)
    last_wave:           int                      = 0
    created_at:          float                    = field(default_factory=time.time)
    updated_at:          float                    = field(default_factory=time.time)

    def is_step_done(self, step_id: str) -> bool:
        return step_id in self.completed_step_ids

    def output_of(self, step_id: str) -> Optional[Any]:
        return self.step_outputs.get(step_id)


class CheckpointManager:
    """
    Persists and restores playbook execution state to/from SQLite.

    Every checkpoint write is atomic (WAL mode). TTL-expired checkpoints
    are pruned on startup.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._db   = self._init_db()

    def _init_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                run_id        TEXT NOT NULL,
                playbook_name TEXT NOT NULL,
                step_id       TEXT NOT NULL,
                outputs       TEXT,
                wave          INTEGER DEFAULT 0,
                created_at    REAL,
                ttl_sec       INTEGER DEFAULT 86400,
                PRIMARY KEY (run_id, step_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_variables (
                run_id     TEXT NOT NULL,
                key        TEXT NOT NULL,
                value      TEXT,
                updated_at REAL,
                PRIMARY KEY (run_id, key)
            )
        """)
        conn.commit()
        self._prune_expired(conn)
        return conn

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_step(
        self,
        run_id:       str,
        playbook_name: str,
        step_id:      str,
        outputs:      Any,
        wave:         int = 0,
        ttl_sec:      int = 86400,
    ) -> None:
        now = time.time()
        self._db.execute(
            "INSERT OR REPLACE INTO checkpoints "
            "(run_id, playbook_name, step_id, outputs, wave, created_at, ttl_sec) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, playbook_name, step_id, json.dumps(outputs), wave, now, ttl_sec)
        )
        self._db.commit()
        logger.debug("Checkpoint saved: run=%s step=%s", run_id[:8], step_id)

    def save_variables(self, run_id: str, variables: dict[str, Any]) -> None:
        now = time.time()
        for k, v in variables.items():
            self._db.execute(
                "INSERT OR REPLACE INTO run_variables (run_id, key, value, updated_at) VALUES (?, ?, ?, ?)",
                (run_id, k, json.dumps(v), now)
            )
        self._db.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load(self, run_id: str) -> Optional[CheckpointState]:
        rows = self._db.execute(
            "SELECT playbook_name, step_id, outputs, wave FROM checkpoints WHERE run_id = ? ORDER BY wave",
            (run_id,)
        ).fetchall()

        if not rows:
            return None

        var_rows = self._db.execute(
            "SELECT key, value FROM run_variables WHERE run_id = ?", (run_id,)
        ).fetchall()

        state = CheckpointState(
            run_id        = run_id,
            playbook_name = rows[0][0],
        )
        for _, step_id, outputs_json, wave in rows:
            state.completed_step_ids.append(step_id)
            state.step_outputs[step_id] = json.loads(outputs_json) if outputs_json else None
            state.last_wave = max(state.last_wave, wave)

        for key, val_json in var_rows:
            state.variables[key] = json.loads(val_json) if val_json else None

        return state

    def has_checkpoint(self, run_id: str) -> bool:
        r = self._db.execute(
            "SELECT 1 FROM checkpoints WHERE run_id = ? LIMIT 1", (run_id,)
        ).fetchone()
        return r is not None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def delete_run(self, run_id: str) -> None:
        self._db.execute("DELETE FROM checkpoints WHERE run_id = ?", (run_id,))
        self._db.execute("DELETE FROM run_variables WHERE run_id = ?", (run_id,))
        self._db.commit()

    def _prune_expired(self, conn: sqlite3.Connection) -> None:
        now = time.time()
        conn.execute("DELETE FROM checkpoints WHERE (created_at + ttl_sec) < ?", (now,))
        conn.commit()
