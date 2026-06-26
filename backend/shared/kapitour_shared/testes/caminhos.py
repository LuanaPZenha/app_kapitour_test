import sys
from pathlib import Path


def configurar_pythonpath(servico: str) -> Path:
    """Insere shared/ e services/<servico>/ no PYTHONPATH para imports `app.*`."""
    backend = Path(__file__).resolve().parents[3]
    shared = backend / "shared"
    raiz_servico = backend / "services" / servico
    for caminho in (str(shared), str(raiz_servico)):
        if caminho not in sys.path:
            sys.path.insert(0, caminho)
    return raiz_servico
