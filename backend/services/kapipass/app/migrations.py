import time

from sqlalchemy.orm import Session

from app.models import (
    Colecao,
    ColecaoPonto,
    Conquista,
    EcoAtividade,
    KapiPassCarimbo,
    KapiPassNivel,
    Missao,
    Tesouro,
)
from kapitour_shared.clients import ContentClient
from kapitour_shared.database import Base, engine


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


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


def _pontos_por_palavras(pontos: list[dict], palavras: list[str]) -> list[int]:
    ids: list[int] = []
    for palavra in palavras:
        for ponto in pontos:
            if palavra.lower() in ponto["nome"].lower() and ponto["id"] not in ids:
                ids.append(ponto["id"])
    return ids


def _seed_colecoes(db: Session, pontos: list[dict]) -> None:
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
        for ponto_id in _pontos_por_palavras(pontos, palavras):
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


def _seed_tesouros(db: Session, pontos: list[dict]) -> None:
    if db.query(Tesouro).count() > 0:
        return
    pedra_ids = _pontos_por_palavras(pontos, ["pedra", "elefante", "itaocaia"])
    centro_ids = _pontos_por_palavras(pontos, ["centro", "igreja", "histór"])
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


def seed_kapipass(db: Session, pontos: list[dict]) -> None:
    if db.query(KapiPassNivel).count() == 0:
        db.add_all(_build_niveis())
        db.flush()

    existing_codigos = {codigo for (codigo,) in db.query(Conquista.codigo).all()}
    novas_conquistas = [c for c in _build_conquistas() if c.codigo not in existing_codigos]
    if novas_conquistas:
        db.add_all(novas_conquistas)
        db.flush()

    pontos_com_carimbo = {pid for (pid,) in db.query(KapiPassCarimbo.ponto_turistico_id).all()}
    novos_carimbos = []
    for ponto in pontos:
        if ponto["id"] in pontos_com_carimbo:
            continue
        novos_carimbos.append(
            KapiPassCarimbo(
                ponto_turistico_id=ponto["id"],
                nome=f"Carimbo · {ponto['nome']}",
                descricao=f"Carimbo conquistado ao visitar {ponto['nome']}.",
                imagem=ponto.get("url_img"),
                raridade="comum",
                xp_recompensa=50,
            )
        )
    if novos_carimbos:
        db.add_all(novos_carimbos)
        db.flush()

    _seed_colecoes(db, pontos)
    _seed_missoes(db)
    _seed_eco_atividades(db)
    _seed_tesouros(db, pontos)


def seed_initial_data(db: Session) -> None:
    content = ContentClient()
    pontos: list[dict] = []
    for attempt in range(10):
        try:
            pontos = content.list_pontos()
            if pontos:
                break
        except Exception:
            pass
        time.sleep(1)

    seed_kapipass(db, pontos)
    db.commit()
