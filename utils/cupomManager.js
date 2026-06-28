import { cuponsApi, dbApi } from '../lib/api';

export const buscarCuponsDisponiveis = async (parceiroId) => {
  return cuponsApi.buscarDisponiveis(parceiroId);
};

export const buscarCuponsResgatados = async (usuarioId = null) => {
  return cuponsApi.buscarResgatados(usuarioId);
};

export const buscarHistoricoResgates = async (usuarioId = null) => {
  return cuponsApi.buscarResgatados(usuarioId);
};

export const verificarCupomResgatado = async (cupomId, usuarioId = null) => {
  return cuponsApi.verificarResgatado(cupomId, usuarioId);
};

export const verificarResgatePorCampanha = async (campanhaId, usuarioId = null) => {
  const resgatados = await cuponsApi.buscarResgatados(usuarioId);
  if (!resgatados.success) return resgatados;
  const jaResgatou = (resgatados.data || []).some(
    (item) => item.campanha_id === campanhaId || item.campanhaId === campanhaId
  );
  return { success: true, jaResgatou };
};

export const resgatarCupom = async (cupomId, usuarioId = null, parceiroId = null) => {
  return cuponsApi.resgatar(cupomId, usuarioId, parceiroId);
};

export const buscarCampanhasParceiro = async (parceiroUsuarioId) => {
  return cuponsApi.campanhasParceiro(parceiroUsuarioId);
};

export const contarCuponsCampanha = async (parceiroUsuarioId) => {
  return cuponsApi.contagemCampanha(parceiroUsuarioId);
};
