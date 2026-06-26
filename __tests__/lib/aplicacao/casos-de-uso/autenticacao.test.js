/**
 * Testes BDD + unitários — casos de uso de autenticação (frontend).
 *
 * Cenários em Dado/Quando/Então alinhados às regras de negócio do auth service.
 */

jest.mock("../../../../lib/infraestrutura", () => ({
  apiAutenticacao: {
    entrar: jest.fn(),
    obterSessao: jest.fn(),
    sair: jest.fn(),
  },
  apiTurismo: {
    buscarUsuarioPorAuthId: jest.fn(),
  },
}));

const { apiAutenticacao, apiTurismo } = require("../../../../lib/infraestrutura");
const {
  entrarUsuario,
  obterSessaoAtual,
  sairUsuario,
} = require("../../../../lib/aplicacao/casos-de-uso/autenticacao");

describe("Funcionalidade: Autenticação no app mobile", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Cenário: Login com credenciais válidas", () => {
    it("Dado credenciais corretas / Quando entrar / Então retorna sessão e usuário", async () => {
      // Dado
      apiAutenticacao.entrar.mockResolvedValue({
        data: {
          user: { auth_id: "auth-1", email: "turista@marica.gov.br", nome: "Ana" },
        },
        error: null,
      });

      // Quando
      const resultado = await entrarUsuario("turista@marica.gov.br", "segura123");

      // Então
      expect(resultado.success).toBe(true);
      expect(resultado.usuarioSessao).toEqual({
        id: "auth-1",
        email: "turista@marica.gov.br",
      });
      expect(resultado.dadosUsuario.nome).toBe("Ana");
    });
  });

  describe("Cenário: Login com credenciais inválidas", () => {
    it("Dado API de erro / Quando entrar / Então retorna falha com mensagem", async () => {
      apiAutenticacao.entrar.mockResolvedValue({
        data: null,
        error: { message: "Credenciais inválidas." },
      });

      const resultado = await entrarUsuario("x@y.com", "errada");

      expect(resultado.success).toBe(false);
      expect(resultado.error).toBe("Credenciais inválidas.");
    });
  });

  describe("Cenário: Restaurar sessão ativa", () => {
    it("Dado sessão válida / Quando obter sessão / Então carrega perfil do usuário", async () => {
      apiAutenticacao.obterSessao.mockResolvedValue({
        data: { session: { user: { id: "auth-99", email: "a@b.com" } } },
      });
      apiTurismo.buscarUsuarioPorAuthId.mockResolvedValue({
        data: { id: 1, nome: "Turista" },
      });

      const resultado = await obterSessaoAtual();

      expect(resultado.usuarioSessao.id).toBe("auth-99");
      expect(resultado.dadosUsuario.nome).toBe("Turista");
      expect(apiTurismo.buscarUsuarioPorAuthId).toHaveBeenCalledWith("auth-99");
    });
  });

  describe("Cenário: Sessão inexistente", () => {
    it("Dado sem sessão / Quando obter sessão / Então retorna null", async () => {
      apiAutenticacao.obterSessao.mockResolvedValue({ data: {} });

      const resultado = await obterSessaoAtual();

      expect(resultado.usuarioSessao).toBeNull();
      expect(resultado.dadosUsuario).toBeNull();
    });
  });

  describe("Cenário: Logout", () => {
    it("Dado usuário logado / Quando sair / Então encerra sessão local", async () => {
      apiAutenticacao.sair.mockResolvedValue(undefined);

      const resultado = await sairUsuario();

      expect(apiAutenticacao.sair).toHaveBeenCalled();
      expect(resultado.success).toBe(true);
    });
  });
});
