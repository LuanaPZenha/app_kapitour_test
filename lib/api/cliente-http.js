import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const CHAVE_TOKEN = "kapitour_access_token";
let tokenEmMemoria = null;

function obterHostMaquinaDesenvolvimento() {
  const hostDepurador =
    Constants.expoGoConfig?.debuggerHost ||
    Constants.manifest2?.extra?.expoGo?.debuggerHost ||
    Constants.expoConfig?.hostUri;

  return hostDepurador ? hostDepurador.split(":")[0] : null;
}

function resolverUrlBaseApi() {
  const urlConfigurada = EXPO_PUBLIC_API_URL || "http://localhost:8000/api";

  if (Platform.OS === "web") {
    return urlConfigurada.includes("localhost")
      ? urlConfigurada
      : urlConfigurada.replace(/\/$/, "");
  }

  if (Platform.OS === "android" && !obterHostMaquinaDesenvolvimento()) {
    if (urlConfigurada.includes("localhost") || urlConfigurada.includes("127.0.0.1")) {
      return "http://10.0.2.2:8000/api";
    }
  }

  const hostDev = obterHostMaquinaDesenvolvimento();
  if (hostDev && (urlConfigurada.includes("localhost") || urlConfigurada.includes("127.0.0.1"))) {
    return `http://${hostDev}:8000/api`;
  }

  return urlConfigurada.replace(/\/$/, "");
}

export const urlBaseApi = resolverUrlBaseApi();

export const clienteHttp = axios.create({
  baseURL: urlBaseApi,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

clienteHttp.interceptors.request.use(async (config) => {
  if (tokenEmMemoria === null) {
    tokenEmMemoria = await AsyncStorage.getItem(CHAVE_TOKEN);
  }
  if (tokenEmMemoria) {
    config.headers.Authorization = `Bearer ${tokenEmMemoria}`;
  }
  return config;
});

export async function definirTokenAcesso(token) {
  tokenEmMemoria = token || null;
  if (token) {
    await AsyncStorage.setItem(CHAVE_TOKEN, token);
  } else {
    await AsyncStorage.removeItem(CHAVE_TOKEN);
  }
}

export function obterTokenAcesso() {
  return AsyncStorage.getItem(CHAVE_TOKEN);
}
