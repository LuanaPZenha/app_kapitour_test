import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { NativeModules, Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const CHAVE_TOKEN = "kapitour_access_token";
const CHAVE_REFRESH = "kapitour_refresh_token";
const CHAVE_CACHE_PORTA = "kapitour_dev_api_porta";

/** 8000 primeiro — regra de firewall Windows costuma existir para esta porta. */
const PORTAS_GATEWAY = ["8000", "8080"];
const PORTA_API_PADRAO = PORTAS_GATEWAY[0];
const CAMINHO_API = "/api";

let tokenEmMemoria = null;
let refreshEmMemoria = null;
let renovandoToken = false;
let filaRenovacao = [];
let initPromise = null;
let ultimoHostResolvido = null;

function extrairHostDeUrl(raw) {
  if (!raw) return null;
  const limpo = String(raw).replace(/^https?:\/\//, "");
  return limpo.split(":")[0]?.split("/")[0] || null;
}

function extrairPortaDeUrl(raw) {
  if (!raw) return null;
  const limpo = String(raw).replace(/^https?:\/\//, "");
  const hostPorta = limpo.split("/")[0];
  const partes = hostPorta.split(":");
  return partes.length > 1 ? partes[1] : null;
}

function obterEndpointMetro() {
  const fontes = [
    NativeModules.SourceCode?.scriptURL,
    Constants.expoGoConfig?.debuggerHost,
    Constants.manifest2?.extra?.expoGo?.debuggerHost,
    Constants.manifest?.debuggerHost,
    Constants.expoConfig?.hostUri,
  ].filter(Boolean);

  for (const raw of fontes) {
    const host = extrairHostDeUrl(raw);
    const porta = extrairPortaDeUrl(raw);
    if (host && porta) return { host, porta };
  }
  return null;
}

async function obterEndpointMetroComRetry() {
  for (let i = 0; i < 20; i += 1) {
    const metro = obterEndpointMetro();
    if (metro?.host && metro?.porta && isIpWifiLan(metro.host) && !isIpVirtual(metro.host)) {
      return metro;
    }
    await aguardar(300);
  }
  return obterEndpointMetro();
}

/** Celular físico: API passa pelo Metro (mesma porta do QR code). Emulador/web: direto no gateway. */
function deveUsarProxyMetro() {
  return __DEV__ && Platform.OS !== "web" && !isAndroidEmulador();
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

function isHostTunnel(host) {
  if (!host) return false;
  const h = host.toLowerCase();
  return h.includes("exp.direct") || h.includes("ngrok") || h.includes("tunnel");
}

function aguardar(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** IP do PC na rede — vem do Metro/Expo Go (muda quando a Wi-Fi muda). */
function obterHostMetro() {
  const candidatos = [
    extrairHostDeUrl(NativeModules.SourceCode?.scriptURL),
    extrairHostDeUrl(Constants.expoGoConfig?.debuggerHost),
    extrairHostDeUrl(Constants.manifest2?.extra?.expoGo?.debuggerHost),
    extrairHostDeUrl(Constants.manifest?.debuggerHost),
    extrairHostDeUrl(Constants.expoConfig?.hostUri),
  ].filter(Boolean);

  const wifi = candidatos.find((host) => isIpWifiLan(host) && !isIpVirtual(host));
  if (wifi) return wifi;

  const valido = candidatos.find((host) => !isIpVirtual(host) && !isHostTunnel(host));
  if (valido) return valido;

  return candidatos[0] || null;
}

/** Aguarda Metro expor o IP (evita resolver localhost no boot). */
async function obterHostMetroComRetry() {
  if (Platform.OS === "web") return "localhost";

  const hostEmulador = hostEmuladorAndroid();
  if (hostEmulador) return hostEmulador;

  for (let i = 0; i < 20; i += 1) {
    const host = obterHostMetro();
    if (host && isIpWifiLan(host) && !isIpVirtual(host)) {
      return host;
    }
    await aguardar(300);
  }

  const host = obterHostMetro();
  if (host && !isIpVirtual(host) && !isHostTunnel(host)) return host;

  try {
    const parsed = new URL(
      EXPO_PUBLIC_API_URL || `http://localhost:${PORTA_API_PADRAO}${CAMINHO_API}`
    );
    if (parsed.hostname && isIpWifiLan(parsed.hostname)) {
      return parsed.hostname;
    }
  } catch {
    /* ignore */
  }

  return host || "localhost";
}

function montarUrlApi(host, porta, caminho = CAMINHO_API) {
  return `http://${host}:${porta}${caminho}`;
}

function isAndroidEmulador() {
  return Platform.OS === "android" && Constants.isDevice === false;
}

function hostEmuladorAndroid() {
  return isAndroidEmulador() ? "10.0.2.2" : null;
}

function resolverUrlProducao() {
  const url = EXPO_PUBLIC_API_URL || montarUrlApi("localhost", PORTA_API_PADRAO);
  try {
    const parsed = new URL(url);
    const caminho = parsed.pathname.replace(/\/$/, "") || CAMINHO_API;
    return `${parsed.protocol}//${parsed.host}${caminho}`;
  } catch {
    return montarUrlApi("localhost", PORTA_API_PADRAO);
  }
}

let urlBaseApiAtual = __DEV__ ? montarUrlApi("localhost", PORTA_API_PADRAO) : resolverUrlProducao();

export let urlBaseApi = urlBaseApiAtual;

export const clienteHttp = axios.create({
  baseURL: urlBaseApiAtual,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

function aplicarUrlBase(url) {
  urlBaseApiAtual = url;
  urlBaseApi = url;
  clienteHttp.defaults.baseURL = url;
}

async function sondarPorta(host, porta) {
  try {
    const { data } = await axios.get(montarUrlApi(host, porta, `${CAMINHO_API}/health`), {
      timeout: 4000,
    });
    return data?.status === "ok" || data?.status === "degraded";
  } catch {
    return false;
  }
}

async function descobrirPortaApi(host) {
  const cache = await AsyncStorage.getItem(CHAVE_CACHE_PORTA);
  const ordem =
    cache && PORTAS_GATEWAY.includes(cache)
      ? [cache, ...PORTAS_GATEWAY.filter((p) => p !== cache)]
      : [...PORTAS_GATEWAY];

  for (const porta of ordem) {
    if (await sondarPorta(host, porta)) {
      await AsyncStorage.setItem(CHAVE_CACHE_PORTA, porta);
      return porta;
    }
  }

  return PORTA_API_PADRAO;
}

/**
 * Resolve host (Metro) + porta (8000/8080) antes das chamadas à API.
 */
export async function inicializarClienteApi(forcar = false) {
  if (!__DEV__) {
    aplicarUrlBase(resolverUrlProducao());
    return urlBaseApiAtual;
  }

  const host = await obterHostMetroComRetry();

  if (isHostTunnel(host)) {
    console.warn(
      "[Kapitour] Expo em modo Tunnel — a API local não funciona. Use: npx expo start --lan"
    );
  }

  if (forcar || host !== ultimoHostResolvido) {
    initPromise = null;
    if (forcar) await AsyncStorage.removeItem(CHAVE_CACHE_PORTA);
    ultimoHostResolvido = host;
  }

  if (initPromise) return initPromise;

  initPromise = (async () => {
    if (deveUsarProxyMetro()) {
      const metro = await obterEndpointMetroComRetry();
      if (metro?.host && metro?.porta && !isHostTunnel(metro.host)) {
        const url = montarUrlApi(metro.host, metro.porta);
        aplicarUrlBase(url);
        const ok = await sondarPorta(metro.host, metro.porta);
        console.log(
          `[Kapitour] API via Metro (porta ${metro.porta}): ${url}${ok ? "" : " (health falhou — confira Docker)"}`
        );
        return url;
      }
    }

    const porta = await descobrirPortaApi(host);
    const url = montarUrlApi(host, porta);
    aplicarUrlBase(url);

    const ok = await sondarPorta(host, porta);
    console.log(
      `[Kapitour] API base URL: ${url}${ok ? "" : " (health check falhou — confira Docker/firewall)"}`
    );

    return url;
  })();

  return initPromise;
}

async function carregarTokensMemoria() {
  if (tokenEmMemoria === null) {
    tokenEmMemoria = await AsyncStorage.getItem(CHAVE_TOKEN);
  }
  if (refreshEmMemoria === null) {
    refreshEmMemoria = await AsyncStorage.getItem(CHAVE_REFRESH);
  }
}

clienteHttp.interceptors.request.use(async (config) => {
  if (__DEV__) {
    await inicializarClienteApi();
  }
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
  const base = clienteHttp.defaults.baseURL || urlBaseApiAtual;
  const { data } = await axios.post(`${base}/auth/refresh`, {
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

function isErroRede(erro) {
  return (
    !erro.response &&
    (erro.code === "ERR_NETWORK" || erro.message === "Network Error")
  );
}

clienteHttp.interceptors.response.use(
  (resposta) => resposta,
  async (erro) => {
    const configOriginal = erro.config;

    if (configOriginal && isErroRede(erro) && !configOriginal._networkRetry && __DEV__) {
      configOriginal._networkRetry = true;
      await inicializarClienteApi(true);
      return clienteHttp(configOriginal);
    }

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

export async function definirTokenAcesso(token) {
  await definirTokens(token, refreshEmMemoria);
}

export function obterTokenAcesso() {
  return AsyncStorage.getItem(CHAVE_TOKEN);
}

export function obterRefreshToken() {
  return AsyncStorage.getItem(CHAVE_REFRESH);
}
