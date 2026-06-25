import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const TOKEN_KEY = "kapitour_access_token";

function getDevMachineHost() {
  const debuggerHost =
    Constants.expoGoConfig?.debuggerHost ||
    Constants.manifest2?.extra?.expoGo?.debuggerHost ||
    Constants.expoConfig?.hostUri;

  if (debuggerHost) {
    return debuggerHost.split(":")[0];
  }
  return null;
}

function resolveApiBaseUrl() {
  const configured = EXPO_PUBLIC_API_URL || "http://localhost:8000/api";

  if (Platform.OS === "web") {
    return configured.includes("localhost")
      ? configured
      : configured.replace(/\/$/, "");
  }

  if (Platform.OS === "android" && !getDevMachineHost()) {
    // Emulador Android: localhost do host é 10.0.2.2
    if (configured.includes("localhost") || configured.includes("127.0.0.1")) {
      return "http://10.0.2.2:8000/api";
    }
  }

  const devHost = getDevMachineHost();
  if (devHost && (configured.includes("localhost") || configured.includes("127.0.0.1"))) {
    return `http://${devHost}:8000/api`;
  }

  return configured.replace(/\/$/, "");
}

const baseURL = resolveApiBaseUrl();

export const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const setAccessToken = async (token) => {
  if (token) {
    await AsyncStorage.setItem(TOKEN_KEY, token);
  } else {
    await AsyncStorage.removeItem(TOKEN_KEY);
  }
};

export const getAccessToken = () => AsyncStorage.getItem(TOKEN_KEY);

const unwrap = (response) => ({ data: response.data, error: null });
const wrapError = (error) => {
  const isNetwork = error.message === "Network Error" || error.code === "ERR_NETWORK";
  const message = isNetwork
    ? `Sem conexão com a API (${baseURL}). Verifique se o backend está rodando e se o celular está na mesma rede Wi-Fi.`
    : error.response?.data?.detail || error.message;

  return { data: null, error: { message } };
};

export const authApi = {
  async login(email, password) {
    try {
      const { data } = await api.post("/auth/login", { email, password });
      await setAccessToken(data.access_token);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async register(payload) {
    try {
      const { data } = await api.post("/auth/register", payload);
      await setAccessToken(data.access_token);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getSession() {
    try {
      const token = await getAccessToken();
      if (!token) return { data: { session: null }, error: null };
      const { data: user } = await api.get("/auth/me");
      return {
        data: {
          session: {
            access_token: token,
            user: { id: user.auth_id, email: user.email },
          },
        },
        error: null,
      };
    } catch (error) {
      await setAccessToken(null);
      return { data: { session: null }, error: null };
    }
  },

  async signOut() {
    await setAccessToken(null);
    return { error: null };
  },
};

export const dbApi = {
  async emailExists(email) {
    try {
      const { data } = await api.get("/usuarios/email-exists", { params: { email } });
      return { data: data.exists ? [{ email }] : [], error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getUserByAuthId(authId) {
    try {
      const { data } = await api.get(`/usuarios/by-auth/${authId}`);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async updateUser(authId, payload) {
    try {
      const { data } = await api.patch(`/usuarios/${authId}`, payload);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listCategorias() {
    try {
      const { data } = await api.get("/categorias");
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listPontos(categoriaId = null) {
    try {
      const params = categoriaId ? { categoria_id: categoriaId } : {};
      const { data } = await api.get("/pontos-turisticos", { params });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listRotas() {
    try {
      const { data } = await api.get("/rotas");
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getRotaPontos(rotaId) {
    try {
      const { data } = await api.get(`/rotas/${rotaId}/pontos`);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listRotaPontoByRota(rotaId) {
    try {
      const { data } = await api.get("/rota-ponto", { params: { rota_id: rotaId } });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listRotaPontoByPontos(pontoIds) {
    try {
      const { data } = await api.get("/rota-ponto", {
        params: { ponto_ids: pontoIds.join(",") },
      });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listPontoCategoriaByPontos(pontoIds) {
    try {
      const { data } = await api.get("/ponto-categoria", {
        params: { ponto_ids: pontoIds.join(",") },
      });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listPontoCategoriaByCategoria(categoriaId) {
    try {
      const { data } = await api.get("/ponto-categoria", {
        params: { categoria_id: categoriaId },
      });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getPontosByIds(ids) {
    try {
      const results = await Promise.all(
        ids.map(async (id) => {
          const { data } = await api.get(`/pontos-turisticos/${id}`);
          return data;
        })
      );
      return { data: results, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listFavoritos(usuarioId) {
    try {
      const { data } = await api.get("/favoritos", { params: { usuario_id: usuarioId } });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getFavorito(usuarioId, pontoId) {
    try {
      const { data } = await api.get("/favoritos", { params: { usuario_id: usuarioId } });
      const found = (data || []).find((f) => f.ponto_id === pontoId);
      return { data: found || null, error: found ? null : { code: "PGRST116" } };
    } catch (error) {
      return wrapError(error);
    }
  },

  async addFavorito(usuarioId, pontoId) {
    try {
      const { data } = await api.post("/favoritos", {
        usuario_id: usuarioId,
        ponto_id: pontoId,
      });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async removeFavorito(usuarioId, pontoId) {
    try {
      await api.delete("/favoritos", { params: { usuario_id: usuarioId, ponto_id: pontoId } });
      return { error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listAvaliacoes(pontoId) {
    try {
      const { data } = await api.get("/avaliacoes", { params: { ponto_id: pontoId } });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async getAvaliacao(usuarioId, pontoId) {
    try {
      const { data } = await api.get("/avaliacoes", {
        params: { usuario_id: usuarioId, ponto_id: pontoId },
      });
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async saveAvaliacao(payload) {
    try {
      const { data } = await api.post("/avaliacoes", payload);
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listProdutos() {
    try {
      const { data } = await api.get("/produtos");
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listTiposProduto() {
    try {
      const { data } = await api.get("/tipos-produto");
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },

  async listEstoque() {
    try {
      const { data } = await api.get("/estoque");
      return { data, error: null };
    } catch (error) {
      return wrapError(error);
    }
  },
};

export const cuponsApi = {
  async buscarDisponiveis(parceiroId) {
    try {
      const params = parceiroId ? { parceiro_id: parceiroId } : {};
      const { data } = await api.get("/cupons/disponiveis", { params });
      return data;
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async buscarResgatados(usuarioId) {
    try {
      const { data } = await api.get(`/cupons/resgatados/${usuarioId}`);
      return data;
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async verificarResgatado(cupomId, usuarioId) {
    try {
      const { data } = await api.get("/cupons/verificar", {
        params: { cupom_id: cupomId, usuario_id: usuarioId },
      });
      return { success: true, jaResgatado: data.jaResgatado, data: data.jaResgatado ? {} : null };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async resgatar(cupomId, usuarioId, parceiroId) {
    try {
      const { data } = await api.post("/cupons/resgatar", {
        cupom_id: cupomId,
        usuario_id: usuarioId,
        parceiro_id: parceiroId,
      });
      return data;
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async campanhasParceiro(parceiroId) {
    try {
      const { data } = await api.get(`/cupons/campanhas-parceiro/${parceiroId}`);
      return data;
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async contagemCampanha(parceiroId) {
    try {
      const { data } = await api.get(`/cupons/contagem-campanha/${parceiroId}`);
      return data;
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
};

export const atualizarUsuario = async (authId, payload) => {
  const { data, error } = await dbApi.updateUser(authId, payload);
  if (error) return { success: false, error: error.message };
  return { success: true, data };
};
