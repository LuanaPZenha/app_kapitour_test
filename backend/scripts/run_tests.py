#!/usr/bin/env python3
"""Executa testes de um microserviço ou de todos (TDD/BDD)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SERVICOS = ("auth", "content", "commerce", "engagement", "kapipass")
BACKEND = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rodar pytest por microserviço")
    parser.add_argument(
        "servico",
        nargs="?",
        choices=[*SERVICOS, "all"],
        default="all",
        help="Microserviço alvo (padrão: all)",
    )
    args = parser.parse_args()
    alvos = (
        list(SERVICOS)
        if args.servico == "all"
        else [args.servico]
    )
    codigo = 0
    for servico in alvos:
        pasta = BACKEND / "services" / servico / "tests"
        print(f"\n=== Testes: {servico} ===")
        cmd = [sys.executable, "-m", "pytest", str(pasta), "-v"]
        resultado = subprocess.call(cmd, cwd=BACKEND)
        if resultado != 0:
            codigo = resultado
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
