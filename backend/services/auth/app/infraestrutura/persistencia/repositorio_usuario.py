from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.dominio.entidades.usuario import Usuario
from app.infraestrutura.persistencia.modelos import TokenOperacaoModelo, UsuarioModelo
from kapitour_shared.security.passwords import gerar_hash_senha, precisa_rehash, senha_confere


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
        email_verificado=modelo.email_verificado,
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
            email_verificado=kwargs.pop("email_verificado", False),
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

    def atualizar_senha(self, auth_id: str, nova_senha: str) -> Usuario | None:
        modelo = self.sessao.query(UsuarioModelo).filter(UsuarioModelo.auth_id == auth_id).first()
        if not modelo:
            return None
        modelo.senha_hash = gerar_hash_senha(nova_senha)
        self.sessao.commit()
        self.sessao.refresh(modelo)
        return _para_entidade(modelo)

    def marcar_email_verificado(self, auth_id: str) -> Usuario | None:
        usuario = self.buscar_por_auth_id(auth_id)
        if not usuario:
            return None
        return self.atualizar(usuario, {"email_verificado": True})

    def autenticar(self, email: str, password: str) -> Usuario | None:
        modelo = (
            self.sessao.query(UsuarioModelo).filter(UsuarioModelo.email == email.lower()).first()
        )
        if not modelo or not senha_confere(password, modelo.senha_hash):
            return None
        if precisa_rehash(modelo.senha_hash):
            modelo.senha_hash = gerar_hash_senha(password)
            self.sessao.commit()
        return _para_entidade(modelo)

    def criar_token_operacao(
        self, auth_id: str, tipo: str, horas_validade: int = 24
    ) -> str:
        token = str(uuid4())
        registro = TokenOperacaoModelo(
            token=token,
            auth_id=auth_id,
            tipo=tipo,
            expira_em=datetime.utcnow() + timedelta(hours=horas_validade),
        )
        self.sessao.add(registro)
        self.sessao.commit()
        return token

    def consumir_token_operacao(self, token: str, tipo: str) -> str | None:
        registro = (
            self.sessao.query(TokenOperacaoModelo)
            .filter(
                TokenOperacaoModelo.token == token,
                TokenOperacaoModelo.tipo == tipo,
                TokenOperacaoModelo.usado.is_(False),
                TokenOperacaoModelo.expira_em > datetime.utcnow(),
            )
            .first()
        )
        if not registro:
            return None
        registro.usado = True
        self.sessao.commit()
        return registro.auth_id
