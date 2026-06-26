from sqlalchemy.orm import Session

from app.esquemas import UsuarioResponse
from app.repositorios import RepositorioUsuario
from kapitour_shared.autenticacao import criar_token_acesso


class ServicoAutenticacao:
    def __init__(self, sessao: Session):
        self.usuarios = RepositorioUsuario(sessao)

    def registrar(self, nome, email, password, **kwargs) -> dict:
        if self.usuarios.email_existe(email):
            raise ValueError("Este email já está cadastrado.")
        usuario = self.usuarios.criar(
            nome=nome,
            email=email,
            password=password,
            cpf=kwargs.get("cpf"),
            sexo=kwargs.get("sexo"),
            data_nascimento=kwargs.get("data_nascimento"),
            tipo_usuario_id=kwargs.get("tipo_usuario_id", 3),
        )
        return self._montar_resposta_token(usuario)

    def entrar(self, email: str, password: str) -> dict:
        usuario = self.usuarios.autenticar(email, password)
        if not usuario:
            raise ValueError("Credenciais inválidas.")
        return self._montar_resposta_token(usuario)

    def _montar_resposta_token(self, usuario) -> dict:
        token = criar_token_acesso(usuario.auth_id, usuario.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(usuario),
        }


class ServicoUsuario:
    def __init__(self, sessao: Session):
        self.usuarios = RepositorioUsuario(sessao)

    def buscar_por_auth_id(self, auth_id: str):
        return self.usuarios.buscar_por_auth_id(auth_id)

    def atualizar(self, auth_id: str, dados: dict):
        usuario = self.usuarios.buscar_por_auth_id(auth_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        self._validar_email_unico(usuario, dados)
        return self.usuarios.atualizar(usuario, dados)

    def _validar_email_unico(self, usuario, dados: dict) -> None:
        if not dados.get("email"):
            return
        existente = self.usuarios.buscar_por_email(dados["email"])
        if existente and existente.id != usuario.id:
            raise ValueError("Email já cadastrado.")
