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
