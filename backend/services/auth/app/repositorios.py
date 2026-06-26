from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modelos import Usuario
from kapitour_shared.autenticacao import gerar_hash_senha, senha_confere


class RepositorioUsuario:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def buscar_por_auth_id(self, auth_id: str) -> Usuario | None:
        return self.sessao.query(Usuario).filter(Usuario.auth_id == auth_id).first()

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return self.sessao.query(Usuario).filter(Usuario.id == usuario_id).first()

    def buscar_por_ids(self, ids_usuarios: list[int]) -> list[Usuario]:
        if not ids_usuarios:
            return []
        return self.sessao.query(Usuario).filter(Usuario.id.in_(ids_usuarios)).all()

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.sessao.query(Usuario).filter(Usuario.email == email.lower()).first()

    def email_existe(self, email: str) -> bool:
        return self.buscar_por_email(email) is not None

    def criar(self, nome: str, email: str, password: str, **kwargs) -> Usuario:
        usuario = Usuario(
            auth_id=str(uuid4()),
            nome=nome,
            email=email.lower(),
            senha_hash=gerar_hash_senha(password),
            data_criacao=datetime.utcnow(),
            **kwargs,
        )
        self.sessao.add(usuario)
        self.sessao.commit()
        self.sessao.refresh(usuario)
        return usuario

    def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        for chave, valor in dados.items():
            if valor is not None and hasattr(usuario, chave):
                setattr(usuario, chave, valor)
        self.sessao.commit()
        self.sessao.refresh(usuario)
        return usuario

    def autenticar(self, email: str, password: str) -> Usuario | None:
        usuario = self.buscar_por_email(email)
        if not usuario or not senha_confere(password, usuario.senha_hash):
            return None
        return usuario
