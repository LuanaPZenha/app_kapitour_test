import { urlBaseApi } from "./cliente-http";

export function respostaComSucesso(resposta) {
  return { data: resposta.data, error: null };
}

export function respostaComErro(erro) {
  const semRede = erro.message === "Network Error" || erro.code === "ERR_NETWORK";
  const mensagem = semRede
    ? `Sem conexão com a API (${urlBaseApi}). Celular e PC na mesma Wi-Fi? Docker rodando? Teste no navegador do celular: ${urlBaseApi}/health — se não abrir, execute scripts\\abrir-firewall-api.bat como Administrador.`
    : erro.response?.data?.detail || erro.message;

  if (__DEV__ && semRede) {
    console.warn("[Kapitour] Erro de rede:", erro.code, erro.message, "->", urlBaseApi);
  }

  return { data: null, error: { message: mensagem } };
}
