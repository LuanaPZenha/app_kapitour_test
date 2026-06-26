"""Bootstrap de imports — chame antes de `import app` nos módulos de teste."""

import sys
from pathlib import Path


def preparar_imports(servico: str, arquivo_teste: str) -> None:
    """Insere shared/ e services/<servico>/ no início do PYTHONPATH."""
    backend = Path(arquivo_teste).resolve().parents[3]
    for caminho in (backend / "shared", backend / "services" / servico):
        texto = str(caminho)
        if texto in sys.path:
            sys.path.remove(texto)
        sys.path.insert(0, texto)
    backend_str = str(backend)
    while backend_str in sys.path:
        sys.path.remove(backend_str)
