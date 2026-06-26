/**
 * Casos de uso de autenticação — camada de aplicação (sem HTTP direto nas telas).
 */
import { apiAutenticacao, apiTurismo } from "../../infraestrutura";

export async function entrarUsuario(email, senha) {
  const { data, error } = await apiAutenticacao.entrar(email, senha);
  if (error) {
    return { success: false, error: error.message };
  }
  return {
    success: true,
    usuarioSessao: { id: data.user.auth_id, email: data.user.email },
    dadosUsuario: data.user,
  };
}

export async function obterSessaoAtual() {
  const { data } = await apiAutenticacao.obterSessao();
  if (!data?.session?.user) {
    return { usuarioSessao: null, dadosUsuario: null };
  }
  const authId = data.session.user.id;
  const { data: dadosUsuario } = await apiTurismo.buscarUsuarioPorAuthId(authId);
  return {
    usuarioSessao: data.session.user,
    dadosUsuario: dadosUsuario || null,
  };
}

export async function sairUsuario() {
  await apiAutenticacao.sair();
  return { success: true };
}
