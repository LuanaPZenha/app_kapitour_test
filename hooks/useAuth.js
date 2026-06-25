import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi, dbApi } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUserInfo = useCallback(async (authId) => {
    const { data, error } = await dbApi.getUserByAuthId(authId);
    if (error) {
      console.log("Erro ao buscar usuário:", error);
      return null;
    }
    setUserInfo(data);
    return data;
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await authApi.getSession();
        if (data?.session?.user) {
          setUser(data.session.user);
          await loadUserInfo(data.session.user.id);
        } else {
          setUser(null);
          setUserInfo(null);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [loadUserInfo]);

  const signIn = async (email, password) => {
    try {
      const { data, error } = await authApi.login(email, password);
      if (error) throw new Error(error.message);

      const sessionUser = { id: data.user.auth_id, email: data.user.email };
      setUser(sessionUser);
      setUserInfo(data.user);
      return { success: true, user: sessionUser };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const signInWithGoogle = async (idToken) => {
    try {
      const { data, error } = await authApi.googleLogin(idToken);
      if (error) throw new Error(error.message);

      const sessionUser = { id: data.user.auth_id, email: data.user.email };
      setUser(sessionUser);
      setUserInfo(data.user);
      return { success: true, user: sessionUser };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const signOut = async () => {
    try {
      await authApi.signOut();
      setUser(null);
      setUserInfo(null);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const value = {
    user,
    userInfo,
    isLogged: userInfo !== null,
    loading,
    signIn,
    signInWithGoogle,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
};
