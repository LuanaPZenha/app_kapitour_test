from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    GUIA = "GUIA"
    TURISTA = "TURISTA"
    EMPRESA = "EMPRESA"


# Mapeamento tipo_usuario_id legado → Role
TIPO_USUARIO_PARA_ROLE: dict[int, Role] = {
    1: Role.ADMIN,
    2: Role.EMPRESA,
    3: Role.TURISTA,
    4: Role.GUIA,
}


PERMISSOES_POR_ROLE: dict[Role, set[str]] = {
    Role.ADMIN: {
        "usuarios:ler",
        "usuarios:escrever",
        "usuarios:deletar",
        "conteudo:gerenciar",
        "cupons:gerenciar",
        "kapipass:gerenciar",
        "relatorios:exportar",
    },
    Role.GUIA: {
        "usuarios:ler",
        "conteudo:ler",
        "conteudo:escrever",
        "rotas:gerenciar",
        "kapipass:ler",
    },
    Role.TURISTA: {
        "usuarios:ler_proprio",
        "usuarios:escrever_proprio",
        "conteudo:ler",
        "favoritos:gerenciar",
        "kapipass:participar",
        "cupons:resgatar",
    },
    Role.EMPRESA: {
        "usuarios:ler_proprio",
        "cupons:gerenciar",
        "campanhas:gerenciar",
        "relatorios:exportar",
    },
}


def role_de_tipo_usuario(tipo_usuario_id: int) -> Role:
    return TIPO_USUARIO_PARA_ROLE.get(tipo_usuario_id, Role.TURISTA)


def possui_permissao(role: Role, permissao: str) -> bool:
    return permissao in PERMISSOES_POR_ROLE.get(role, set())
