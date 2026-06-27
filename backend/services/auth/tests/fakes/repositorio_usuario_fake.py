from datetime import datetime

from app.dominio.entidades.usuario import Usuario


class RepositorioUsuarioFake:
    """Fake in-memory do repositório de usuários para testes unitários."""

    def __init__(self):
        self._registros: list[dict] = []
        self._proximo_id = 1

    def email_existe(self, email: str) -> bool:
        return any(r["usuario"].email == email for r in self._registros)

    def criar(self, nome, email, password, **kwargs) -> Usuario:
        usuario = Usuario(
            id=self._proximo_id,
            auth_id=f"auth-{self._proximo_id}",
            nome=nome,
            email=email,
            tipo_usuario_id=kwargs.get("tipo_usuario_id", 3),
            cpf=kwargs.get("cpf"),
            sexo=kwargs.get("sexo"),
            data_nascimento=kwargs.get("data_nascimento"),
            data_criacao=datetime.utcnow(),
        )
        self._registros.append({"usuario": usuario, "password": password})
        self._proximo_id += 1
        return usuario

    def autenticar(self, email: str, password: str) -> Usuario | None:
        for registro in self._registros:
            if registro["usuario"].email == email and registro["password"] == password:
                return registro["usuario"]
        return None

    def buscar_por_auth_id(self, auth_id: str) -> Usuario | None:
        for registro in self._registros:
            if registro["usuario"].auth_id == auth_id:
                return registro["usuario"]
        return None

    def buscar_por_email(self, email: str) -> Usuario | None:
        for registro in self._registros:
            if registro["usuario"].email == email:
                return registro["usuario"]
        return None

    def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        for registro in self._registros:
            if registro["usuario"].id == usuario.id:
                if "nome" in dados:
                    registro["usuario"].nome = dados["nome"]
                if "email" in dados:
                    registro["usuario"].email = dados["email"]
                if "cpf" in dados:
                    registro["usuario"].cpf = dados["cpf"]
                return registro["usuario"]
        raise ValueError("Usuário não encontrado.")


class GeradorTokenFake:
    def gerar(self, auth_id: str, usuario_id: int, tipo_usuario_id: int = 3) -> tuple[str, str]:
        return f"token-{auth_id}-{usuario_id}", f"refresh-{auth_id}-{usuario_id}"
