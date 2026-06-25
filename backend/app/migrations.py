from datetime import date, datetime

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, engine
from app.models import (
    Campanha,
    Categoria,
    Colecao,
    ColecaoPonto,
    Conquista,
    Cupom,
    EcoAtividade,
    Estoque,
    KapiPassCarimbo,
    KapiPassNivel,
    Missao,
    PontoCategoria,
    PontoTuristico,
    Produto,
    Rota,
    RotaPonto,
    Tesouro,
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


def _build_niveis() -> list[KapiPassNivel]:
    return [
        KapiPassNivel(nome="Turista Iniciante", xp_minimo=0, ordem=1),
        KapiPassNivel(nome="Explorador Local", xp_minimo=250, ordem=2),
        KapiPassNivel(nome="Aventureiro", xp_minimo=750, ordem=3),
        KapiPassNivel(nome="Mestre dos Caminhos", xp_minimo=1500, ordem=4),
        KapiPassNivel(nome="Lenda Kapitour", xp_minimo=3000, ordem=5),
    ]


def _build_conquistas() -> list[Conquista]:
    return [
        Conquista(
            codigo="explorador_marica",
            nome="Explorador de Maricá",
            descricao="Faça seu primeiro check-in em um ponto turístico.",
            icone="compass-outline",
            xp_bonus=50,
        ),
        Conquista(
            codigo="cacador_historias",
            nome="Caçador de Histórias",
            descricao="Visite 3 pontos turísticos diferentes.",
            icone="book-outline",
            xp_bonus=100,
        ),
        Conquista(
            codigo="fotografo_urbano",
            nome="Fotógrafo Urbano",
            descricao="Visite 5 pontos turísticos diferentes.",
            icone="camera-outline",
            xp_bonus=150,
        ),
        Conquista(
            codigo="guardiao_natureza",
            nome="Guardião da Natureza",
            descricao="Visite 8 pontos turísticos diferentes.",
            icone="leaf-outline",
            xp_bonus=200,
        ),
        Conquista(
            codigo="colecionador_carimbos",
            nome="Colecionador de Carimbos",
            descricao="Colete 5 carimbos digitais.",
            icone="ribbon-outline",
            xp_bonus=250,
        ),
    ]


def seed_kapipass(db: Session) -> None:
    """Seeds idempotentes do KapiPass: níveis, conquistas e 1 carimbo por ponto."""
    if db.query(KapiPassNivel).count() == 0:
        db.add_all(_build_niveis())
        db.flush()

    existing_codigos = {codigo for (codigo,) in db.query(Conquista.codigo).all()}
    novas_conquistas = [c for c in _build_conquistas() if c.codigo not in existing_codigos]
    if novas_conquistas:
        db.add_all(novas_conquistas)
        db.flush()

    pontos_com_carimbo = {
        pid for (pid,) in db.query(KapiPassCarimbo.ponto_turistico_id).all()
    }
    novos_carimbos = []
    for ponto in db.query(PontoTuristico).all():
        if ponto.id in pontos_com_carimbo:
            continue
        novos_carimbos.append(
            KapiPassCarimbo(
                ponto_turistico_id=ponto.id,
                nome=f"Carimbo · {ponto.nome}",
                descricao=f"Carimbo conquistado ao visitar {ponto.nome}.",
                imagem=ponto.url_img,
                raridade="comum",
                xp_recompensa=50,
            )
        )
    if novos_carimbos:
        db.add_all(novos_carimbos)
        db.flush()

    _seed_colecoes(db)
    _seed_missoes(db)
    _seed_eco_atividades(db)
    _seed_tesouros(db)


def _pontos_por_palavras(db: Session, palavras: list[str]) -> list[int]:
    ids: list[int] = []
    for palavra in palavras:
        for ponto in (
            db.query(PontoTuristico).filter(PontoTuristico.nome.ilike(f"%{palavra}%")).all()
        ):
            if ponto.id not in ids:
                ids.append(ponto.id)
    return ids


def _seed_colecoes(db: Session) -> None:
    if db.query(Colecao).count() > 0:
        return
    definicoes = [
        (
            "Praias de Maricá",
            "As praias mais famosas da cidade.",
            ["praia", "itaipua", "cordeirinho", "ponta negra"],
        ),
        (
            "Maricá Histórica",
            "Patrimônio histórico e cultural de Maricá.",
            ["igreja", "centro", "fazenda", "histór", "matriz"],
        ),
        (
            "Trilhas e Aventuras",
            "Trilhas, pedras e mirantes para aventureiros.",
            ["pedra", "trilha", "mirante", "elefante", "itaocaia", "serra"],
        ),
    ]
    for nome, descricao, palavras in definicoes:
        colecao = Colecao(nome=nome, descricao=descricao, imagem=None)
        db.add(colecao)
        db.flush()
        for ponto_id in _pontos_por_palavras(db, palavras):
            db.add(ColecaoPonto(colecao_id=colecao.id, ponto_turistico_id=ponto_id))
    db.flush()


def _seed_missoes(db: Session) -> None:
    if db.query(Missao).count() > 0:
        return
    db.add_all(
        [
            Missao(
                nome="Primeiro Passo",
                descricao="Faça seu primeiro check-in em qualquer ponto turístico.",
                tipo="explorar",
                objetivo_quantidade=1,
                xp=50,
                recompensa="50 XP",
                dias_validade=None,
                ativo=True,
            ),
            Missao(
                nome="Explorador de Maricá",
                descricao="Visite 3 pontos turísticos diferentes.",
                tipo="explorar",
                objetivo_quantidade=3,
                xp=100,
                recompensa="100 XP",
                dias_validade=30,
                ativo=True,
            ),
            Missao(
                nome="Colecionador",
                descricao="Colete 5 carimbos digitais.",
                tipo="carimbos",
                objetivo_quantidade=5,
                xp=150,
                recompensa="150 XP",
                dias_validade=None,
                ativo=True,
            ),
            Missao(
                nome="Aventureiro",
                descricao="Visite 8 pontos turísticos diferentes.",
                tipo="explorar",
                objetivo_quantidade=8,
                xp=200,
                recompensa="200 XP",
                dias_validade=None,
                ativo=True,
            ),
        ]
    )
    db.flush()


def _seed_eco_atividades(db: Session) -> None:
    if db.query(EcoAtividade).count() > 0:
        return
    db.add_all(
        [
            EcoAtividade(
                nome="Trilha Ecológica",
                descricao="Participe de uma trilha ecológica guiada.",
                tipo="trilha",
                pontuacao_eco=30,
                xp_recompensa=40,
            ),
            EcoAtividade(
                nome="Limpeza de Praia",
                descricao="Ajude em um mutirão de limpeza de praia.",
                tipo="acao",
                pontuacao_eco=50,
                xp_recompensa=60,
            ),
            EcoAtividade(
                nome="Evento Ambiental",
                descricao="Participe de um evento de educação ambiental.",
                tipo="evento",
                pontuacao_eco=40,
                xp_recompensa=50,
            ),
            EcoAtividade(
                nome="Plantio de Mudas",
                descricao="Contribua com o plantio de mudas nativas.",
                tipo="acao",
                pontuacao_eco=35,
                xp_recompensa=45,
            ),
        ]
    )
    db.flush()


def _seed_tesouros(db: Session) -> None:
    if db.query(Tesouro).count() > 0:
        return
    pedra_ids = _pontos_por_palavras(db, ["pedra", "elefante", "itaocaia"])
    centro_ids = _pontos_por_palavras(db, ["centro", "igreja", "histór"])
    db.add_all(
        [
            Tesouro(
                nome="O Guardião de Pedra",
                descricao="Um tesouro escondido nas alturas de Maricá.",
                pista="Procure onde a pedra tem forma de um grande animal.",
                enigma="Sou grande, sou cinza, e pareço ter tromba. Que pedra sou eu?",
                ponto_turistico_id=pedra_ids[0] if pedra_ids else None,
                carimbo_id=None,
                conquista_id=None,
                xp_bonus=300,
            ),
            Tesouro(
                nome="Segredos do Centro",
                descricao="A história de Maricá guarda um enigma.",
                pista="Onde os sinos tocam e a fé se reúne.",
                enigma="Tenho torre, tenho sino, e sou o coração da fé local.",
                ponto_turistico_id=centro_ids[0] if centro_ids else None,
                carimbo_id=None,
                conquista_id=None,
                xp_bonus=250,
            ),
        ]
    )
    db.flush()


def seed_initial_data(db: Session) -> None:
    if db.query(Usuario).count() > 0:
        seed_demo_users(db)
        seed_kapipass(db)
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

    seed_kapipass(db)
    db.commit()
