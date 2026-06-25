"""Importa dados de um dump PostgreSQL (Supabase) para o SQLite local."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.migrations import run_migrations, seed_demo_users
from app.models import Categoria, PontoCategoria, PontoTuristico, Rota, RotaPonto, Usuario

COPY_START = re.compile(
    r"^COPY (?:(public)\.(\w+)|(auth)\.(\w+)) \(([^)]+)\) FROM stdin;$"
)


def normalize_image_url(url: str | None) -> str | None:
    if not url:
        return None
    marker = "github.com/Kapitour/Imgs-Padr-o/blob/"
    if marker in url:
        path = url.split("/blob/main/", 1)[1].split("?", 1)[0]
        return f"https://raw.githubusercontent.com/Kapitour/Imgs-Padr-o/main/{unquote(path)}"
    return url


def unescape_copy_value(value: str) -> str | None:
    if value == r"\N":
        return None

    chars: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            if nxt == "n":
                chars.append("\n")
            elif nxt == "t":
                chars.append("\t")
            elif nxt == "r":
                chars.append("\r")
            elif nxt == "b":
                chars.append("\b")
            elif nxt == "f":
                chars.append("\f")
            elif nxt == "v":
                chars.append("\v")
            elif nxt == "\\":
                chars.append("\\")
            else:
                chars.append(nxt)
            i += 2
        else:
            chars.append(value[i])
            i += 1
    return "".join(chars)


def parse_row(columns: list[str], line: str) -> dict[str, str | None]:
    parts = line.split("\t")
    if len(parts) != len(columns):
        raise ValueError(
            f"Colunas esperadas: {len(columns)}, recebidas: {len(parts)} — linha: {line[:120]}..."
        )
    return {col: unescape_copy_value(val) for col, val in zip(columns, parts)}


def load_copy_tables(backup_path: Path) -> dict[str, dict]:
    tables: dict[str, dict] = {}
    with backup_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = COPY_START.match(line.rstrip("\n"))
            if not match:
                continue

            schema = match.group(1) or match.group(3)
            table = match.group(2) or match.group(4)
            key = f"{schema}.{table}" if schema == "auth" else table
            columns = [col.strip() for col in match.group(5).split(",")]
            rows: list[str] = []

            for row_line in handle:
                if row_line.rstrip("\n") == r"\.":
                    break
                rows.append(row_line.rstrip("\n"))

            tables[key] = {"columns": columns, "rows": rows}

    return tables


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    normalized = value.replace("+00", "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    return datetime.utcnow()


def parse_birth_date(raw_meta: str | None) -> date | None:
    if not raw_meta:
        return None
    try:
        meta = json.loads(raw_meta)
    except json.JSONDecodeError:
        return None
    nascimento = meta.get("nascimento")
    if not nascimento or len(nascimento) != 8:
        return None
    day = int(nascimento[0:2])
    month = int(nascimento[2:4])
    year = int(nascimento[4:8])
    return date(year, month, day)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    return float(value)


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    run_migrations()


def update_sqlite_sequence(db, table: str, max_id: int) -> None:
    if max_id <= 0:
        return

    has_sequence_table = db.execute(
        text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'")
    ).fetchone()
    if not has_sequence_table:
        return

    exists = db.execute(
        text("SELECT 1 FROM sqlite_sequence WHERE name = :name"),
        {"name": table},
    ).fetchone()
    if exists:
        db.execute(
            text("UPDATE sqlite_sequence SET seq = :seq WHERE name = :name"),
            {"seq": max_id, "name": table},
        )
    else:
        db.execute(
            text("INSERT INTO sqlite_sequence (name, seq) VALUES (:name, :seq)"),
            {"name": table, "seq": max_id},
        )


def import_backup(backup_path: Path) -> dict[str, int]:
    tables = load_copy_tables(backup_path)
    reset_database()

    db = SessionLocal()
    counts: dict[str, int] = {}

    try:
        auth_rows = {
            row["id"]: row
            for row in (
                parse_row(tables["auth.users"]["columns"], line)
                for line in tables["auth.users"]["rows"]
            )
        }

        categorias_data = tables.get("categorias")
        if categorias_data:
            for line in categorias_data["rows"]:
                row = parse_row(categorias_data["columns"], line)
                db.add(Categoria(id=parse_int(row["id"]), nome=row["nome"] or ""))
            counts["categorias"] = len(categorias_data["rows"])

        pontos_data = tables.get("pontos_turisticos")
        if pontos_data:
            for line in pontos_data["rows"]:
                row = parse_row(pontos_data["columns"], line)
                db.add(
                    PontoTuristico(
                        id=parse_int(row["id"]),
                        nome=row["nome"] or "",
                        descricao=row["descricao"],
                        rua_numero=row["rua_numero"],
                        latitude=parse_float(row["latitude"]),
                        longitude=parse_float(row["longitude"]),
                        url_img=normalize_image_url(row["url_img"]),
                    )
                )
            counts["pontos_turisticos"] = len(pontos_data["rows"])

        ponto_cat_data = tables.get("ponto_categoria")
        if ponto_cat_data:
            for line in ponto_cat_data["rows"]:
                row = parse_row(ponto_cat_data["columns"], line)
                db.add(
                    PontoCategoria(
                        ponto_id=parse_int(row["ponto_id"]),
                        categoria_id=parse_int(row["categoria_id"]),
                    )
                )
            counts["ponto_categoria"] = len(ponto_cat_data["rows"])

        rotas_data = tables.get("rotas")
        if rotas_data:
            for line in rotas_data["rows"]:
                row = parse_row(rotas_data["columns"], line)
                db.add(
                    Rota(
                        id=parse_int(row["id"]),
                        nome=row["nome"] or "",
                        descricao=row["descricao"],
                    )
                )
            counts["rotas"] = len(rotas_data["rows"])

        rota_ponto_data = tables.get("rota_ponto")
        if rota_ponto_data:
            for line in rota_ponto_data["rows"]:
                row = parse_row(rota_ponto_data["columns"], line)
                db.add(
                    RotaPonto(
                        id=parse_int(row["id"]),
                        rota_id=parse_int(row["rota_id"]),
                        ponto_id=parse_int(row["ponto_id"]),
                        ordem=parse_int(row["ordem"]) or 0,
                    )
                )
            counts["rota_ponto"] = len(rota_ponto_data["rows"])

        usuarios_data = tables.get("usuarios")
        max_usuario_id = 0
        if usuarios_data:
            for line in usuarios_data["rows"]:
                row = parse_row(usuarios_data["columns"], line)
                auth_id = row["user_id"] or ""
                auth = auth_rows.get(auth_id, {})
                meta = auth.get("raw_user_meta_data")
                usuario_id = parse_int(row["id"]) or 0
                max_usuario_id = max(max_usuario_id, usuario_id)

                db.add(
                    Usuario(
                        id=usuario_id,
                        auth_id=auth_id,
                        nome=row["nome"] or "",
                        email=row["email"] or "",
                        cpf=row["cpf"],
                        sexo=row["sexo"],
                        data_nascimento=parse_birth_date(meta),
                        data_criacao=parse_datetime(row["data_criacao"]),
                        tipo_usuario_id=3,
                        senha_hash=auth.get("encrypted_password") or "",
                    )
                )
            counts["usuarios"] = len(usuarios_data["rows"])

        db.flush()

        for table, key in (
            ("categorias", "categorias"),
            ("pontos_turisticos", "pontos_turisticos"),
            ("rotas", "rotas"),
            ("rota_ponto", "rota_ponto"),
        ):
            data = tables.get(key)
            if not data:
                continue
            max_id = max(parse_int(parse_row(data["columns"], line)["id"]) or 0 for line in data["rows"])
            update_sqlite_sequence(db, table, max_id)

        if max_usuario_id:
            update_sqlite_sequence(db, "usuarios", max_usuario_id)

        seed_demo_users(db)
        db.commit()
        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa backup Supabase/PostgreSQL para SQLite.")
    parser.add_argument(
        "backup_path",
        type=Path,
        help="Caminho do arquivo .backup (dump pg_dump)",
    )
    args = parser.parse_args()

    if not args.backup_path.is_file():
        raise SystemExit(f"Arquivo não encontrado: {args.backup_path}")

    counts = import_backup(args.backup_path)
    print("Importação concluída:")
    for table, total in sorted(counts.items()):
        print(f"  {table}: {total} registros")


if __name__ == "__main__":
    main()
