from datetime import date, datetime

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, engine
from app.models import (
    Campanha,
    Categoria,
    Cupom,
    Estoque,
    PontoCategoria,
    PontoTuristico,
    Produto,
    Rota,
    RotaPonto,
    TipoProduto,
    Usuario,
)


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


def _build_demo_users() -> list[Usuario]:
    return [
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000001",
            nome="Administrador",
            email="admin@kapitour.com",
            cpf="000.000.000-00",
            sexo="Masculino",
            data_nascimento=date(1990, 1, 1),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=1,
            senha_hash=hash_password("admin123"),
        ),
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000002",
            nome="Parceiro Demo",
            email="parceiro@kapitour.com",
            cpf="111.111.111-11",
            sexo="Feminino",
            data_nascimento=date(1988, 5, 10),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=2,
            senha_hash=hash_password("parceiro123"),
        ),
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000003",
            nome="Usuário Demo",
            email="user@kapitour.com",
            cpf="222.222.222-22",
            sexo="Masculino",
            data_nascimento=date(1995, 3, 15),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=3,
            senha_hash=hash_password("user123"),
        ),
    ]


def seed_demo_users(db: Session) -> None:
    existing_emails = {email for (email,) in db.query(Usuario.email).all()}
    demo_users = [user for user in _build_demo_users() if user.email not in existing_emails]
    if not demo_users:
        return
    db.add_all(demo_users)
    db.flush()


def seed_initial_data(db: Session) -> None:
    if db.query(Usuario).count() > 0:
        seed_demo_users(db)
        db.commit()
        return

    demo_users = _build_demo_users()
    admin, parceiro, comum = demo_users
    db.add_all(demo_users)
    db.flush()

    categorias = [
        Categoria(nome="Praia"),
        Categoria(nome="Histórico"),
        Categoria(nome="Gastronomia"),
        Categoria(nome="Natureza"),
    ]
    db.add_all(categorias)
    db.flush()

    pontos = [
        PontoTuristico(
            nome="Farol da Barra",
            descricao="Cartão-postal com vista panorâmica do mar.",
            latitude=-13.0105,
            longitude=-38.5325,
            url_img="https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            rua_numero="Av. Oceânica, 1",
        ),
        PontoTuristico(
            nome="Pelourinho",
            descricao="Centro histórico com arquitetura colonial.",
            latitude=-12.9714,
            longitude=-38.5014,
            url_img="https://images.unsplash.com/photo-1512453979798-5ea266f8880c",
            rua_numero="Praça José de Alencar",
        ),
        PontoTuristico(
            nome="Mercado Modelo",
            descricao="Artesanato local e gastronomia baiana.",
            latitude=-12.9698,
            longitude=-38.5129,
            url_img="https://images.unsplash.com/photo-1559339352-11d035aa65de",
            rua_numero="Praça Visconde de Cayru",
        ),
    ]
    db.add_all(pontos)
    db.flush()

    db.add_all(
        [
            PontoCategoria(ponto_id=pontos[0].id, categoria_id=categorias[0].id),
            PontoCategoria(ponto_id=pontos[1].id, categoria_id=categorias[1].id),
            PontoCategoria(ponto_id=pontos[2].id, categoria_id=categorias[2].id),
        ]
    )

    rotas = [
        Rota(nome="Rota Histórica", descricao="Principais pontos históricos da cidade."),
        Rota(nome="Rota Gastronômica", descricao="Sabores e mercados tradicionais."),
    ]
    db.add_all(rotas)
    db.flush()

    db.add_all(
        [
            RotaPonto(rota_id=rotas[0].id, ponto_id=pontos[1].id, ordem=1),
            RotaPonto(rota_id=rotas[0].id, ponto_id=pontos[0].id, ordem=2),
            RotaPonto(rota_id=rotas[1].id, ponto_id=pontos[2].id, ordem=1),
            RotaPonto(rota_id=rotas[1].id, ponto_id=pontos[1].id, ordem=2),
        ]
    )

    tipos = [TipoProduto(nome="Souvenir"), TipoProduto(nome="Vestuário")]
    db.add_all(tipos)
    db.flush()

    produtos = [
        Produto(
            nome="Camiseta Kapitour",
            descricao="Camiseta oficial do app.",
            valor_unid=59.9,
            tipo_id=tipos[1].id,
            imagem_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
        ),
        Produto(
            nome="Chaveiro Farol",
            descricao="Souvenir do Farol da Barra.",
            valor_unid=19.9,
            tipo_id=tipos[0].id,
            imagem_url="https://images.unsplash.com/photo-1513885535751-8b9238bd345a",
        ),
    ]
    db.add_all(produtos)
    db.flush()

    db.add_all(
        [
            Estoque(produto_id=produtos[0].id, quantidade=25),
            Estoque(produto_id=produtos[1].id, quantidade=100),
        ]
    )

    campanha = Campanha(
        nome="Verão Kapitour",
        descricao="Descontos especiais de verão.",
        data_inicio=date(2025, 1, 1),
        data_fim=date(2026, 12, 31),
        ativa=True,
        criada_em=datetime.utcnow(),
    )
    db.add(campanha)
    db.flush()

    db.add(
        Cupom(
            codigo="VERAO10",
            descricao="10% de desconto em parceiros selecionados.",
            criado_por=parceiro.id,
            parceiro_id=parceiro.id,
            data_validade=date(2026, 12, 31),
            data_criacao=datetime.utcnow(),
            quantidade_disponivel=50,
            campanha_id=campanha.id,
        )
    )

    db.commit()
