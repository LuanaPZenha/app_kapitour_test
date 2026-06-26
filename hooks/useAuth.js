import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { apiAutenticacao, apiTurismo } from "../lib/api";

const ContextoAutenticacao = createContext(null);

export function ProvedorAutenticacao({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [dadosUsuario, setDadosUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  const carregarDadosUsuario = useCallback(async (authId) => {
    const { data, error } = await apiTurismo.buscarUsuarioPorAuthId(authId);
    if (error) {
      console.log("Erro ao buscar usuário:", error);
      return null;
    }
    setDadosUsuario(data);
    return data;
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await apiAutenticacao.obterSessao();
        if (data?.session?.user) {
          setUsuario(data.session.user);
          await carregarDadosUsuario(data.session.user.id);
        } else {
          setUsuario(null);
          setDadosUsuario(null);
        }
      } finally {
        setCarregando(false);
      }
    })();
  }, [carregarDadosUsuario]);

  const entrar = async (email, senha) => {
    try {
      const { data, error } = await apiAutenticacao.entrar(email, senha);
      if (error) throw new Error(error.message);

      const usuarioSessao = { id: data.user.auth_id, email: data.user.email };
      setUsuario(usuarioSessao);
      setDadosUsuario(data.user);
      return { success: true, user: usuarioSessao };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  };

  const sair = async () => {
    try {
      await apiAutenticacao.sair();
      setUsuario(null);
      setDadosUsuario(null);
      return { success: true };
    } catch (erro) {
      return { success: false, error: erro.message };
    }
  };

  const valor = {
    user: usuario,
    userInfo: dadosUsuario,
    isLogged: dadosUsuario !== null,
    loading: carregando,
    signIn: entrar,
    signOut: sair,
  };

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

// Compatibilidade com telas ainda não migradas
export const AuthProvider = ProvedorAutenticacao;
export const useAuth = useAutenticacao;
