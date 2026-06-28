import { apiAutenticacao } from "./autenticacao";
import { apiCupons } from "./cupons";
import { apiKapiPass } from "./kapipass";
import { apiTurismo } from "./turismo";

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
  listFavoritos: () => apiTurismo.listarFavoritos(),
  getFavorito: (_usuarioId, pontoId) => apiTurismo.buscarFavorito(pontoId),
  addFavorito: (_usuarioId, pontoId) => apiTurismo.adicionarFavorito(pontoId),
  removeFavorito: (_usuarioId, pontoId) => apiTurismo.removerFavorito(pontoId),
  listAvaliacoes: (pontoId) => apiTurismo.listarAvaliacoes(pontoId),
  getAvaliacao: (_usuarioId, pontoId) => apiTurismo.buscarAvaliacaoDoUsuario(pontoId),
  saveAvaliacao: (dados) =>
    apiTurismo.salvarAvaliacao({
      ponto_id: dados.ponto_id,
      nota: dados.nota,
      comentario: dados.comentario,
    }),
  listProdutos: () => apiTurismo.listarProdutos(),
  listTiposProduto: () => apiTurismo.listarTiposProduto(),
  listEstoque: () => apiTurismo.listarEstoque(),
};

export const kapipassApi = {
  getPassaporte: () => apiKapiPass.obterPassaporte(),
  listNiveis: () => apiKapiPass.listarNiveis(),
  checkin: (pontoId, lat, lng) => apiKapiPass.registrarCheckin(pontoId, lat, lng),
  listCheckins: () => apiKapiPass.listarCheckins(),
  listCarimbos: () => apiKapiPass.listarCarimbos(),
  listConquistas: () => apiKapiPass.listarConquistas(),
  listColecoes: () => apiKapiPass.listarColecoes(),
  listMissoes: () => apiKapiPass.listarMissoes(),
  aceitarMissao: (missaoId) => apiKapiPass.aceitarMissao(missaoId),
  listEco: () => apiKapiPass.listarAtividadesEco(),
  registrarEco: (atividadeId) => apiKapiPass.registrarAtividadeEco(atividadeId),
  listDiario: () => apiKapiPass.listarDiario(),
  listTesouros: () => apiKapiPass.listarTesouros(),
  concluirTesouro: (tesouroId) => apiKapiPass.concluirTesouro(tesouroId),
  getRankings: (categoria, pagina, tamanho) =>
    apiKapiPass.buscarRankings(categoria, pagina, tamanho),
};

export const cuponsApi = {
  buscarDisponiveis: (parceiroId) => apiCupons.buscarDisponiveis(parceiroId),
  buscarResgatados: (usuarioId) => apiCupons.buscarResgatados(usuarioId ?? null),
  verificarResgatado: (cupomId, usuarioId) =>
    apiCupons.verificarSeJaResgatado(cupomId, usuarioId ?? null),
  resgatar: (cupomId, usuarioId, parceiroId) =>
    apiCupons.resgatar(cupomId, usuarioId ?? null, parceiroId ?? null),
  campanhasParceiro: (parceiroId) => apiCupons.listarCampanhasDoParceiro(parceiroId),
  contagemCampanha: (parceiroId) => apiCupons.contarCuponsPorCampanha(parceiroId),
};
