#!/usr/bin/env python3
"""Garante que os microserviços usem os dados de Maricá do kapitour.db quando existir."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "database"
MONOLITH = DB_DIR / "kapitour.db"
CONTENT = DB_DIR / "content.db"

# Menos que isso indica seed de demo (Salvador) ou banco vazio incorreto.
MIN_PONTOS_MARICA = 10


def _count_pontos(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM pontos_turisticos").fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()


def needs_migration() -> bool:
    if not MONOLITH.exists():
        return False
    monolith_count = _count_pontos(MONOLITH)
    if monolith_count < MIN_PONTOS_MARICA:
        return False
    content_count = _count_pontos(CONTENT)
    return content_count < monolith_count


def main() -> int:
    if not needs_migration():
        return 0

    print(f"Migrando {MONOLITH.name} → microserviços ({_count_pontos(MONOLITH)} pontos)...")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from split_database import split_database

    split_database(MONOLITH, backup=False)
    print("Dados de Maricá restaurados nos microserviços.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
