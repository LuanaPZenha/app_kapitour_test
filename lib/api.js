export {
  clienteHttp,
  definirTokenAcesso,
  obterTokenAcesso,
  urlBaseApi,
} from "./api/cliente-http";

export { apiAutenticacao } from "./api/autenticacao";
export { apiTurismo, atualizarPerfilUsuario } from "./api/turismo";
export { apiKapiPass } from "./api/kapipass";
export { apiCupons } from "./api/cupons";

export {
  authApi,
  cuponsApi,
  dbApi,
  kapipassApi,
} from "./api/compatibilidade";

import { clienteHttp, definirTokenAcesso, obterTokenAcesso } from "./api/cliente-http";

export const api = clienteHttp;
export const setAccessToken = definirTokenAcesso;
export const getAccessToken = obterTokenAcesso;
