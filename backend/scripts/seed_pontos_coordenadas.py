"""Atualiza latitude/longitude dos pontos turísticos de Maricá."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import PontoTuristico
from scripts.pontos_coordenadas import ALIASES_COORDENADAS, COORDENADAS_POR_NOME, CoordenadaPonto


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def resolve_coordenada(nome: str) -> CoordenadaPonto | None:
    if nome in COORDENADAS_POR_NOME:
        return COORDENADAS_POR_NOME[nome]

    chave = normalize(nome)
    if chave in ALIASES_COORDENADAS:
        return COORDENADAS_POR_NOME.get(ALIASES_COORDENADAS[chave])

    for catalogo_nome, coord in COORDENADAS_POR_NOME.items():
        alvo = normalize(catalogo_nome)
        if chave == alvo:
            return coord
        if len(alvo) >= 8 and (alvo in chave or chave in alvo):
            return coord

    return None


def seed_coordenadas(force: bool = False) -> dict[str, int]:
    db = SessionLocal()
    stats = {"atualizados": 0, "ignorados": 0, "sem_coordenada": 0}

    try:
        pontos = db.query(PontoTuristico).order_by(PontoTuristico.id).all()
        for ponto in pontos:
            coord = resolve_coordenada(ponto.nome)
            if not coord:
                stats["sem_coordenada"] += 1
                continue

            if (
                not force
                and round(ponto.latitude, 6) == round(coord.latitude, 6)
                and round(ponto.longitude, 6) == round(coord.longitude, 6)
            ):
                stats["ignorados"] += 1
                continue

            ponto.latitude = coord.latitude
            ponto.longitude = coord.longitude
            if coord.rua_numero:
                ponto.rua_numero = coord.rua_numero
            stats["atualizados"] += 1

        db.commit()
        stats["total"] = len(pontos)
        return stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Atualiza coordenadas dos pontos turísticos.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Atualiza mesmo quando as coordenadas já coincidem",
    )
    args = parser.parse_args()

    stats = seed_coordenadas(force=args.force)
    print("Coordenadas dos pontos:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
