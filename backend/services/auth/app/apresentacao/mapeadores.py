from app.apresentacao.esquemas import TokenResponse, UsuarioResponse
from app.dominio.entidades.resultado_autenticacao import ResultadoAutenticacao
from app.dominio.entidades.usuario import Usuario


def usuario_para_resposta(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        auth_id=usuario.auth_id,
        nome=usuario.nome,
        email=usuario.email,
        cpf=usuario.cpf,
        sexo=usuario.sexo,
        data_nascimento=usuario.data_nascimento,
        data_criacao=usuario.data_criacao,
        tipo_usuario_id=usuario.tipo_usuario_id,
    )


def autenticacao_para_resposta(resultado: ResultadoAutenticacao) -> TokenResponse:
    return TokenResponse(
        access_token=resultado.token,
        user=usuario_para_resposta(resultado.usuario),
    )
