import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const CHAVE_TOKEN = "kapitour_access_token";
const CHAVE_REFRESH = "kapitour_refresh_token";
let tokenEmMemoria = null;
let refreshEmMemoria = null;
let renovandoToken = false;
let filaRenovacao = [];

function obterHostMaquinaDesenvolvimento() {
  const hostDepurador =
    Constants.expoGoConfig?.debuggerHost ||
    Constants.manifest2?.extra?.expoGo?.debuggerHost ||
    Constants.expoConfig?.hostUri;

  return hostDepurador ? hostDepurador.split(":")[0] : null;
}

const PORTA_API_PADRAO = "8080";

function resolverUrlBaseApi() {
  const urlConfigurada = EXPO_PUBLIC_API_URL || `http://localhost:${PORTA_API_PADRAO}/api`;

  try {
    const parsed = new URL(urlConfigurada);
    const caminho = parsed.pathname.replace(/\/$/, "") || "/api";
    const porta = parsed.port || PORTA_API_PADRAO;
    const hostLocal = parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";
    const hostDev = obterHostMaquinaDesenvolvimento();

    if (Platform.OS === "web") {
      return `${parsed.protocol}//${parsed.host}${caminho}`;
    }

    if (Platform.OS === "android" && !hostDev && hostLocal) {
      return `http://10.0.2.2:${porta}${caminho}`;
    }

    // localhost no .env → IP da máquina na rede (Expo DevTools), porta da API (8080)
    if (hostDev && hostLocal) {
      return `http://${hostDev}:${porta}${caminho}`;
    }

    // IP desatualizado no .env → usa IP atual do Expo, mantém porta da API
    if (hostDev && !hostLocal && parsed.hostname !== hostDev) {
      return `http://${hostDev}:${porta}${caminho}`;
    }

    return `${parsed.protocol}//${parsed.host}${caminho}`;
  } catch {
    const hostDev = obterHostMaquinaDesenvolvimento();
    if (hostDev) {
      return `http://${hostDev}:${PORTA_API_PADRAO}/api`;
    }
    return `http://localhost:${PORTA_API_PADRAO}/api`;
  }
}

export const urlBaseApi = resolverUrlBaseApi();

export const clienteHttp = axios.create({
  baseURL: urlBaseApi,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

async function carregarTokensMemoria() {
  if (tokenEmMemoria === null) {
    tokenEmMemoria = await AsyncStorage.getItem(CHAVE_TOKEN);
  }
  if (refreshEmMemoria === null) {
    refreshEmMemoria = await AsyncStorage.getItem(CHAVE_REFRESH);
  }
}

clienteHttp.interceptors.request.use(async (config) => {
  await carregarTokensMemoria();
  if (tokenEmMemoria) {
    config.headers.Authorization = `Bearer ${tokenEmMemoria}`;
  }
  return config;
});

async function executarRenovacaoToken() {
  await carregarTokensMemoria();
  if (!refreshEmMemoria) {
    throw new Error("Sem refresh token");
  }
  const { data } = await axios.post(`${urlBaseApi}/auth/refresh`, {
    refresh_token: refreshEmMemoria,
  });
  await definirTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

function enfileirarRenovacao() {
  return new Promise((resolve, reject) => {
    filaRenovacao.push({ resolve, reject });
  });
}

function processarFilaRenovacao(erro, token = null) {
  filaRenovacao.forEach((promessa) => {
    if (erro) promessa.reject(erro);
    else promessa.resolve(token);
  });
  filaRenovacao = [];
}

clienteHttp.interceptors.response.use(
  (resposta) => resposta,
  async (erro) => {
    const configOriginal = erro.config;
    if (
      !configOriginal ||
      erro.response?.status !== 401 ||
      configOriginal._retry ||
      configOriginal.url?.includes("/auth/login") ||
      configOriginal.url?.includes("/auth/register") ||
      configOriginal.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(erro);
    }

    if (renovandoToken) {
      const novoToken = await enfileirarRenovacao();
      configOriginal.headers.Authorization = `Bearer ${novoToken}`;
      return clienteHttp(configOriginal);
    }

    configOriginal._retry = true;
    renovandoToken = true;

    try {
      const novoToken = await executarRenovacaoToken();
      processarFilaRenovacao(null, novoToken);
      configOriginal.headers.Authorization = `Bearer ${novoToken}`;
      return clienteHttp(configOriginal);
    } catch (erroRenovacao) {
      processarFilaRenovacao(erroRenovacao, null);
      await definirTokens(null, null);
      return Promise.reject(erroRenovacao);
    } finally {
      renovandoToken = false;
    }
  }
);

export async function definirTokens(accessToken, refreshToken) {
  tokenEmMemoria = accessToken || null;
  refreshEmMemoria = refreshToken || null;

  if (accessToken) {
    await AsyncStorage.setItem(CHAVE_TOKEN, accessToken);
  } else {
    await AsyncStorage.removeItem(CHAVE_TOKEN);
  }

  if (refreshToken) {
    await AsyncStorage.setItem(CHAVE_REFRESH, refreshToken);
  } else {
    await AsyncStorage.removeItem(CHAVE_REFRESH);
  }
}

/** Compatibilidade — mantém API anterior que só persistia access token. */
export async function definirTokenAcesso(token) {
  await definirTokens(token, refreshEmMemoria);
}

export function obterTokenAcesso() {
  return AsyncStorage.getItem(CHAVE_TOKEN);
}

export function obterRefreshToken() {
  return AsyncStorage.getItem(CHAVE_REFRESH);
}
