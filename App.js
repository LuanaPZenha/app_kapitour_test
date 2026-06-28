import React, { useEffect, useCallback, useRef, useState } from "react";
import * as NavigationBar from "expo-navigation-bar";
import * as SystemUI from "expo-system-ui";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { AccessibilityProvider } from "./src/accessibility/AccessibilityContext";
import { useAccessibility } from "./src/accessibility/AccessibilityContext";
import { AppAlertProvider } from "./components/AppAlert";
import FloatingAccessibilityButton from "./src/accessibility/FloatingAccessibilityButton";
import { AppDrawerProvider, AppFloatingMenuButton, getActiveRouteName } from "./components/AppDrawerMenu";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StyleSheet, View, ActivityIndicator } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { dbApi } from "./lib/api";
import { useAuth, AuthProvider } from "./hooks/useAuth";

import Home from "./Screens/Home";
import Login from "./Screens/Login";
import Rotas from "./Screens/Rotas";
import PontosTuristicos from "./Screens/PontosTuristicos";
import Contato from "./Screens/Contato";
import Mapa from "./Screens/Mapa";
import Cadastro from "./Screens/Cadastro";
import AreaUsuario from "./Screens/AreaUsuario";
import Cupons from "./Screens/Cupons";
import LeitorQR from "./Screens/LeitorQR";
import WeatherScreen from "./Screens/WeatherScreen";
import KapiPassScreen from "./Screens/KapiPassScreen";
import CarimbosScreen from "./Screens/CarimbosScreen";
import ConquistasScreen from "./Screens/ConquistasScreen";
import MissoesScreen from "./Screens/MissoesScreen";
import RankingScreen from "./Screens/RankingScreen";
import ColecoesScreen from "./Screens/ColecoesScreen";
import EcoPassScreen from "./Screens/EcoPassScreen";
import DiarioScreen from "./Screens/DiarioScreen";
import TesourosScreen from "./Screens/TesourosScreen";

const Stack = createNativeStackNavigator();

const AppThemeBase = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: "#0f142c",
    card: "#0f142c",
  },
};

function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{ headerShown: false, animation: "slide_from_right" }}
      sceneContainerStyle={{ backgroundColor: "#0f142c" }}
    >
      <Stack.Screen name="Login" component={Login} />
      <Stack.Screen name="Cadastro" component={Cadastro} />
    </Stack.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator
      initialRouteName="Inicio"
      screenOptions={{ headerShown: false, animation: "slide_from_right" }}
      sceneContainerStyle={{ backgroundColor: "#0f142c" }}
    >
      <Stack.Screen name="Inicio" component={Home} />
      <Stack.Screen name="KapiPass" component={KapiPassScreen} />
      <Stack.Screen name="Rotas" component={Rotas} />
      <Stack.Screen name="Pontos" component={PontosTuristicos} />
      <Stack.Screen name="Perfil" component={AreaUsuario} />
      <Stack.Screen name="LeitorQR" component={LeitorQR} />
      <Stack.Screen name="Contato" component={Contato} />
      <Stack.Screen name="Clima" component={WeatherScreen} />
      <Stack.Screen name="Mapa" component={Mapa} />
      <Stack.Screen name="Cupons" component={Cupons} />
      <Stack.Screen name="Carimbos" component={CarimbosScreen} />
      <Stack.Screen name="Conquistas" component={ConquistasScreen} />
      <Stack.Screen name="Missoes" component={MissoesScreen} />
      <Stack.Screen name="Ranking" component={RankingScreen} />
      <Stack.Screen name="Colecoes" component={ColecoesScreen} />
      <Stack.Screen name="EcoPass" component={EcoPassScreen} />
      <Stack.Screen name="Diario" component={DiarioScreen} />
      <Stack.Screen name="Tesouros" component={TesourosScreen} />
    </Stack.Navigator>
  );
}

function NavigationContent() {
  const { isLogged, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#c83349" />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }} sceneContainerStyle={{ backgroundColor: "#0f142c" }}>
      {isLogged ? (
        <Stack.Screen name="Main" component={MainStack} />
      ) : (
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  const { state } = useAccessibility();
  const navigationRef = useRef(null);
  const [activeRoute, setActiveRoute] = useState(null);

  const syncActiveRoute = useCallback(() => {
    const rootState = navigationRef.current?.getRootState?.();
    if (rootState) {
      setActiveRoute(getActiveRouteName(rootState));
    }
  }, []);

  useEffect(() => {
    const hideNavigationBar = async () => {
      try {
        await SystemUI.setBackgroundColorAsync("black");
        await NavigationBar.setVisibilityAsync("hidden");
      } catch (error) {
        console.warn("Erro ao esconder NavigationBar:", error);
      }
    };
    hideNavigationBar();
  }, []);

  useEffect(() => {
    const prefetch = async () => {
      try {
        const cat = await dbApi.listCategorias();
        if (!cat.error && cat.data) {
          await AsyncStorage.setItem(
            "cache:categorias",
            JSON.stringify({ ts: Date.now(), data: cat.data })
          );
        }
      } catch {}
      try {
        const pts = await dbApi.listPontos();
        if (!pts.error && pts.data) {
          await AsyncStorage.setItem(
            "cache:pontos:all",
            JSON.stringify({ ts: Date.now(), data: pts.data })
          );
        }
      } catch {}
    };
    prefetch();
  }, []);

  return (
    <AuthProvider>
      <AccessibilityProvider>
        <AppAlertProvider>
          <SafeAreaProvider>
            <NavigationContainer
              ref={navigationRef}
              onReady={syncActiveRoute}
              onStateChange={syncActiveRoute}
              theme={{
                ...AppThemeBase,
                colors: {
                  ...AppThemeBase.colors,
                  background: state?.darkMode ? "#0f142c" : "#ffffff",
                  card: state?.darkMode ? "#0f142c" : "#ffffff",
                },
              }}
            >
              <AppDrawerProvider activeRoute={activeRoute}>
                <StatusBar hidden />
                <NavigationContent />
                <AppFloatingMenuButton />
                <FloatingAccessibilityButton />
              </AppDrawerProvider>
            </NavigationContainer>
          </SafeAreaProvider>
        </AppAlertProvider>
      </AccessibilityProvider>
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#fff",
  },
});
