import {
  clienteHttp,
  definirTokenAcesso,
  obterTokenAcesso,
} from "./cliente-http";
import { respostaComErro, respostaComSucesso } from "./respostas";

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
