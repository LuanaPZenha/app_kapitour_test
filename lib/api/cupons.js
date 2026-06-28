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

  /** Turista: omita usuarioId (usa JWT). Empresa: informe o id do turista. */
  async buscarResgatados(usuarioId = null) {
    try {
      const url =
        usuarioId != null ? `/cupons/resgatados/${usuarioId}` : "/cupons/resgatados/me";
      const { data } = await clienteHttp.get(url);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  /** Turista: omita usuarioId. Empresa (QR): informe o id do turista escaneado. */
  async verificarSeJaResgatado(cupomId, usuarioId = null) {
    try {
      const params = { cupom_id: cupomId };
      if (usuarioId != null) {
        params.usuario_id = usuarioId;
      }
      const { data } = await clienteHttp.get("/cupons/verificar", { params });
      return { success: true, jaResgatado: data.jaResgatado, data: data.jaResgatado ? {} : null };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  /** Turista: resgatar(cupomId). Empresa: resgatar(cupomId, turistaId, parceiroId). */
  async resgatar(cupomId, usuarioId = null, parceiroId = null) {
    try {
      const payload = { cupom_id: cupomId };
      if (usuarioId != null) {
        payload.usuario_id = usuarioId;
      }
      if (parceiroId != null) {
        payload.parceiro_id = parceiroId;
      }
      const { data } = await clienteHttp.post("/cupons/resgatar", payload);
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
