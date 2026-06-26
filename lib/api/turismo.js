import { clienteHttp } from "./cliente-http";
import { respostaComErro, respostaComSucesso } from "./respostas";

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
      const unicos = [...new Set((ids || []).filter(Boolean))];
      if (!unicos.length) {
        return { data: [], error: null };
      }
      if (unicos.length === 1) {
        const { data } = await clienteHttp.get(`/pontos-turisticos/${unicos[0]}`);
        return { data: data ? [data] : [], error: null };
      }
      const { data: todos } = await clienteHttp.get("/pontos-turisticos");
      const porId = Object.fromEntries((todos || []).map((p) => [p.id, p]));
      return {
        data: unicos.map((id) => porId[id]).filter(Boolean),
        error: null,
      };
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

export async function atualizarPerfilUsuario(authId, dados) {
  const { data, error } = await apiTurismo.atualizarUsuario(authId, dados);
  if (error) return { success: false, error: error.message };
  return { success: true, data };
}
