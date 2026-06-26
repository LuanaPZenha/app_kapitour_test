from app.dominio.entidades.resultado_autenticacao import ResultadoAutenticacao
from app.dominio.portas.gerador_token import ContratoGeradorToken
from app.dominio.portas.repositorio_usuario import ContratoRepositorioUsuario


class CasoRegistrarUsuario:
    """Caso de uso: cadastrar novo usuário."""

    def __init__(
        self,
        repositorio: ContratoRepositorioUsuario,
        gerador_token: ContratoGeradorToken,
    ):
        self._usuarios = repositorio
        self._gerar_token = gerador_token

    def executar(self, nome, email, password, **kwargs) -> ResultadoAutenticacao:
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
        token = self._gerar_token(usuario.auth_id, usuario.id)
        return ResultadoAutenticacao(token=token, usuario=usuario)


class CasoEntrarUsuario:
    """Caso de uso: autenticar com email e senha."""

    def __init__(
        self,
        repositorio: ContratoRepositorioUsuario,
        gerador_token: ContratoGeradorToken,
    ):
        self._usuarios = repositorio
        self._gerar_token = gerador_token

    def executar(self, email: str, password: str) -> ResultadoAutenticacao:
        usuario = self._usuarios.autenticar(email, password)
        if not usuario:
            raise ValueError("Credenciais inválidas.")
        token = self._gerar_token(usuario.auth_id, usuario.id)
        return ResultadoAutenticacao(token=token, usuario=usuario)
