"""Atualiza pontos turísticos de Maricá: remove imagens e aplica catálogo curado."""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import Categoria, PontoCategoria, PontoTuristico
from scripts.seed_pontos_coordenadas import seed_coordenadas


@dataclass
class PontoCatalogo:
    nome: str
    descricao: str
    categorias: list[int]
    latitude: float
    longitude: float
    rua_numero: str | None = None
    aliases: tuple[str, ...] = ()


PONTOS_MARICA: list[PontoCatalogo] = [
    PontoCatalogo(
        nome="Praia de Itaipuaçu",
        descricao=(
            "Uma das maiores e mais famosas da cidade. Possui águas agitadas, areia de granulação grossa "
            "e uma vista deslumbrante para a Pedra do Elefante. O calçadão é excelente para caminhadas "
            "e passeios de bicicleta."
        ),
        categorias=[1],
        latitude=-22.969117,
        longitude=-42.97921,
        rua_numero="Orla de Itaipuaçu",
        aliases=("praia itaipuacu", "itaipuacu"),
    ),
    PontoCatalogo(
        nome="Praia de Ponta Negra",
        descricao=(
            "Muito procurada por surfistas devido às boas ondas. O bairro tem um clima de vila de pescadores "
            "e é cortado por um canal charmoso que liga a lagoa ao mar."
        ),
        categorias=[1],
        latitude=-22.955813,
        longitude=-42.698436,
        rua_numero="Av. Beira Mar",
        aliases=("ponta negra",),
    ),
    PontoCatalogo(
        nome="Praia de Cordeirinho",
        descricao=(
            "Uma opção mais tranquila e residencial, ideal para quem busca fugir do agito. "
            "A areia também é mais grossa e o mar costuma ser forte."
        ),
        categorias=[1],
        latitude=-22.957335,
        longitude=-42.746782,
        rua_numero="Av. Maysa",
        aliases=("cordeirinho",),
    ),
    PontoCatalogo(
        nome="Praia de Guaratiba",
        descricao=(
            "Extensão natural de Cordeirinho, compartilha das mesmas características de tranquilidade "
            "e natureza preservada."
        ),
        categorias=[1],
        latitude=-22.960056,
        longitude=-42.799522,
        rua_numero="Av. Maysa",
        aliases=("guaratiba",),
    ),
    PontoCatalogo(
        nome="Praia da Sacristia",
        descricao=(
            "Um verdadeiro refúgio escondido entre as pedras, próximo a Ponta Negra. "
            "É uma praia muito pequena, com piscinas naturais formadas pelas rochas, "
            "ideal para quem gosta de natureza rústica."
        ),
        categorias=[1],
        latitude=-22.95002,
        longitude=-42.682664,
        rua_numero="Av. Maysa",
        aliases=("sacristia",),
    ),
    PontoCatalogo(
        nome="Orla de Araçatiba",
        descricao=(
            "O ponto de encontro queridinho dos moradores e turistas. Possui excelente infraestrutura "
            "com calçadão, ciclovia, praças e decks. É o melhor lugar da cidade para assistir ao pôr do sol."
        ),
        categorias=[5],
        latitude=-22.919469,
        longitude=-42.827239,
        rua_numero="Rua Alvares de Castro",
        aliases=("orla da lagoa de aracatiba", "aracatiba"),
    ),
    PontoCatalogo(
        nome="Orla do Parque Nanci",
        descricao=(
            "Uma área recentemente revitalizada às margens da lagoa. Conta com paisagismo, "
            "áreas de lazer para crianças, quadras de areia e um ambiente muito familiar."
        ),
        categorias=[5, 2],
        latitude=-22.9362,
        longitude=-42.8418,
        rua_numero="Parque Nanci",
        aliases=("parque nanci",),
    ),
    PontoCatalogo(
        nome="Complexo Lagunar",
        descricao=(
            "Imenso sistema de lagoas que banha grande parte da cidade — Lagoas de Maricá, Barra, "
            "Guarapina e Padre. São ótimas para a prática de esportes náuticos (stand-up paddle e caiaque) "
            "e pesca artesanal."
        ),
        categorias=[5],
        latitude=-22.9215,
        longitude=-42.8185,
        rua_numero="Região das Lagoas",
        aliases=("lagoa de marica", "lagoa de jaconé", "complexo lagunar"),
    ),
    PontoCatalogo(
        nome="Canal de Ponta Negra",
        descricao=(
            "Ligação artificial entre o sistema lagunar e o oceano. As margens do canal são ótimas "
            "para caminhadas, e as águas ali costumam ser mais calmas e próprias para banho em dias de maré favorável."
        ),
        categorias=[5],
        latitude=-22.956381,
        longitude=-42.693887,
        rua_numero="Rua do Canal",
        aliases=("canal ponta negra",),
    ),
    PontoCatalogo(
        nome="Pedra do Elefante",
        descricao=(
            "No Parque Estadual da Serra da Tiririca, na divisa entre Maricá e Niterói. "
            "A trilha é considerada de nível moderado a pesado, mas recompensa os aventureiros "
            "com uma vista panorâmica espetacular da costa oceânica."
        ),
        categorias=[7],
        latitude=-22.974438,
        longitude=-43.017236,
        rua_numero="Serra da Tiririca",
        aliases=("pedra do elefante", "serra da tiririca"),
    ),
    PontoCatalogo(
        nome="Farol de Ponta Negra",
        descricao=(
            "Localizado no alto do promontório em Ponta Negra, oferece uma das vistas mais bonitas da cidade, "
            "englobando toda a restinga e a faixa de areia até Itaipuaçu."
        ),
        categorias=[2],
        latitude=-22.960387,
        longitude=-42.692821,
        rua_numero="Rua Beira do Canal",
        aliases=("farol ponta negra",),
    ),
    PontoCatalogo(
        nome="Cachoeira do Espraiado",
        descricao=(
            "Situada na área rural de Maricá, é um ponto perfeito para quem busca contato com a Mata Atlântica, "
            "águas geladas e tranquilidade. A região do Espraiado também conta com ótima gastronomia local."
        ),
        categorias=[6],
        latitude=-22.869636,
        longitude=-42.689961,
        rua_numero="Estrada do Espraiado",
        aliases=("espraiado",),
    ),
    PontoCatalogo(
        nome="Pedra do Macaco",
        descricao=(
            "Localizada no bairro de São José do Imbassaí. A trilha é curta, embora íngreme, "
            "e o topo oferece um visual incrível de todo o complexo lagunar e da restinga de Maricá."
        ),
        categorias=[7],
        latitude=-22.924355,
        longitude=-42.895871,
        rua_numero="São José do Imbassaí",
        aliases=("pedra do macaco",),
    ),
    PontoCatalogo(
        nome="Gruta do Spar",
        descricao=(
            "Conjunto de galerias e cavernas artificiais criadas por antigas minerações de pedras. "
            "Hoje, com a natureza tomando conta, é um cenário belíssimo e muito procurado "
            "por praticantes de rapel e ecoturismo."
        ),
        categorias=[7],
        latitude=-22.890751,
        longitude=-42.946932,
        rua_numero="Av. Gilberto Carvalho",
        aliases=("gruta spar",),
    ),
    PontoCatalogo(
        nome="Igreja Matriz de Nossa Senhora do Amparo",
        descricao=(
            "Localizada no centro da cidade, é um marco histórico cujas origens remontam ao século XVIII. "
            "A arquitetura preserva a memória da fundação do município."
        ),
        categorias=[3, 8],
        latitude=-22.912912,
        longitude=-42.817104,
        rua_numero="Rua Alvares de Castro",
        aliases=("igreja matriz", "nossa senhora do amparo"),
    ),
    PontoCatalogo(
        nome="Casa de Darcy Ribeiro",
        descricao=(
            "Localizada na Praia de Cordeirinho, esta casa de formato peculiar foi projetada pelo renomado "
            "arquiteto Oscar Niemeyer para o antropólogo e político Darcy Ribeiro, que viveu ali seus últimos anos."
        ),
        categorias=[8],
        latitude=-22.9588,
        longitude=-42.7495,
        rua_numero="Praia de Cordeirinho",
        aliases=("darcy ribeiro", "niemeyer"),
    ),
    PontoCatalogo(
        nome="Fazenda Itaocaia",
        descricao=(
            "Construção histórica em Itaipuaçu, famosa por ter hospedado o naturalista Charles Darwin em 1832 "
            "durante sua expedição pelo Brasil. A região ao redor mantém um charme colonial."
        ),
        categorias=[8],
        latitude=-22.9712,
        longitude=-42.9685,
        rua_numero="Itaipuaçu",
        aliases=("itaocaia", "darwin"),
    ),
    PontoCatalogo(
        nome="Praça Orlando de Barros Pimentel",
        descricao=(
            "A praça principal do Centro de Maricá. É o coração comercial e cultural da cidade, "
            "cercada por prédios históricos, bares e onde acontecem diversos eventos locais."
        ),
        categorias=[8],
        latitude=-22.9186,
        longitude=-42.8179,
        rua_numero="Centro de Maricá",
        aliases=("orlando de barros pimentel", "praca orlando"),
    ),
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def matches(ponto: PontoTuristico, catalogo: PontoCatalogo) -> bool:
    nome = normalize(ponto.nome)
    alvos = {normalize(catalogo.nome), *(normalize(alias) for alias in catalogo.aliases)}
    if nome in alvos:
        return True
    return any(alvo in nome or nome in alvo for alvo in alvos if len(alvo) >= 8)


def sync_categorias(db, ponto_id: int, categoria_ids: list[int]) -> None:
    db.query(PontoCategoria).filter(PontoCategoria.ponto_id == ponto_id).delete()
    for categoria_id in categoria_ids:
        exists = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        if exists:
            db.add(PontoCategoria(ponto_id=ponto_id, categoria_id=categoria_id))


def apply_updates() -> dict[str, int]:
    db = SessionLocal()
    stats = {"imagens_removidas": 0, "atualizados": 0, "criados": 0}

    try:
        existentes = db.query(PontoTuristico).all()
        for ponto in existentes:
            if ponto.url_img:
                stats["imagens_removidas"] += 1
            ponto.url_img = None

        usados: set[int] = set()

        for catalogo in PONTOS_MARICA:
            ponto = next(
                (p for p in existentes if p.id not in usados and matches(p, catalogo)),
                None,
            )

            if ponto:
                usados.add(ponto.id)
                ponto.nome = catalogo.nome
                ponto.descricao = catalogo.descricao
                ponto.latitude = catalogo.latitude
                ponto.longitude = catalogo.longitude
                ponto.rua_numero = catalogo.rua_numero
                ponto.url_img = None
                sync_categorias(db, ponto.id, catalogo.categorias)
                stats["atualizados"] += 1
            else:
                novo = PontoTuristico(
                    nome=catalogo.nome,
                    descricao=catalogo.descricao,
                    latitude=catalogo.latitude,
                    longitude=catalogo.longitude,
                    rua_numero=catalogo.rua_numero,
                    url_img=None,
                )
                db.add(novo)
                db.flush()
                usados.add(novo.id)
                sync_categorias(db, novo.id, catalogo.categorias)
                stats["criados"] += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    coord_stats = seed_coordenadas(force=True)
    stats["total_pontos"] = coord_stats["total"]
    stats["coordenadas_atualizadas"] = coord_stats["atualizados"]
    stats["sem_coordenada"] = coord_stats["sem_coordenada"]
    return stats


def main() -> None:
    stats = apply_updates()
    print("Pontos atualizados:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
