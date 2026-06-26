from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import Campanha, Cupom, Estoque, Produto, TipoProduto
from kapitour_shared.database import Base, engine


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


def seed_initial_data(db: Session) -> None:
    if db.query(Produto).count() > 0:
        return

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
            criado_por=2,
            parceiro_id=2,
            data_validade=date(2026, 12, 31),
            data_criacao=datetime.utcnow(),
            quantidade_disponivel=50,
            campanha_id=campanha.id,
        )
    )
    db.commit()
