import {
  clienteHttp,
  definirTokens,
  obterRefreshToken,
  obterTokenAcesso,
} from "./cliente-http";
import { respostaComErro, respostaComSucesso } from "./respostas";

export const apiAutenticacao = {
  async entrar(email, senha) {
    try {
      const { data } = await clienteHttp.post("/auth/login", { email, password: senha });
      await definirTokens(data.access_token, data.refresh_token);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async cadastrar(dadosCadastro) {
    try {
      const { data } = await clienteHttp.post("/auth/register", dadosCadastro);
      await definirTokens(data.access_token, data.refresh_token);
      return respostaComSucesso({ data });
    } catch (erro) {
      return respostaComErro(erro);
    }
  },

  async renovarToken() {
    const refresh = await obterRefreshToken();
    if (!refresh) return { data: null, error: { message: "Sem refresh token" } };
    try {
      const { data } = await clienteHttp.post("/auth/refresh", { refresh_token: refresh });
      await definirTokens(data.access_token, data.refresh_token);
      return respostaComSucesso({ data });
    } catch (erro) {
      await definirTokens(null, null);
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
      await definirTokens(null, null);
      return { data: { session: null }, error: null };
    }
  },

  async sair() {
    try {
      const refresh = await obterRefreshToken();
      if (refresh) {
        await clienteHttp.post("/auth/logout", { refresh_token: refresh });
      }
    } catch {
      // Encerra sessão local mesmo se o servidor falhar
    } finally {
      await definirTokens(null, null);
    }
    return { error: null };
  },
};
