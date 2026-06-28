import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { NativeModules, Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const CHAVE_TOKEN = "kapitour_access_token";
const CHAVE_REFRESH = "kapitour_refresh_token";
let tokenEmMemoria = null;
let refreshEmMemoria = null;
let renovandoToken = false;
let filaRenovacao = [];

/** Porta exposta no host (8000 = liberada no firewall Windows; 8080 exige regra extra). */
const PORTA_API_PADRAO = "8000";
const PORTA_API_LEGADA = "8080";

function resolverPortaApi(portaConfigurada) {
  const porta = portaConfigurada || PORTA_API_PADRAO;
  // Celular em dev: 8080 costuma estar bloqueada no firewall — usa 8000
  if (__DEV__ && Platform.OS !== "web" && porta === PORTA_API_LEGADA) {
    return PORTA_API_PADRAO;
  }
  return porta;
}

function extrairHostDeUrl(raw) {
  if (!raw) return null;
  const limpo = String(raw).replace(/^https?:\/\//, "");
  return limpo.split(":")[0]?.split("/")[0] || null;
}

function isIpVirtual(host) {
  if (!host || host === "localhost" || host === "127.0.0.1") return true;
  return (
    host.startsWith("172.17.") ||
    host.startsWith("172.24.") ||
    host.startsWith("169.254.")
  );
}

function isIpWifiLan(host) {
  return /^(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})$/.test(host);
}

/** IP da máquina de dev (Metro/Expo) — prioriza Wi-Fi (192.168.x.x). */
function obterHostMaquinaDesenvolvimento() {
  const candidatos = [
    extrairHostDeUrl(NativeModules.SourceCode?.scriptURL),
    extrairHostDeUrl(Constants.expoGoConfig?.debuggerHost),
    extrairHostDeUrl(Constants.manifest2?.extra?.expoGo?.debuggerHost),
    extrairHostDeUrl(Constants.manifest?.debuggerHost),
    extrairHostDeUrl(Constants.expoConfig?.hostUri),
  ].filter(Boolean);

  const wifi = candidatos.find((host) => isIpWifiLan(host) && !isIpVirtual(host));
  if (wifi) return wifi;

  const valido = candidatos.find((host) => !isIpVirtual(host));
  if (valido) return valido;

  return candidatos[0] || null;
}

function escolherHostMobile(hostDev, hostEnv) {
  if (hostEnv && isIpWifiLan(hostEnv) && (!hostDev || isIpVirtual(hostDev))) {
    return hostEnv;
  }
  if (hostDev && !isIpVirtual(hostDev)) {
    return hostDev;
  }
  if (hostEnv && !isIpVirtual(hostEnv)) {
    return hostEnv;
  }
  return null;
}

function montarUrlApi(host, porta, caminho) {
  return `http://${host}:${porta}${caminho}`;
}

function resolverUrlBaseApi() {
  const urlConfigurada = EXPO_PUBLIC_API_URL || `http://localhost:${PORTA_API_PADRAO}/api`;

  try {
    const parsed = new URL(urlConfigurada);
    const caminho = parsed.pathname.replace(/\/$/, "") || "/api";
    const porta = resolverPortaApi(parsed.port || PORTA_API_PADRAO);
    const hostLocal = parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";
    const hostEnv = hostLocal ? null : parsed.hostname;
    const hostDev = obterHostMaquinaDesenvolvimento();

    if (Platform.OS === "web") {
      return montarUrlApi("localhost", porta, caminho);
    }

    const hostMobile = escolherHostMobile(hostDev, hostEnv);
    if (hostMobile) {
      return montarUrlApi(hostMobile, porta, caminho);
    }

    // Emulador Android (localhost no Metro)
    if (Platform.OS === "android" && (hostLocal || isIpVirtual(hostDev))) {
      return montarUrlApi("10.0.2.2", porta, caminho);
    }

    return `${parsed.protocol}//${parsed.host}${caminho}`;
  } catch {
    const parsedEnv = (() => {
      try {
        return new URL(EXPO_PUBLIC_API_URL || "");
      } catch {
        return null;
      }
    })();
    const hostEnv = parsedEnv && !["localhost", "127.0.0.1"].includes(parsedEnv.hostname)
      ? parsedEnv.hostname
      : null;
    const hostDev = obterHostMaquinaDesenvolvimento();
    const hostMobile = escolherHostMobile(hostDev, hostEnv);
    if (hostMobile) {
      return montarUrlApi(hostMobile, PORTA_API_PADRAO, "/api");
    }
    if (Platform.OS === "android") {
      return montarUrlApi("10.0.2.2", PORTA_API_PADRAO, "/api");
    }
    return `http://localhost:${PORTA_API_PADRAO}/api`;
  }
}

export const urlBaseApi = resolverUrlBaseApi();

if (__DEV__) {
  console.log("[Kapitour] API base URL:", urlBaseApi);
}

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
