#!/usr/bin/env python3
"""Smoke tests da API Kapitour via gateway — local ou CI."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def _requisitar(base_url: str, metodo: str, caminho: str, timeout: float) -> tuple[int, dict | list | str | None]:
    url = f"{base_url.rstrip('/')}{caminho}"
    req = urllib.request.Request(url, method=metodo)
    with urllib.request.urlopen(req, timeout=timeout) as resposta:
        corpo = resposta.read().decode()
        try:
            return resposta.status, json.loads(corpo)
        except json.JSONDecodeError:
            return resposta.status, corpo


def _aguardar(base_url: str, timeout: float, intervalo: float) -> bool:
    limite = time.time() + timeout
    while time.time() < limite:
        try:
            status, _ = _requisitar(base_url, "GET", "/api/health", timeout=5)
            if status == 200:
                return True
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(intervalo)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke tests HTTP da API Kapitour")
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--wait", type=float, default=90, help="Segundos aguardando gateway")
    parser.add_argument("--timeout", type=float, default=10, help="Timeout por requisição")
    args = parser.parse_args()

    if not _aguardar(args.base_url, args.wait, intervalo=2):
        print(f"FALHA: gateway indisponível em {args.base_url}", file=sys.stderr)
        return 1

    rotas_publicas = [
        ("GET", "/api/health"),
        ("GET", "/api/categorias"),
        ("GET", "/api/pontos-turisticos"),
        ("GET", "/api/produtos"),
        ("GET", "/api/kapipass/niveis"),
    ]

    falhas = 0
    for metodo, caminho in rotas_publicas:
        try:
            status, corpo = _requisitar(args.base_url, metodo, caminho, args.timeout)
            if status != 200:
                print(f"FALHA {metodo} {caminho}: HTTP {status}")
                falhas += 1
                continue
            if caminho == "/api/health":
                if isinstance(corpo, dict) and corpo.get("status") not in ("ok", "degraded"):
                    print(f"FALHA {caminho}: status inesperado {corpo}")
                    falhas += 1
                    continue
            print(f"OK   {metodo} {caminho}")
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"FALHA {metodo} {caminho}: {exc}")
            falhas += 1

    if falhas:
        print(f"\n{len(rotas_publicas) - falhas}/{len(rotas_publicas)} rotas OK", file=sys.stderr)
        return 1

    print(f"\nSmoke OK — {len(rotas_publicas)} rotas públicas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
