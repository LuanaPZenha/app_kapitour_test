from app.dominio.entidades.usuario import Usuario
from app.dominio.portas.repositorio_usuario import ContratoRepositorioUsuario


class CasoBuscarUsuarioPorAuthId:
    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, auth_id: str) -> Usuario | None:
        return self._usuarios.buscar_por_auth_id(auth_id)


class CasoAtualizarPerfilUsuario:
    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, auth_id: str, dados: dict) -> Usuario:
        usuario = self._usuarios.buscar_por_auth_id(auth_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        self._validar_email_unico(usuario, dados)
        return self._usuarios.atualizar(usuario, dados)

    def _validar_email_unico(self, usuario: Usuario, dados: dict) -> None:
        if not dados.get("email"):
            return
        existente = self._usuarios.buscar_por_email(dados["email"])
        if existente and existente.id != usuario.id:
            raise ValueError("Email já cadastrado.")


class CasoVerificarEmailExiste:
    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, email: str) -> bool:
        return self._usuarios.email_existe(email)
