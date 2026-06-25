"""Coordenadas verificadas dos pontos turísticos de Maricá (RJ)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoordenadaPonto:
    latitude: float
    longitude: float
    rua_numero: str | None = None


# Fontes: cadastro original (Supabase), OpenStreetMap/Nominatim e coordenadas oficiais
# do Farol (DHN/Marinha) e trilhas locais (Maricá Info / trilhando montanhas).
COORDENADAS_POR_NOME: dict[str, CoordenadaPonto] = {
    "Praia de Itaipuaçu": CoordenadaPonto(
        -22.969117,
        -42.97921,
        "Av. Benvindo Taques Horta Júnior, Itaipuaçu",
    ),
    "Mirante de Itaipuaçu": CoordenadaPonto(
        -22.962885,
        -43.021461,
        "Estrada Gilberto Carvalho, Recanto de Itaipuaçu",
    ),
    "Praia de Guaratiba": CoordenadaPonto(
        -22.9600557,
        -42.7995221,
        "Av. Alziro Rodrigues de Moura, Guaratiba",
    ),
    "Praia de Cordeirinho": CoordenadaPonto(
        -22.9573347,
        -42.7467818,
        "Av. Litorânea, Cordeirinho",
    ),
    "Praia de Ponta Negra": CoordenadaPonto(
        -22.9558128,
        -42.6984362,
        "Rua Carolino J. do Nascimento, Ponta Negra",
    ),
    "Praia de Jaconé": CoordenadaPonto(
        -22.9450876,
        -42.679963,
        "Av. A, Jaconé",
    ),
    "Praia da Sacristia": CoordenadaPonto(
        -22.9500204,
        -42.6826637,
        "Rua Sacristia, Ponta Negra",
    ),
    "Pedra do Elefante": CoordenadaPonto(
        -22.971886,
        -43.021122,
        "Estrada Gilberto Carvalho, Serra da Tiririca",
    ),
    "Pedra do Macaco": CoordenadaPonto(
        -22.9243547,
        -42.8958711,
        "Trilha da Pedra do Macaco, São José do Imbassaí",
    ),
    "Cachoeira do Espraiado": CoordenadaPonto(
        -22.8696365,
        -42.6899611,
        "Rodovia Ernani do Amaral Peixoto, Espraiado",
    ),
    "Cachoeira do Silvado": CoordenadaPonto(
        -22.8711612,
        -42.7372401,
        "Silvado, Maricá",
    ),
    "Gruta do Spar": CoordenadaPonto(
        -22.8907509,
        -42.9469322,
        "Trilha de acesso às Grutas do Spar, Inoã",
    ),
    "Gruta da Sacristia": CoordenadaPonto(
        -22.9511097,
        -42.6823289,
        "Praia da Sacristia, Ponta Negra",
    ),
    "Parque Estadual da Serra da Tiririca": CoordenadaPonto(
        -22.9731498,
        -43.0276923,
        "Serra da Tiririca, Itaipuaçu",
    ),
    "Túnel da Antiga Estrada de Ferro de Maricá": CoordenadaPonto(
        -22.900748,
        -42.9440426,
        "Antiga Estrada de Ferro, Inoã",
    ),
    "Igreja Matriz de Nossa Senhora do Amparo": CoordenadaPonto(
        -22.91942,
        -42.81855,
        "Rua Álvares de Castro, 239, Centro",
    ),
    "Capela de Santo Antônio": CoordenadaPonto(
        -22.8845091,
        -42.7039875,
        "Rua José Thomaz, Espraiado",
    ),
    "Capela de São Jorge": CoordenadaPonto(
        -22.8966963,
        -42.7097993,
        "Av. Central, Espraiado",
    ),
    "Capela Nossa Senhora da Saúde": CoordenadaPonto(
        -22.8527637,
        -42.780641,
        "Rodovia Vereador Oldemar Guedes Figueiredo, Caxito",
    ),
    "Farol de Ponta Negra": CoordenadaPonto(
        -22.9606556,
        -42.6926167,
        "Rua Beira do Canal, Ponta Negra",
    ),
    "Orla de Araçatiba": CoordenadaPonto(
        -22.9194686,
        -42.8272395,
        "Rua Álvares de Castro, Araçatiba",
    ),
    "Canal de Ponta Negra": CoordenadaPonto(
        -22.9563807,
        -42.693887,
        "Rua do Canal, Ponta Negra",
    ),
    "Complexo Lagunar": CoordenadaPonto(
        -22.9382439,
        -42.8496716,
        "Lagoa de Maricá",
    ),
    "Fazenda Itaocaia": CoordenadaPonto(
        -22.97115,
        -42.96845,
        "Itaocaia Valley, Itaipuaçu",
    ),
    "Caminho de Darwin (Trilha)": CoordenadaPonto(
        -22.9295691,
        -42.9806921,
        "Estrada da Barrinha, Itaocaia Valley",
    ),
    "Orla do Parque Nanci": CoordenadaPonto(
        -22.9202801,
        -42.8483561,
        "Parque Nanci",
    ),
    "Casa de Darcy Ribeiro": CoordenadaPonto(
        -22.9588,
        -42.7495,
        "Praia de Cordeirinho",
    ),
    "Praça Orlando de Barros Pimentel": CoordenadaPonto(
        -22.9197283,
        -42.8188837,
        "Centro de Maricá",
    ),
}

ALIASES_COORDENADAS: dict[str, str] = {
    "praia itaipuacu": "Praia de Itaipuaçu",
    "orla da lagoa de aracatiba": "Orla de Araçatiba",
    "lagoa de jaconé": "Complexo Lagunar",
    "lagoa de marica": "Complexo Lagunar",
}
