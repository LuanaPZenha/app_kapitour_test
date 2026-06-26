from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.dominio.entidades.usuario import Usuario
from app.infraestrutura.persistencia.modelos import UsuarioModelo
from kapitour_shared.autenticacao import gerar_hash_senha, senha_confere


def _para_entidade(modelo: UsuarioModelo) -> Usuario:
    return Usuario(
        id=modelo.id,
        auth_id=modelo.auth_id,
        nome=modelo.nome,
        email=modelo.email,
        tipo_usuario_id=modelo.tipo_usuario_id,
        cpf=modelo.cpf,
        sexo=modelo.sexo,
        data_nascimento=modelo.data_nascimento,
        data_criacao=modelo.data_criacao,
    )


class RepositorioUsuarioSqlAlchemy:
    """Adaptador de persistência — implementa a porta do domínio."""

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def buscar_por_auth_id(self, auth_id: str) -> Usuario | None:
        modelo = self.sessao.query(UsuarioModelo).filter(UsuarioModelo.auth_id == auth_id).first()
        return _para_entidade(modelo) if modelo else None

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        modelo = self.sessao.query(UsuarioModelo).filter(UsuarioModelo.id == usuario_id).first()
        return _para_entidade(modelo) if modelo else None

    def buscar_por_ids(self, ids_usuarios: list[int]) -> list[Usuario]:
        if not ids_usuarios:
            return []
        modelos = self.sessao.query(UsuarioModelo).filter(UsuarioModelo.id.in_(ids_usuarios)).all()
        return [_para_entidade(m) for m in modelos]

    def buscar_por_email(self, email: str) -> Usuario | None:
        modelo = (
            self.sessao.query(UsuarioModelo).filter(UsuarioModelo.email == email.lower()).first()
        )
        return _para_entidade(modelo) if modelo else None

    def email_existe(self, email: str) -> bool:
        return self.buscar_por_email(email) is not None

    def criar(self, nome: str, email: str, password: str, **kwargs) -> Usuario:
        modelo = UsuarioModelo(
            auth_id=str(uuid4()),
            nome=nome,
            email=email.lower(),
            senha_hash=gerar_hash_senha(password),
            data_criacao=datetime.utcnow(),
            **kwargs,
        )
        self.sessao.add(modelo)
        self.sessao.commit()
        self.sessao.refresh(modelo)
        return _para_entidade(modelo)

    def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        modelo = self.sessao.query(UsuarioModelo).filter(UsuarioModelo.id == usuario.id).first()
        if not modelo:
            raise ValueError("Usuário não encontrado.")
        for chave, valor in dados.items():
            if valor is not None and hasattr(modelo, chave):
                setattr(modelo, chave, valor)
        self.sessao.commit()
        self.sessao.refresh(modelo)
        return _para_entidade(modelo)

    def autenticar(self, email: str, password: str) -> Usuario | None:
        modelo = (
            self.sessao.query(UsuarioModelo).filter(UsuarioModelo.email == email.lower()).first()
        )
        if not modelo or not senha_confere(password, modelo.senha_hash):
            return None
        return _para_entidade(modelo)
