#!/usr/bin/env python3
"""
Migra database/kapitour.db (monolito) para os bancos separados dos microserviços.

Uso:
  python backend/scripts/split_database.py
  python backend/scripts/split_database.py --source database/kapitour.db
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "database" / "kapitour.db"

SPLIT: dict[str, list[str]] = {
    "auth.db": ["usuarios"],
    "content.db": [
        "categorias",
        "pontos_turisticos",
        "ponto_categoria",
        "rotas",
        "rota_ponto",
    ],
    "engagement.db": ["favoritos", "avaliacoes", "ponto_avaliacoes"],
    "commerce.db": [
        "tipos_produto",
        "produtos",
        "estoque",
        "campanhas",
        "cupons",
        "cupons_resgatados",
    ],
    "kapipass.db": [
        "kapipass_niveis",
        "usuario_xp",
        "kapipass_carimbos",
        "usuario_carimbos",
        "checkins",
        "conquistas",
        "usuario_conquistas",
        "colecoes",
        "colecao_pontos",
        "missoes",
        "usuario_missoes",
        "eco_atividades",
        "usuario_eco_atividades",
        "diario_viagem",
        "tesouros",
        "usuario_tesouros",
    ],
}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _copy_table(source: sqlite3.Connection, target: sqlite3.Connection, table: str) -> int:
    if not _table_exists(source, table):
        return 0

    ddl_row = source.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if not ddl_row or not ddl_row[0]:
        return 0

    target.execute(f"DROP TABLE IF EXISTS {table}")
    target.execute(ddl_row[0])

    rows = source.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        return 0

    col_count = len(rows[0])
    placeholders = ",".join("?" for _ in range(col_count))
    target.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    return len(rows)


def split_database(source_path: Path, backup: bool = True) -> None:
    if not source_path.exists():
        raise FileNotFoundError(f"Banco monolito não encontrado: {source_path}")

    db_dir = source_path.parent
    db_dir.mkdir(parents=True, exist_ok=True)

    if backup:
        backup_path = db_dir / f"{source_path.stem}.backup{source_path.suffix}"
        if not backup_path.exists():
            shutil.copy2(source_path, backup_path)
            print(f"Backup criado: {backup_path}")

    source = sqlite3.connect(source_path)
    try:
        for target_name, tables in SPLIT.items():
            target_path = db_dir / target_name
            if target_path.exists():
                target_path.unlink()

            target = sqlite3.connect(target_path)
            try:
                copied = 0
                for table in tables:
                    count = _copy_table(source, target, table)
                    copied += count
                    if count:
                        print(f"  {target_name}: {table} ({count} registros)")
                target.commit()
                print(f"OK {target_name} ({copied} registros no total)")
            finally:
                target.close()
    finally:
        source.close()

    print("\nMigração concluída. Suba os microserviços com: docker compose up --build")


def main() -> None:
    parser = argparse.ArgumentParser(description="Divide o banco monolito em microserviços")
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE),
        help="Caminho do SQLite monolito (padrão: database/kapitour.db)",
    )
    parser.add_argument("--no-backup", action="store_true", help="Não criar backup do monolito")
    args = parser.parse_args()
    split_database(Path(args.source), backup=not args.no_backup)


if __name__ == "__main__":
    main()
