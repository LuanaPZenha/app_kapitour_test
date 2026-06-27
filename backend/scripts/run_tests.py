#!/usr/bin/env python3
"""Executa testes de um microserviço ou de todos (TDD/BDD)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SERVICOS = ("auth", "content", "commerce", "engagement", "kapipass")
BACKEND = Path(__file__).resolve().parents[1]
SHARED_TESTS = BACKEND / "shared" / "kapitour_shared" / "testes"


def main() -> int:
    parser = argparse.ArgumentParser(description="Rodar pytest por microserviço")
    parser.add_argument(
        "servico",
        nargs="?",
        choices=[*SERVICOS, "shared", "all"],
        default="all",
        help="Microserviço alvo (padrão: all)",
    )
    parser.add_argument(
        "--cov",
        action="store_true",
        help="Inclui relatório de cobertura do kapitour_shared",
    )
    args = parser.parse_args()
    alvos = (
        list(SERVICOS)
        if args.servico == "all"
        else ([] if args.servico == "shared" else [args.servico])
    )
    codigo = 0
    for servico in alvos:
        pasta = BACKEND / "services" / servico / "tests"
        print(f"\n=== Testes: {servico} ===")
        cmd = [sys.executable, "-m", "pytest", str(pasta), "-v"]
        if args.cov:
            cmd.extend(["--cov=kapitour_shared", "--cov-report=term-missing"])
        resultado = subprocess.call(cmd, cwd=BACKEND)
        if resultado != 0:
            codigo = resultado

    if args.servico in ("shared", "all"):
        print("\n=== Testes: shared ===")
        cmd = [sys.executable, "-m", "pytest", str(SHARED_TESTS), "-v"]
        if args.cov:
            cmd.extend(["--cov=kapitour_shared", "--cov-report=term-missing", "--cov-fail-under=70"])
        resultado = subprocess.call(cmd, cwd=BACKEND)
        if resultado != 0:
            codigo = resultado

    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
