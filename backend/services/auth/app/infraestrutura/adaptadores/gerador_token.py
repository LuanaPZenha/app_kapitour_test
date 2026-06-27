from kapitour_shared.security.jwt_service import ParTokens, servico_jwt


class AdaptadorGeradorToken:
    """Adaptador — emite par access/refresh via ServicoJWT compartilhado."""

    def gerar(self, auth_id: str, usuario_id: int, tipo_usuario_id: int = 3) -> tuple[str, str]:
        par = servico_jwt.criar_par_tokens(auth_id, usuario_id, tipo_usuario_id)
        return par.access_token, par.refresh_token

    def renovar(self, refresh_token: str) -> ParTokens | None:
        return servico_jwt.renovar_tokens(refresh_token)
