import React, { useEffect, useState, useRef, useContext } from "react";
import * as NavigationBar from "expo-navigation-bar";
import * as SystemUI from "expo-system-ui";
import { speak } from "./src/accessibility/tts";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { AccessibilityProvider } from "./src/accessibility/AccessibilityContext";
import { useAccessibility } from "./src/accessibility/AccessibilityContext";
import { AppAlertProvider } from "./components/AppAlert";
import FloatingAccessibilityButton from "./src/accessibility/FloatingAccessibilityButton";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StyleSheet, View, ActivityIndicator } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { dbApi } from "./lib/api";
import Animated, { FadeIn, SlideInLeft, SlideInRight, Easing } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";
import { useAuth, AuthProvider } from "./hooks/useAuth";
import { ClerkProvider } from "@clerk/clerk-expo";
import * as SecureStore from "expo-secure-store";

// Telas
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

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const TabTransitionContext = React.createContext({ direction: 0, animate: false });

const AppThemeBase = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: "#0f142c",
    card: "#0f142c",
  },
};

function withTabTransition(Component) {
  return function Wrapped(props) {
    const { direction, animate } = useContext(TabTransitionContext);

    if (!animate) {
      return (
        <View style={{ flex: 1 }}>
          <Component {...props} />
        </View>
      );
    }

    return (
      <Animated.View
        style={{ flex: 1 }}
        entering={(direction >= 0 ? SlideInRight : SlideInLeft)
          .duration(200)
          .easing(Easing.out(Easing.cubic))}
      >
        <Component {...props} />
      </Animated.View>
    );
  };
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, animation: "slide_from_right" }} sceneContainerStyle={{ backgroundColor: "#0f142c" }}>
      <Stack.Screen name="Login" component={Login} />
      <Stack.Screen name="Cadastro" component={Cadastro} />
    </Stack.Navigator>
  );
}

// Stack principal com todas as telas
function MainStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, animation: "slide_from_right" }} sceneContainerStyle={{ backgroundColor: "#0f142c" }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
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

// Tabs principais
function MainTabs() {
  const { isLogged } = useAuth();
  const { state } = useAccessibility();
  const [direction, setDirection] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [animateTabs, setAnimateTabs] = useState(false);
  const TAB_NAMES = ["Início", "KapiPass", "Rotas", "Pontos Turísticos", "Perfil"];
  const handleTabPress = (nextIndex) => {
    setDirection(nextIndex > currentIndex ? 1 : -1);
    setCurrentIndex(nextIndex);
    setAnimateTabs(true);
    speak(`${TAB_NAMES[nextIndex]}`);
  };
  return (
    <TabTransitionContext.Provider value={{ direction, animate: animateTabs }}>
      <Tab.Navigator
        detachInactiveScreens={false}
        screenOptions={{
          headerShown: false,
          tabBarShowLabel: true,
          tabBarActiveTintColor: state?.darkMode ? "#ff4d6d" : "#c83349",
          tabBarInactiveTintColor: state?.darkMode ? "#eeeeee" : "#bbbbbb",
          tabBarLabelStyle: {
            fontSize: 12 * (state?.fontScale || 1),
            marginBottom: 5,
          },
          tabBarStyle: [
            styles.tabBar,
            { backgroundColor: state?.darkMode ? "#0f142c" : "white" },
          ],
          sceneContainerStyle: { backgroundColor: state?.darkMode ? "#0f142c" : "#ffffff" },
        }}
      >
        <Tab.Screen
          name="Início"
          component={withTabTransition(Home)}
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="home-outline" color={color} size={28} />
            ),
          }}
          listeners={{
            tabPress: () => handleTabPress(0),
          }}
        />
        <Tab.Screen
          name="KapiPass"
          component={withTabTransition(KapiPassScreen)}
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="ribbon-outline" color={color} size={28} />
            ),
          }}
          listeners={{
            tabPress: () => handleTabPress(1),
          }}
        />
        <Tab.Screen
          name="Rotas"
          component={withTabTransition(Rotas)}
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="navigate-outline" color={color} size={28} />
            ),
          }}
          listeners={{
            tabPress: () => handleTabPress(2),
          }}
        />
        <Tab.Screen
          name="Pontos"
          component={withTabTransition(PontosTuristicos)}
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="location-outline" color={color} size={28} />
            ),
          }}
          listeners={{
            tabPress: () => handleTabPress(3),
          }}
        />
        <Tab.Screen
          name="Perfil"
          component={withTabTransition(isLogged ? AreaUsuario : AuthStack)}
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="person-circle-outline" color={color} size={28} />
            ),
          }}
          listeners={{
            tabPress: () => handleTabPress(4),
          }}
        />
      </Tab.Navigator>
    </TabTransitionContext.Provider>
  );
}

// Stack Principal (sem Clerk)
function MainStackLegacy() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen name="LeitorQR" component={LeitorQR} />
      <Stack.Screen name="Contato" component={Contato} />
      <Stack.Screen name="Clima" component={WeatherScreen} />
      <Stack.Screen name="Mapa" component={Mapa} />
    </Stack.Navigator>
  );
}

// 🔥 TELA DE NAVEGAÇÃO CORRIGIDA (SUPABASE + CLERK)
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
        // Usuário logado - mostrar stack principal com tabs
        <Stack.Screen name="Main" component={MainStack} />
      ) : (
        // Usuário não logado - mostrar stack de autenticação
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  const { state } = useAccessibility();
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
          <NavigationContainer theme={{
            ...AppThemeBase,
            colors: {
              ...AppThemeBase.colors,
              background: state?.darkMode ? "#0f142c" : "#ffffff",
              card: state?.darkMode ? "#0f142c" : "#ffffff",
            },
          }}>
            <StatusBar hidden />
            <NavigationContent />
            <FloatingAccessibilityButton />
          </NavigationContainer>
        </SafeAreaProvider>
        </AppAlertProvider>
      </AccessibilityProvider>
    </AuthProvider>
  );
}

// ESTILOS CORRIGIDOS
const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#fff",
  },
  tabBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: 90,
    backgroundColor: "white",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: "hidden",
    elevation: 5,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -3 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    borderTopWidth: 0,
  },
});
