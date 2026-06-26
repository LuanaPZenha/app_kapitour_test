/**
 * Infraestrutura — reexporta adaptadores HTTP (lib/api).
 */
export * from "../api/cliente-http";
export * from "../api/respostas";
export * from "../api/autenticacao";
export * from "../api/turismo";
export * from "../api/kapipass";
export * from "../api/cupons";
export * from "../api/compatibilidade";

import { clienteHttp, definirTokenAcesso, obterTokenAcesso } from "../api/cliente-http";

export const api = clienteHttp;
export const setAccessToken = definirTokenAcesso;
export const getAccessToken = obterTokenAcesso;
