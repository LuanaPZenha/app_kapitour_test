import { urlBaseApi } from "./cliente-http";

export function respostaComSucesso(resposta) {
  return { data: resposta.data, error: null };
}

export function respostaComErro(erro) {
  const semRede = erro.message === "Network Error" || erro.code === "ERR_NETWORK";
  const mensagem = semRede
    ? `Sem conexão com a API (${urlBaseApi}). Celular e PC na mesma Wi-Fi? Teste http://SEU_IP:8000/api/health no navegador do celular.`
    : erro.response?.data?.detail || erro.message;

  if (__DEV__ && semRede) {
    console.warn("[Kapitour] Erro de rede:", erro.code, erro.message, "→", urlBaseApi);
  }

  return { data: null, error: { message: mensagem } };
}
