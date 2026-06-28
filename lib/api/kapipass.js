import { clienteHttp } from "./cliente-http";
import { respostaComErro, respostaComSucesso } from "./respostas";

export const apiKapiPass = {
  async obterPassaporte() {
    try {
      const { data } = await clienteHttp.get("/kapipass/me");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarNiveis() {
    try {
      const { data } = await clienteHttp.get("/kapipass/niveis");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async registrarCheckin(pontoTuristicoId, latitude = null, longitude = null) {
    try {
      const { data } = await clienteHttp.post("/kapipass/checkin", {
        ponto_turistico_id: pontoTuristicoId,
        latitude,
        longitude,
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCheckins() {
    try {
      const { data } = await clienteHttp.get("/kapipass/checkins");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCarimbos() {
    try {
      const { data } = await clienteHttp.get("/kapipass/carimbos");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarConquistas() {
    try {
      const { data } = await clienteHttp.get("/kapipass/conquistas");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarColecoes() {
    try {
      const { data } = await clienteHttp.get("/kapipass/colecoes");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarMissoes() {
    try {
      const { data } = await clienteHttp.get("/kapipass/missoes");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async aceitarMissao(missaoId) {
    try {
      const { data } = await clienteHttp.post(`/kapipass/missoes/${missaoId}/aceitar`, {});
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarAtividadesEco() {
    try {
      const { data } = await clienteHttp.get("/kapipass/eco");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async registrarAtividadeEco(ecoAtividadeId) {
    try {
      const { data } = await clienteHttp.post("/kapipass/eco/registrar", {
        eco_atividade_id: ecoAtividadeId,
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarDiario() {
    try {
      const { data } = await clienteHttp.get("/kapipass/diario");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarTesouros() {
    try {
      const { data } = await clienteHttp.get("/kapipass/tesouros");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async concluirTesouro(tesouroId) {
    try {
      const { data } = await clienteHttp.post(`/kapipass/tesouros/${tesouroId}/concluir`, {});
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarRankings(categoria = "exploradores", pagina = 1, tamanho = 20) {
    try {
      const { data } = await clienteHttp.get("/kapipass/rankings", {
        params: { categoria, page: pagina, size: tamanho },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },
};
