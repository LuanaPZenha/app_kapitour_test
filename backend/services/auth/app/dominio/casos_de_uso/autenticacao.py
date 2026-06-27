from app.dominio.entidades.resultado_autenticacao import ResultadoAutenticacao
from app.dominio.portas.repositorio_usuario import ContratoRepositorioUsuario
from app.infraestrutura.adaptadores.gerador_token import AdaptadorGeradorToken


class CasoRegistrarUsuario:
    """Caso de uso: cadastrar novo usuário."""

    def __init__(
        self,
        repositorio: ContratoRepositorioUsuario,
        gerador_token: AdaptadorGeradorToken | None = None,
    ):
        self._usuarios = repositorio
        self._tokens = gerador_token or AdaptadorGeradorToken()

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
        access, refresh = self._tokens.gerar(
            usuario.auth_id, usuario.id, usuario.tipo_usuario_id
        )
        self._enviar_confirmacao_email(usuario)
        return ResultadoAutenticacao(token=access, usuario=usuario, refresh_token=refresh)

    def _enviar_confirmacao_email(self, usuario) -> None:
        if not hasattr(self._usuarios, "criar_token_operacao"):
            return
        try:
            token = self._usuarios.criar_token_operacao(usuario.auth_id, "email_verify", 48)
            link = f"/api/auth/verify-email?token={token}"
            from kapitour_shared.workers.tasks import enviar_email_assincrono

            enviar_email_assincrono.delay(
                usuario.email,
                "Confirme seu e-mail — Kapitour",
                f"<p>Olá {usuario.nome}, confirme seu e-mail: <a href='{link}'>{link}</a></p>",
            )
        except Exception:
            pass


class CasoEntrarUsuario:
    """Caso de uso: autenticar com email e senha."""

    def __init__(
        self,
        repositorio: ContratoRepositorioUsuario,
        gerador_token: AdaptadorGeradorToken | None = None,
    ):
        self._usuarios = repositorio
        self._tokens = gerador_token or AdaptadorGeradorToken()

    def executar(self, email: str, password: str) -> ResultadoAutenticacao:
        usuario = self._usuarios.autenticar(email, password)
        if not usuario:
            raise ValueError("Credenciais inválidas.")
        access, refresh = self._tokens.gerar(
            usuario.auth_id, usuario.id, usuario.tipo_usuario_id
        )
        return ResultadoAutenticacao(token=access, usuario=usuario, refresh_token=refresh)


class CasoRenovarToken:
    """Caso de uso: renovar access token via refresh token."""

    def __init__(self, gerador_token: AdaptadorGeradorToken | None = None):
        self._tokens = gerador_token or AdaptadorGeradorToken()

    def executar(self, refresh_token: str) -> tuple[str, str] | None:
        par = self._tokens.renovar(refresh_token)
        if not par:
            return None
        return par.access_token, par.refresh_token


class CasoLogout:
    """Caso de uso: invalidar tokens na blacklist."""

    def executar(self, access_token: str | None, refresh_token: str | None) -> None:
        from kapitour_shared.security.jwt_service import servico_jwt

        servico_jwt.logout(access_token, refresh_token)


class CasoAlterarSenha:
    """Caso de uso: alterar senha do usuário autenticado."""

    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, auth_id: str, senha_atual: str, nova_senha: str) -> None:
        usuario = self._usuarios.buscar_por_auth_id(auth_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if not self._usuarios.autenticar(usuario.email, senha_atual):
            raise ValueError("Senha atual incorreta.")
        self._usuarios.atualizar_senha(auth_id, nova_senha)
        from kapitour_shared.security.jwt_service import servico_jwt

        servico_jwt.revogar_todas_sessoes(auth_id)


class CasoRecuperarSenha:
    """Caso de uso: solicitar recuperação de senha por e-mail."""

    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, email: str) -> None:
        usuario = self._usuarios.buscar_por_email(email)
        if not usuario:
            return
        try:
            token = self._usuarios.criar_token_operacao(usuario.auth_id, "password_reset", 1)
            from kapitour_shared.workers.tasks import enviar_email_assincrono

            enviar_email_assincrono.delay(
                usuario.email,
                "Recuperação de senha — Kapitour",
                f"<p>Use o token para redefinir sua senha: <code>{token}</code></p>",
            )
        except Exception:
            pass


class CasoRedefinirSenha:
    """Caso de uso: redefinir senha com token de recuperação."""

    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, token: str, nova_senha: str) -> None:
        auth_id = self._usuarios.consumir_token_operacao(token, "password_reset")
        if not auth_id:
            raise ValueError("Token inválido ou expirado.")
        self._usuarios.atualizar_senha(auth_id, nova_senha)
        from kapitour_shared.security.jwt_service import servico_jwt

        servico_jwt.revogar_todas_sessoes(auth_id)


class CasoConfirmarEmail:
    """Caso de uso: confirmar e-mail com token."""

    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._usuarios = repositorio

    def executar(self, token: str) -> None:
        auth_id = self._usuarios.consumir_token_operacao(token, "email_verify")
        if not auth_id:
            raise ValueError("Token inválido ou expirado.")
        self._usuarios.marcar_email_verificado(auth_id)
