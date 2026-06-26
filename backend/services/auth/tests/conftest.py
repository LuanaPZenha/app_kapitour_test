import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[3]
if str(BACKEND / "shared") not in sys.path:
    sys.path.insert(0, str(BACKEND / "shared"))
if str(BACKEND / "services" / "auth") not in sys.path:
    sys.path.insert(0, str(BACKEND / "services" / "auth"))
TESTS = Path(__file__).resolve().parent
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import pytest


@pytest.fixture
def contexto_bdd():
    """Estado compartilhado entre passos BDD (Dado/Quando/Então)."""
    return {}
