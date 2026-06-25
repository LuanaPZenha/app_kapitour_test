import { cuponsApi, dbApi } from '../lib/api';

export const buscarCuponsDisponiveis = async (parceiroId) => {
  return cuponsApi.buscarDisponiveis(parceiroId);
};

export const buscarCuponsResgatados = async (usuarioId) => {
  return cuponsApi.buscarResgatados(usuarioId);
};

export const buscarHistoricoResgates = async (usuarioId) => {
  return cuponsApi.buscarResgatados(usuarioId);
};

export const verificarCupomResgatado = async (cupomId, usuarioId) => {
  return cuponsApi.verificarResgatado(cupomId, usuarioId);
};

export const verificarResgatePorCampanha = async (campanhaId, usuarioId) => {
  const resgatados = await cuponsApi.buscarResgatados(usuarioId);
  if (!resgatados.success) return resgatados;
  const jaResgatou = (resgatados.data || []).some(
    (item) => item.cupom?.campanha_id === campanhaId
  );
  return { success: true, jaResgatouCampanha: jaResgatou };
};

export const resgatarCupom = async (cupomId, usuarioId, parceiroId) => {
  return cuponsApi.resgatar(cupomId, usuarioId, parceiroId);
};

export const buscarCampanhasDoParceiro = async (parceiroUsuarioId) => {
  return cuponsApi.campanhasParceiro(parceiroUsuarioId);
};

export const buscarContagemCuponsPorCampanha = async (parceiroUsuarioId) => {
  return cuponsApi.contagemCampanha(parceiroUsuarioId);
};

export const atualizarUsuario = async (authId, payload) => {
  const { data, error } = await dbApi.updateUser(authId, payload);
  if (error) return { success: false, error: error.message };
  return { success: true, data };
};
