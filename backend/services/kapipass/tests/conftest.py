import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[3]
for caminho in (BACKEND / "shared", BACKEND / "services" / "kapipass"):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))
TESTS = Path(__file__).resolve().parent
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import pytest


@pytest.fixture
def contexto_bdd():
    return {}
