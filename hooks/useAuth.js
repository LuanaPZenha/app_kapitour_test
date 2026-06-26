import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";
import {
  entrarUsuario,
  obterSessaoAtual,
  sairUsuario,
} from "../lib/aplicacao/casos-de-uso/autenticacao";

const ContextoAutenticacao = createContext(null);

export function ProvedorAutenticacao({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [dadosUsuario, setDadosUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  const carregarSessao = useCallback(async () => {
    const { usuarioSessao, dadosUsuario: perfil } = await obterSessaoAtual();
    setUsuario(usuarioSessao);
    setDadosUsuario(perfil);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        await carregarSessao();
      } finally {
        setCarregando(false);
      }
    })();
  }, [carregarSessao]);

  const entrar = useCallback(async (email, senha) => {
    const resultado = await entrarUsuario(email, senha);
    if (!resultado.success) {
      return resultado;
    }
    setUsuario(resultado.usuarioSessao);
    setDadosUsuario(resultado.dadosUsuario);
    return { success: true, user: resultado.usuarioSessao };
  }, []);

  const sair = useCallback(async () => {
    try {
      await sairUsuario();
      setUsuario(null);
      setDadosUsuario(null);
      return { success: true };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  }, []);

  const valor = useMemo(
    () => ({
      user: usuario,
      userInfo: dadosUsuario,
      isLogged: dadosUsuario !== null,
      loading: carregando,
      signIn: entrar,
      signOut: sair,
    }),
    [usuario, dadosUsuario, carregando, entrar, sair]
  );

  return (
    <ContextoAutenticacao.Provider value={valor}>{children}</ContextoAutenticacao.Provider>
  );
}

export function useAutenticacao() {
  const contexto = useContext(ContextoAutenticacao);
  if (!contexto) {
    throw new Error("useAutenticacao deve ser usado dentro de ProvedorAutenticacao");
  }
  return contexto;
}

export const AuthProvider = ProvedorAutenticacao;
export const useAuth = useAutenticacao;
