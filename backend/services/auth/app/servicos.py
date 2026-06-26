"""Compatibilidade — fachada sobre casos de uso (legado)."""

from app.apresentacao.mapeadores import autenticacao_para_resposta, usuario_para_resposta
from app.dominio.casos_de_uso.autenticacao import CasoEntrarUsuario, CasoRegistrarUsuario
from app.dominio.casos_de_uso.perfil import CasoAtualizarPerfilUsuario, CasoBuscarUsuarioPorAuthId
from app.dominio.portas.repositorio_usuario import ContratoRepositorioUsuario
from kapitour_shared.autenticacao import criar_token_acesso


class ServicoAutenticacao:
    def __init__(
        self,
        repositorio: ContratoRepositorioUsuario,
        gerador_token=criar_token_acesso,
    ):
        self._registrar = CasoRegistrarUsuario(repositorio, gerador_token)
        self._entrar = CasoEntrarUsuario(repositorio, gerador_token)

    def registrar(self, nome, email, password, **kwargs) -> dict:
        resultado = self._registrar.executar(nome, email, password, **kwargs)
        resposta = autenticacao_para_resposta(resultado)
        return {"access_token": resposta.access_token, "user": resposta.user}

    def entrar(self, email: str, password: str) -> dict:
        resultado = self._entrar.executar(email, password)
        resposta = autenticacao_para_resposta(resultado)
        return {"access_token": resposta.access_token, "user": resposta.user}


class ServicoUsuario:
    def __init__(self, repositorio: ContratoRepositorioUsuario):
        self._buscar = CasoBuscarUsuarioPorAuthId(repositorio)
        self._atualizar = CasoAtualizarPerfilUsuario(repositorio)

    def buscar_por_auth_id(self, auth_id: str):
        return self._buscar.executar(auth_id)

    def atualizar(self, auth_id: str, dados: dict):
        return self._atualizar.executar(auth_id, dados)
