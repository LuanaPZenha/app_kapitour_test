from pathlib import Path

base = Path(__file__).resolve().parents[1] / "services"

SHIM_MODELS = (
    '"""Compatibilidade — camada de infraestrutura (persistência)."""\n'
    "from app.infraestrutura.persistencia.modelos import *  # noqa: F403\n"
)
SHIM_REPOS = (
    '"""Compatibilidade — adaptadores de persistência."""\n'
    "from app.infraestrutura.persistencia.repositorios import *  # noqa: F403\n"
)
SHIM_ESQ = (
    '"""Compatibilidade — DTOs da camada de apresentação."""\n'
    "from app.apresentacao.esquemas import *  # noqa: F403\n"
)
SHIM_DEP = (
    '"""Compatibilidade — composição de dependências."""\n'
    "from app.apresentacao.dependencias import *  # noqa: F403\n"
)
SHIM_ROT = (
    '"""Compatibilidade — adaptadores HTTP."""\n'
    "from app.apresentacao.roteadores import roteador\n"
)
SHIM_SVC = (
    '"""Compatibilidade — casos de uso."""\n'
    "from app.dominio.casos_de_uso.servicos import *  # noqa: F403\n"
)
SHIM_KAPI = (
    '"""Compatibilidade — orquestração de casos de uso."""\n'
    "from app.aplicacao.servicos import *  # noqa: F403\n"
)


def substituir_imports(texto: str) -> str:
    texto = texto.replace("from app.modelos import", "from app.infraestrutura.persistencia.modelos import")
    texto = texto.replace("from app.repositorios import", "from app.infraestrutura.persistencia.repositorios import")
    texto = texto.replace("from app.validadores", "from app.dominio.regras")
    texto = texto.replace("from app.dependencias import", "from app.apresentacao.dependencias import")
    texto = texto.replace("from app.servicos import", "from app.dominio.casos_de_uso.servicos import")
    texto = texto.replace("from app.esquemas import", "from app.apresentacao.esquemas import")
    texto = texto.replace("from app.estrategias", "from app.dominio.estrategias")
    texto = texto.replace("from app.eventos", "from app.dominio.eventos")
    return texto


def substituir_imports_kapipass(texto: str) -> str:
    texto = substituir_imports(texto)
    return texto.replace(
        "from app.dominio.casos_de_uso.servicos import",
        "from app.aplicacao.servicos import",
    )


def main() -> None:
    for svc in ["content", "commerce", "engagement", "kapipass"]:
        app = base / svc / "app"
        (app / "modelos.py").write_text(SHIM_MODELS, encoding="utf-8")
        (app / "repositorios.py").write_text(SHIM_REPOS, encoding="utf-8")
        (app / "esquemas.py").write_text(SHIM_ESQ, encoding="utf-8")
        (app / "dependencias.py").write_text(SHIM_DEP, encoding="utf-8")
        (app / "roteadores.py").write_text(SHIM_ROT, encoding="utf-8")

    for svc in ["content", "commerce", "engagement"]:
        (base / svc / "app" / "servicos.py").write_text(SHIM_SVC, encoding="utf-8")
    (base / "kapipass" / "app" / "servicos.py").write_text(SHIM_KAPI, encoding="utf-8")

    for svc in ["content", "commerce", "engagement"]:
        for path in (base / svc / "app").rglob("*.py"):
            if path.name == "__init__.py" or "validadores" in path.parts:
                continue
            if path in {
                base / svc / "app" / "modelos.py",
                base / svc / "app" / "repositorios.py",
                base / svc / "app" / "servicos.py",
                base / svc / "app" / "esquemas.py",
                base / svc / "app" / "dependencias.py",
                base / svc / "app" / "roteadores.py",
            }:
                continue
            texto = path.read_text(encoding="utf-8")
            novo = substituir_imports(texto)
            if novo != texto:
                path.write_text(novo, encoding="utf-8")

    for path in (base / "kapipass" / "app").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        if path in {
            base / "kapipass" / "app" / "modelos.py",
            base / "kapipass" / "app" / "repositorios.py",
            base / "kapipass" / "app" / "servicos.py",
            base / "kapipass" / "app" / "esquemas.py",
            base / "kapipass" / "app" / "dependencias.py",
            base / "kapipass" / "app" / "roteadores.py",
        }:
            continue
        if path.parent.name in {"estrategias", "eventos"} and "dominio" not in path.parts:
            continue
        texto = path.read_text(encoding="utf-8")
        novo = substituir_imports_kapipass(texto)
        if novo != texto:
            path.write_text(novo, encoding="utf-8")

    print("migracao clean arch concluida")


if __name__ == "__main__":
    main()
