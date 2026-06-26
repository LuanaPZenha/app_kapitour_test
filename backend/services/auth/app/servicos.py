from app.esquemas import UsuarioResponse
from app.repositorios import RepositorioUsuario
from kapitour_shared.autenticacao import criar_token_acesso


class ServicoAutenticacao:
    """SRP: regras de cadastro e login. Persistência delegada ao repositório (DIP)."""

    def __init__(
        self,
        repositorio: RepositorioUsuario,
        gerador_token=criar_token_acesso,
    ):
        self._usuarios = repositorio
        self._gerar_token = gerador_token

    def registrar(self, nome, email, password, **kwargs) -> dict:
        if self._usuarios.email_existe(email):
            raise ValueError("Este email já está cadastrado.")
        usuario = self._usuarios.criar(
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
        usuario = self._usuarios.autenticar(email, password)
        if not usuario:
            raise ValueError("Credenciais inválidas.")
        return self._montar_resposta_token(usuario)

    def _montar_resposta_token(self, usuario) -> dict:
        token = self._gerar_token(usuario.auth_id, usuario.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(usuario),
        }


class ServicoUsuario:
    """SRP: consulta e atualização de perfil."""

    def __init__(self, repositorio: RepositorioUsuario):
        self._usuarios = repositorio

    def buscar_por_auth_id(self, auth_id: str):
        return self._usuarios.buscar_por_auth_id(auth_id)

    def atualizar(self, auth_id: str, dados: dict):
        usuario = self._usuarios.buscar_por_auth_id(auth_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        self._validar_email_unico(usuario, dados)
        return self._usuarios.atualizar(usuario, dados)

    def _validar_email_unico(self, usuario, dados: dict) -> None:
        if not dados.get("email"):
            return
        existente = self._usuarios.buscar_por_email(dados["email"])
        if existente and existente.id != usuario.id:
            raise ValueError("Email já cadastrado.")
