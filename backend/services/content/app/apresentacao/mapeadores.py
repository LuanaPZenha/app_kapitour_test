from app.apresentacao.esquemas import PontoTuristicoResponse, RotaPontoResponse


def montar_pontos_da_rota(relacoes, ids_pontos, pontos) -> dict:
    mapa = {p.id: p for p in pontos}
    return {
        "relacionamentos": [RotaPontoResponse.model_validate(r) for r in relacoes],
        "pontos": [
            PontoTuristicoResponse.model_validate(mapa[pid])
            for pid in ids_pontos
            if pid in mapa
        ],
    }
