"""Sincroniza dados do Supabase (PostgreSQL) para o SQLite local."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.auth import hash_password
from app.migrations import run_migrations, seed_demo_users
from app.models import Categoria, PontoCategoria, PontoTuristico, Rota, RotaPonto, Usuario
from scripts.import_supabase_backup import (
    normalize_image_url,
    parse_birth_date,
    parse_datetime,
    update_sqlite_sequence,
)


def parse_database_url(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.username is None or parsed.password is None:
        raise ValueError("URL invalida: use postgresql://usuario:senha@host:5432/postgres")
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "dbname": parsed.path.lstrip("/") or "postgres",
        "user": unquote(parsed.username),
        "password": unquote(parsed.password),
        "sslmode": "require",
        "connect_timeout": 15,
    }


def fetch_all(conn, query: str) -> list[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return [dict(row) for row in cur.fetchall()]


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    run_migrations()


def sync_from_supabase(database_url: str) -> dict[str, int]:
    params = parse_database_url(database_url)
    conn = psycopg2.connect(**params)

    try:
        auth_users = {
            row["id"]: row
            for row in fetch_all(
                conn,
                """
                SELECT id, email, encrypted_password, raw_user_meta_data
                FROM auth.users
                WHERE deleted_at IS NULL
                """,
            )
        }
        auth_by_email = {
            (row["email"] or "").lower(): row for row in auth_users.values() if row.get("email")
        }

        categorias = fetch_all(conn, "SELECT id, nome FROM public.categorias ORDER BY id")
        pontos = fetch_all(
            conn,
            """
            SELECT id, nome, descricao, rua_numero, latitude, longitude, url_img
            FROM public.pontos_turisticos
            ORDER BY id
            """,
        )
        ponto_categorias = fetch_all(
            conn, "SELECT ponto_id, categoria_id FROM public.ponto_categoria ORDER BY ponto_id, categoria_id"
        )
        rotas = fetch_all(conn, "SELECT id, nome, descricao FROM public.rotas ORDER BY id")
        rota_pontos = fetch_all(
            conn, "SELECT id, rota_id, ponto_id, ordem FROM public.rota_ponto ORDER BY id"
        )
        usuarios = fetch_all(
            conn,
            """
            SELECT id, nome, email, cpf, sexo, data_criacao, user_id
            FROM public.usuarios
            ORDER BY id
            """,
        )
    finally:
        conn.close()

    reset_database()
    db = SessionLocal()
    counts: dict[str, int] = {}

    try:
        for row in categorias:
            db.add(Categoria(id=row["id"], nome=row["nome"]))
        counts["categorias"] = len(categorias)

        for row in pontos:
            db.add(
                PontoTuristico(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    rua_numero=row["rua_numero"],
                    latitude=float(row["latitude"]) if row["latitude"] is not None else None,
                    longitude=float(row["longitude"]) if row["longitude"] is not None else None,
                    url_img=normalize_image_url(row["url_img"]),
                )
            )
        counts["pontos_turisticos"] = len(pontos)
        counts["pontos_com_imagem"] = sum(1 for row in pontos if row["url_img"])

        for row in ponto_categorias:
            db.add(PontoCategoria(ponto_id=row["ponto_id"], categoria_id=row["categoria_id"]))
        counts["ponto_categoria"] = len(ponto_categorias)

        for row in rotas:
            db.add(Rota(id=row["id"], nome=row["nome"], descricao=row["descricao"]))
        counts["rotas"] = len(rotas)

        for row in rota_pontos:
            db.add(
                RotaPonto(
                    id=row["id"],
                    rota_id=row["rota_id"],
                    ponto_id=row["ponto_id"],
                    ordem=row["ordem"] or 0,
                )
            )
        counts["rota_ponto"] = len(rota_pontos)

        max_usuario_id = 0
        for row in usuarios:
            auth_id = row["user_id"]
            auth = auth_users.get(auth_id, {}) if auth_id else {}
            if not auth_id:
                email_match = auth_by_email.get((row["email"] or "").lower())
                if email_match:
                    auth_id = email_match["id"]
                    auth = email_match
                else:
                    auth_id = str(uuid4())

            usuario_id = row["id"]
            max_usuario_id = max(max_usuario_id, usuario_id)
            meta = auth.get("raw_user_meta_data")
            if isinstance(meta, dict):
                meta_json = json.dumps(meta)
            else:
                meta_json = meta
            senha_hash = auth.get("encrypted_password") or hash_password(secrets.token_urlsafe(24))
            db.add(
                Usuario(
                    id=usuario_id,
                    auth_id=auth_id,
                    nome=row["nome"],
                    email=row["email"],
                    cpf=row["cpf"],
                    sexo=row["sexo"],
                    data_nascimento=parse_birth_date(meta_json),
                    data_criacao=parse_datetime(
                        row["data_criacao"].isoformat()
                        if isinstance(row["data_criacao"], datetime)
                        else str(row["data_criacao"])
                    ),
                    tipo_usuario_id=3,
                    senha_hash=senha_hash,
                )
            )
        counts["usuarios"] = len(usuarios)

        db.flush()

        if categorias:
            update_sqlite_sequence(db, "categorias", max(r["id"] for r in categorias))
        if pontos:
            update_sqlite_sequence(db, "pontos_turisticos", max(r["id"] for r in pontos))
        if rotas:
            update_sqlite_sequence(db, "rotas", max(r["id"] for r in rotas))
        if rota_pontos:
            update_sqlite_sequence(db, "rota_ponto", max(r["id"] for r in rota_pontos))
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
    parser = argparse.ArgumentParser(description="Sincroniza Supabase -> SQLite")
    parser.add_argument(
        "--database-url",
        default=os.getenv("SUPABASE_DATABASE_URL"),
        help="postgresql://postgres:senha@db....supabase.co:5432/postgres",
    )
    args = parser.parse_args()

    if not args.database_url:
        raise SystemExit("Defina SUPABASE_DATABASE_URL ou passe --database-url")

    try:
        counts = sync_from_supabase(args.database_url)
    except psycopg2.OperationalError as exc:
        raise SystemExit(f"Falha ao conectar no Supabase: {exc}") from exc

    print("Sincronizacao concluida:")
    for table, total in sorted(counts.items()):
        print(f"  {table}: {total}")


if __name__ == "__main__":
    main()
