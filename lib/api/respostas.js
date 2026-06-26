import { urlBaseApi } from "./cliente-http";

export function respostaComSucesso(resposta) {
  return { data: resposta.data, error: null };
}

export function respostaComErro(erro) {
  const semRede = erro.message === "Network Error" || erro.code === "ERR_NETWORK";
  const mensagem = semRede
    ? `Sem conexão com a API (${urlBaseApi}). Verifique se o backend está rodando e se o celular está na mesma rede Wi-Fi.`
    : erro.response?.data?.detail || erro.message;

  return { data: null, error: { message: mensagem } };
}
