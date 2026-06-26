import { clienteHttp } from "./cliente-http";

export const apiCupons = {
  async buscarDisponiveis(parceiroId) {
    try {
      const params = parceiroId ? { parceiro_id: parceiroId } : {};
      const { data } = await clienteHttp.get("/cupons/disponiveis", { params });
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async buscarResgatados(usuarioId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/resgatados/${usuarioId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async verificarSeJaResgatado(cupomId, usuarioId) {
    try {
      const { data } = await clienteHttp.get("/cupons/verificar", {
        params: { cupom_id: cupomId, usuario_id: usuarioId },
      });
      return { success: true, jaResgatado: data.jaResgatado, data: data.jaResgatado ? {} : null };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async resgatar(cupomId, usuarioId, parceiroId) {
    try {
      const { data } = await clienteHttp.post("/cupons/resgatar", {
        cupom_id: cupomId,
        usuario_id: usuarioId,
        parceiro_id: parceiroId,
      });
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async listarCampanhasDoParceiro(parceiroId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/campanhas-parceiro/${parceiroId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async contarCuponsPorCampanha(parceiroId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/contagem-campanha/${parceiroId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },
};
