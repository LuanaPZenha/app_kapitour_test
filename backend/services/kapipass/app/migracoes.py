import time

from sqlalchemy.orm import Session

from app.modelos import (
    Colecao,
    ColecaoPonto,
    Conquista,
    EcoAtividade,
    KapiPassCarimbo,
    KapiPassNivel,
    Missao,
    Tesouro,
)
from kapitour_shared.banco_dados import BaseModelo, motor_banco
from kapitour_shared.clientes_http import ClienteConteudo


def executar_migracoes() -> None:
    BaseModelo.metadata.create_all(bind=motor_banco)


def _montar_niveis() -> list[KapiPassNivel]:
    return [
        KapiPassNivel(nome="Turista Iniciante", xp_minimo=0, ordem=1),
        KapiPassNivel(nome="Explorador Local", xp_minimo=250, ordem=2),
        KapiPassNivel(nome="Aventureiro", xp_minimo=750, ordem=3),
        KapiPassNivel(nome="Mestre dos Caminhos", xp_minimo=1500, ordem=4),
        KapiPassNivel(nome="Lenda Kapitour", xp_minimo=3000, ordem=5),
    ]


def _montar_conquistas() -> list[Conquista]:
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


def _semear_colecoes(sessao: Session, pontos: list[dict]) -> None:
    if sessao.query(Colecao).count() > 0:
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
        sessao.add(colecao)
        sessao.flush()
        for ponto_id in _pontos_por_palavras(pontos, palavras):
            sessao.add(ColecaoPonto(colecao_id=colecao.id, ponto_turistico_id=ponto_id))
    sessao.flush()


def _semear_missoes(sessao: Session) -> None:
    if sessao.query(Missao).count() > 0:
        return
    sessao.add_all(
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
    sessao.flush()


def _semear_eco_atividades(sessao: Session) -> None:
    if sessao.query(EcoAtividade).count() > 0:
        return
    sessao.add_all(
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
    sessao.flush()


def _semear_tesouros(sessao: Session, pontos: list[dict]) -> None:
    if sessao.query(Tesouro).count() > 0:
        return
    ids_pedra = _pontos_por_palavras(pontos, ["pedra", "elefante", "itaocaia"])
    ids_centro = _pontos_por_palavras(pontos, ["centro", "igreja", "histór"])
    sessao.add_all(
        [
            Tesouro(
                nome="O Guardião de Pedra",
                descricao="Um tesouro escondido nas alturas de Maricá.",
                pista="Procure onde a pedra tem forma de um grande animal.",
                enigma="Sou grande, sou cinza, e pareço ter tromba. Que pedra sou eu?",
                ponto_turistico_id=ids_pedra[0] if ids_pedra else None,
                carimbo_id=None,
                conquista_id=None,
                xp_bonus=300,
            ),
            Tesouro(
                nome="Segredos do Centro",
                descricao="A história de Maricá guarda um enigma.",
                pista="Onde os sinos tocam e a fé se reúne.",
                enigma="Tenho torre, tenho sino, e sou o coração da fé local.",
                ponto_turistico_id=ids_centro[0] if ids_centro else None,
                carimbo_id=None,
                conquista_id=None,
                xp_bonus=250,
            ),
        ]
    )
    sessao.flush()


def semear_kapipass(sessao: Session, pontos: list[dict]) -> None:
    if sessao.query(KapiPassNivel).count() == 0:
        sessao.add_all(_montar_niveis())
        sessao.flush()

    codigos_existentes = {codigo for (codigo,) in sessao.query(Conquista.codigo).all()}
    novas_conquistas = [c for c in _montar_conquistas() if c.codigo not in codigos_existentes]
    if novas_conquistas:
        sessao.add_all(novas_conquistas)
        sessao.flush()

    pontos_com_carimbo = {pid for (pid,) in sessao.query(KapiPassCarimbo.ponto_turistico_id).all()}
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
        sessao.add_all(novos_carimbos)
        sessao.flush()

    _semear_colecoes(sessao, pontos)
    _semear_missoes(sessao)
    _semear_eco_atividades(sessao)
    _semear_tesouros(sessao, pontos)


def semear_dados_iniciais(sessao: Session) -> None:
    conteudo = ClienteConteudo()
    pontos: list[dict] = []
    for tentativa in range(10):
        try:
            pontos = conteudo.listar_pontos_turisticos()
            if pontos:
                break
        except Exception:
            pass
        time.sleep(1)

    semear_kapipass(sessao, pontos)
    sessao.commit()
