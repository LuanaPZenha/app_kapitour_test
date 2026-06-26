import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { EXPO_PUBLIC_API_URL } from "@env";

const CHAVE_TOKEN = "kapitour_access_token";

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
  const token = await AsyncStorage.getItem(CHAVE_TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function definirTokenAcesso(token) {
  if (token) {
    await AsyncStorage.setItem(CHAVE_TOKEN, token);
  } else {
    await AsyncStorage.removeItem(CHAVE_TOKEN);
  }
}

export function obterTokenAcesso() {
  return AsyncStorage.getItem(CHAVE_TOKEN);
}

function respostaComSucesso(resposta) {
  return { data: resposta.data, error: null };
}

function respostaComErro(erro) {
  const semRede = erro.message === "Network Error" || erro.code === "ERR_NETWORK";
  const mensagem = semRede
    ? `Sem conexão com a API (${urlBaseApi}). Verifique se o backend está rodando e se o celular está na mesma rede Wi-Fi.`
    : erro.response?.data?.detail || erro.message;

  return { data: null, error: { message: mensagem } };
}

export const apiAutenticacao = {
  async entrar(email, senha) {
    try {
      const { data } = await clienteHttp.post("/auth/login", { email, password: senha });
      await definirTokenAcesso(data.access_token);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async cadastrar(dadosCadastro) {
    try {
      const { data } = await clienteHttp.post("/auth/register", dadosCadastro);
      await definirTokenAcesso(data.access_token);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async obterSessao() {
    try {
      const token = await obterTokenAcesso();
      if (!token) return { data: { session: null }, error: null };

      const { data: usuario } = await clienteHttp.get("/auth/me");
      return {
        data: {
          session: {
            access_token: token,
            user: { id: usuario.auth_id, email: usuario.email },
          },
        },
        error: null,
      };
    } catch {
      await definirTokenAcesso(null);
      return { data: { session: null }, error: null };
    }
  },

  async sair() {
    await definirTokenAcesso(null);
    return { error: null };
  },
};

export const apiTurismo = {
  async verificarEmailCadastrado(email) {
    try {
      const { data } = await clienteHttp.get("/usuarios/email-exists", { params: { email } });
      return { data: data.exists ? [{ email }] : [], error: null };
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarUsuarioPorAuthId(authId) {
    try {
      const { data } = await clienteHttp.get(`/usuarios/by-auth/${authId}`);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async atualizarUsuario(authId, dados) {
    try {
      const { data } = await clienteHttp.patch(`/usuarios/${authId}`, dados);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCategorias() {
    try {
      const { data } = await clienteHttp.get("/categorias");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarPontosTuristicos(categoriaId = null) {
    try {
      const params = categoriaId ? { categoria_id: categoriaId } : {};
      const { data } = await clienteHttp.get("/pontos-turisticos", { params });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarRotas() {
    try {
      const { data } = await clienteHttp.get("/rotas");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarPontosDaRota(rotaId) {
    try {
      const { data } = await clienteHttp.get(`/rotas/${rotaId}/pontos`);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarRelacaoRotaPontoPorRota(rotaId) {
    try {
      const { data } = await clienteHttp.get("/rota-ponto", { params: { rota_id: rotaId } });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarRelacaoRotaPontoPorPontos(idsPontos) {
    try {
      const { data } = await clienteHttp.get("/rota-ponto", {
        params: { ponto_ids: idsPontos.join(",") },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCategoriasPorPontos(idsPontos) {
    try {
      const { data } = await clienteHttp.get("/ponto-categoria", {
        params: { ponto_ids: idsPontos.join(",") },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCategoriasPorCategoria(categoriaId) {
    try {
      const { data } = await clienteHttp.get("/ponto-categoria", {
        params: { categoria_id: categoriaId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarPontosPorIds(ids) {
    try {
      const resultados = await Promise.all(
        ids.map(async (id) => {
          const { data } = await clienteHttp.get(`/pontos-turisticos/${id}`);
          return data;
        })
      );
      return { data: resultados, error: null };
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarFavoritos(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/favoritos", { params: { usuario_id: usuarioId } });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarFavorito(usuarioId, pontoId) {
    try {
      const { data } = await clienteHttp.get("/favoritos", { params: { usuario_id: usuarioId } });
      const favorito = (data || []).find((item) => item.ponto_id === pontoId);
      return { data: favorito || null, error: favorito ? null : { code: "PGRST116" } };
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async adicionarFavorito(usuarioId, pontoId) {
    try {
      const { data } = await clienteHttp.post("/favoritos", {
        usuario_id: usuarioId,
        ponto_id: pontoId,
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async removerFavorito(usuarioId, pontoId) {
    try {
      await clienteHttp.delete("/favoritos", {
        params: { usuario_id: usuarioId, ponto_id: pontoId },
      });
      return { error: null };
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarAvaliacoes(pontoId) {
    try {
      const { data } = await clienteHttp.get("/avaliacoes", { params: { ponto_id: pontoId } });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarAvaliacaoDoUsuario(usuarioId, pontoId) {
    try {
      const { data } = await clienteHttp.get("/avaliacoes", {
        params: { usuario_id: usuarioId, ponto_id: pontoId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async salvarAvaliacao(dadosAvaliacao) {
    try {
      const { data } = await clienteHttp.post("/avaliacoes", dadosAvaliacao);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarProdutos() {
    try {
      const { data } = await clienteHttp.get("/produtos");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarTiposProduto() {
    try {
      const { data } = await clienteHttp.get("/tipos-produto");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarEstoque() {
    try {
      const { data } = await clienteHttp.get("/estoque");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },
};

export const apiKapiPass = {
  async obterPassaporte() {
    try {
      const { data } = await clienteHttp.get("/kapipass/me");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarNiveis() {
    try {
      const { data } = await clienteHttp.get("/kapipass/niveis");
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async registrarCheckin(pontoTuristicoId, latitude = null, longitude = null) {
    try {
      const { data } = await clienteHttp.post("/kapipass/checkin", {
        ponto_turistico_id: pontoTuristicoId,
        latitude,
        longitude,
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCheckins(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/checkins", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarCarimbos(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/carimbos", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarConquistas(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/conquistas", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarColecoes(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/colecoes", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarMissoes(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/missoes", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async aceitarMissao(missaoId) {
    try {
      const { data } = await clienteHttp.post(`/kapipass/missoes/${missaoId}/aceitar`, {});
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarAtividadesEco(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/eco", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async registrarAtividadeEco(ecoAtividadeId) {
    try {
      const { data } = await clienteHttp.post("/kapipass/eco/registrar", {
        eco_atividade_id: ecoAtividadeId,
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarDiario(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/diario", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async listarTesouros(usuarioId) {
    try {
      const { data } = await clienteHttp.get("/kapipass/tesouros", {
        params: { usuario_id: usuarioId },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async concluirTesouro(tesouroId) {
    try {
      const { data } = await clienteHttp.post(`/kapipass/tesouros/${tesouroId}/concluir`, {});
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async buscarRankings(categoria = "exploradores", pagina = 1, tamanho = 20) {
    try {
      const { data } = await clienteHttp.get("/kapipass/rankings", {
        params: { categoria, page: pagina, size: tamanho },
      });
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },
};

export const apiCupons = {
  async buscarDisponiveis(parceiroId) {
    try {
      const params = parceiroId ? { parceiro_id: parceiroId } : {};
      const { data } = await clienteHttp.get("/cupons/disponiveis", { params });
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async buscarResgatados(usuarioId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/resgatados/${usuarioId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async verificarSeJaResgatado(cupomId, usuarioId) {
    try {
      const { data } = await clienteHttp.get("/cupons/verificar", {
        params: { cupom_id: cupomId, usuario_id: usuarioId },
      });
      return { success: true, jaResgatado: data.jaResgatado, data: data.jaResgatado ? {} : null };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async resgatar(cupomId, usuarioId, parceiroId) {
    try {
      const { data } = await clienteHttp.post("/cupons/resgatar", {
        cupom_id: cupomId,
        usuario_id: usuarioId,
        parceiro_id: parceiroId,
      });
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async listarCampanhasDoParceiro(parceiroId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/campanhas-parceiro/${parceiroId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },

  async contarCuponsPorCampanha(parceiroId) {
    try {
      const { data } = await clienteHttp.get(`/cupons/contagem-campanha/${parceiroId}`);
      return data;
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  },
};

export async function atualizarPerfilUsuario(authId, dados) {
  const { data, error } = await apiTurismo.atualizarUsuario(authId, dados);
  if (error) return { success: false, error: error.message };
  return { success: true, data };
}

// ── Aliases de compatibilidade (telas ainda usam nomes legados) ──

export const authApi = {
  login: (email, senha) => apiAutenticacao.entrar(email, senha),
  register: (dados) => apiAutenticacao.cadastrar(dados),
  getSession: () => apiAutenticacao.obterSessao(),
  signOut: () => apiAutenticacao.sair(),
};

export const dbApi = {
  emailExists: (email) => apiTurismo.verificarEmailCadastrado(email),
  getUserByAuthId: (authId) => apiTurismo.buscarUsuarioPorAuthId(authId),
  updateUser: (authId, dados) => apiTurismo.atualizarUsuario(authId, dados),
  listCategorias: () => apiTurismo.listarCategorias(),
  listPontos: (categoriaId) => apiTurismo.listarPontosTuristicos(categoriaId),
  listRotas: () => apiTurismo.listarRotas(),
  getRotaPontos: (rotaId) => apiTurismo.buscarPontosDaRota(rotaId),
  listRotaPontoByRota: (rotaId) => apiTurismo.listarRelacaoRotaPontoPorRota(rotaId),
  listRotaPontoByPontos: (ids) => apiTurismo.listarRelacaoRotaPontoPorPontos(ids),
  listPontoCategoriaByPontos: (ids) => apiTurismo.listarCategoriasPorPontos(ids),
  listPontoCategoriaByCategoria: (id) => apiTurismo.listarCategoriasPorCategoria(id),
  getPontosByIds: (ids) => apiTurismo.buscarPontosPorIds(ids),
  listFavoritos: (usuarioId) => apiTurismo.listarFavoritos(usuarioId),
  getFavorito: (usuarioId, pontoId) => apiTurismo.buscarFavorito(usuarioId, pontoId),
  addFavorito: (usuarioId, pontoId) => apiTurismo.adicionarFavorito(usuarioId, pontoId),
  removeFavorito: (usuarioId, pontoId) => apiTurismo.removerFavorito(usuarioId, pontoId),
  listAvaliacoes: (pontoId) => apiTurismo.listarAvaliacoes(pontoId),
  getAvaliacao: (usuarioId, pontoId) => apiTurismo.buscarAvaliacaoDoUsuario(usuarioId, pontoId),
  saveAvaliacao: (dados) => apiTurismo.salvarAvaliacao(dados),
  listProdutos: () => apiTurismo.listarProdutos(),
  listTiposProduto: () => apiTurismo.listarTiposProduto(),
  listEstoque: () => apiTurismo.listarEstoque(),
};

export const kapipassApi = {
  getPassaporte: () => apiKapiPass.obterPassaporte(),
  listNiveis: () => apiKapiPass.listarNiveis(),
  checkin: (pontoId, lat, lng) => apiKapiPass.registrarCheckin(pontoId, lat, lng),
  listCheckins: (usuarioId) => apiKapiPass.listarCheckins(usuarioId),
  listCarimbos: (usuarioId) => apiKapiPass.listarCarimbos(usuarioId),
  listConquistas: (usuarioId) => apiKapiPass.listarConquistas(usuarioId),
  listColecoes: (usuarioId) => apiKapiPass.listarColecoes(usuarioId),
  listMissoes: (usuarioId) => apiKapiPass.listarMissoes(usuarioId),
  aceitarMissao: (missaoId) => apiKapiPass.aceitarMissao(missaoId),
  listEco: (usuarioId) => apiKapiPass.listarAtividadesEco(usuarioId),
  registrarEco: (atividadeId) => apiKapiPass.registrarAtividadeEco(atividadeId),
  listDiario: (usuarioId) => apiKapiPass.listarDiario(usuarioId),
  listTesouros: (usuarioId) => apiKapiPass.listarTesouros(usuarioId),
  concluirTesouro: (tesouroId) => apiKapiPass.concluirTesouro(tesouroId),
  getRankings: (categoria, pagina, tamanho) =>
    apiKapiPass.buscarRankings(categoria, pagina, tamanho),
};

export const cuponsApi = {
  buscarDisponiveis: (parceiroId) => apiCupons.buscarDisponiveis(parceiroId),
  buscarResgatados: (usuarioId) => apiCupons.buscarResgatados(usuarioId),
  verificarResgatado: (cupomId, usuarioId) =>
    apiCupons.verificarSeJaResgatado(cupomId, usuarioId),
  resgatar: (cupomId, usuarioId, parceiroId) =>
    apiCupons.resgatar(cupomId, usuarioId, parceiroId),
  campanhasParceiro: (parceiroId) => apiCupons.listarCampanhasDoParceiro(parceiroId),
  contagemCampanha: (parceiroId) => apiCupons.contarCuponsPorCampanha(parceiroId),
};

export const api = clienteHttp;
export const setAccessToken = definirTokenAcesso;
export const getAccessToken = obterTokenAcesso;
