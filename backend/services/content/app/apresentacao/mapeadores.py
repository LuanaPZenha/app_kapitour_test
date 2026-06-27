from app.apresentacao.esquemas import (
    CategoriaResponse,
    PontoTuristicoResponse,
    RotaPontoResponse,
    RotaResponse,
)


def mapear_categorias(categorias) -> list[CategoriaResponse]:
    return [CategoriaResponse.model_validate(item) for item in categorias]


def mapear_pontos(pontos) -> list[PontoTuristicoResponse]:
    return [PontoTuristicoResponse.model_validate(item) for item in pontos]


def mapear_ponto(ponto) -> PontoTuristicoResponse | None:
    if not ponto:
        return None
    return PontoTuristicoResponse.model_validate(ponto)


def mapear_rotas(rotas) -> list[RotaResponse]:
    return [RotaResponse.model_validate(item) for item in rotas]


def mapear_rotas_ponto(relacoes) -> list[RotaPontoResponse]:
    return [RotaPontoResponse.model_validate(item) for item in relacoes]


def montar_pontos_da_rota(relacoes, ids_pontos, pontos) -> dict:
    mapa = {p.id: p for p in pontos}
    return {
        "relacionamentos": mapear_rotas_ponto(relacoes),
        "pontos": [
            PontoTuristicoResponse.model_validate(mapa[pid])
            for pid in ids_pontos
            if pid in mapa
        ],
    }
