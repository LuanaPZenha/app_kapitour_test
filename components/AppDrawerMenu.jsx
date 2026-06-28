import React, { createContext, useContext, useState } from "react";
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Pressable,
  ScrollView,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../hooks/useAuth";
import { useAccessibility } from "../src/accessibility/AccessibilityContext";

const DrawerContext = createContext({ open: () => {}, close: () => {}, activeRoute: null });

export function useAppDrawer() {
  return useContext(DrawerContext);
}

const MENU_ITEMS = [
  { route: "Inicio", label: "Início", icon: "home-outline" },
  { route: "KapiPass", label: "KapiPass", icon: "ribbon-outline" },
  { route: "Rotas", label: "Rotas", icon: "navigate-outline" },
  { route: "Pontos", label: "Pontos Turísticos", icon: "location-outline" },
  { route: "Perfil", label: "Perfil", icon: "person-circle-outline" },
  { route: "Mapa", label: "Mapa", icon: "map-outline" },
  { route: "Clima", label: "Clima", icon: "partly-sunny-outline" },
  { route: "Cupons", label: "Cupons", icon: "ticket-outline" },
  { route: "Contato", label: "Contato", icon: "mail-outline" },
];

export function AppDrawerProvider({ children, activeRoute = null }) {
  const [visible, setVisible] = useState(false);
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { state } = useAccessibility();
  const dark = state?.darkMode;

  const open = () => setVisible(true);
  const close = () => setVisible(false);

  const goTo = (route) => {
    close();
    const rootState = navigation.getState?.();
    const rootRoutes = rootState?.routeNames ?? [];
    if (rootRoutes.includes(route)) {
      navigation.navigate(route);
      return;
    }
    navigation.navigate("Main", { screen: route });
  };

  return (
    <DrawerContext.Provider value={{ open, close, activeRoute }}>
      {children}
      <Modal visible={visible} transparent animationType="fade" onRequestClose={close}>
        <Pressable style={styles.overlay} onPress={close}>
          <Pressable
            style={[
              styles.drawer,
              {
                paddingTop: insets.top + 12,
                paddingBottom: insets.bottom + 12,
                backgroundColor: dark ? "#0f142c" : "#ffffff",
              },
            ]}
            onPress={(e) => e.stopPropagation()}
          >
            <View style={styles.drawerHeader}>
              <Text style={[styles.drawerTitle, dark && styles.drawerTitleDark]}>Kapitour</Text>
              <TouchableOpacity onPress={close} accessibilityLabel="Fechar menu">
                <Ionicons name="close" size={28} color={dark ? "#eee" : "#333"} />
              </TouchableOpacity>
            </View>
            <ScrollView showsVerticalScrollIndicator={false}>
              {MENU_ITEMS.map((item) => (
                <TouchableOpacity
                  key={item.route}
                  style={styles.menuItem}
                  onPress={() => goTo(item.route)}
                  accessibilityRole="button"
                >
                  <Ionicons name={item.icon} size={22} color="#c83349" />
                  <Text style={[styles.menuLabel, dark && styles.menuLabelDark]}>{item.label}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </DrawerContext.Provider>
  );
}

export function getActiveRouteName(state) {
  if (!state?.routes?.length) return null;
  const route = state.routes[state.index ?? 0];
  if (route.state) return getActiveRouteName(route.state);
  return route.name;
}

function MenuButton({ style, onPress, iconSize = 26 }) {
  return (
    <TouchableOpacity
      style={style}
      onPress={onPress}
      accessibilityLabel="Abrir menu"
      accessibilityRole="button"
      activeOpacity={0.85}
    >
      <Ionicons name="menu" size={iconSize} color="#fff" />
    </TouchableOpacity>
  );
}

/** Botão inline no header (ex.: Home / BrandLogo). */
export function AppMenuButtonInline() {
  const { open } = useAppDrawer();
  const { isLogged } = useAuth();

  if (!isLogged) return null;

  return (
    <MenuButton
      style={[styles.menuButton, styles.menuButtonInline, styles.menuButtonHeader]}
      onPress={open}
      iconSize={22}
    />
  );
}

/** Botão flutuante nas demais telas (oculto na Home). */
export function AppFloatingMenuButton() {
  const { open, activeRoute } = useAppDrawer();
  const insets = useSafeAreaInsets();
  const { isLogged } = useAuth();

  if (!isLogged || activeRoute === "Inicio") return null;

  return (
    <MenuButton
      style={[styles.menuButton, { top: insets.top + 8 }]}
      onPress={open}
    />
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    flexDirection: "row",
    backgroundColor: "rgba(0,0,0,0.45)",
  },
  drawer: {
    width: "78%",
    maxWidth: 320,
    height: "100%",
    paddingHorizontal: 20,
    elevation: 16,
    shadowColor: "#000",
    shadowOpacity: 0.25,
    shadowRadius: 12,
    shadowOffset: { width: 4, height: 0 },
  },
  drawerHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  drawerTitle: {
    fontSize: 22,
    fontWeight: "700",
    color: "#1a1a2e",
  },
  drawerTitleDark: {
    color: "#ffffff",
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "rgba(128,128,128,0.25)",
  },
  menuLabel: {
    fontSize: 16,
    color: "#1a1a2e",
    flex: 1,
  },
  menuLabelDark: {
    color: "#eeeeee",
  },
  menuButton: {
    position: "absolute",
    left: 16,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "rgba(200, 51, 73, 0.92)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 99998,
    elevation: 6,
    shadowColor: "#c83349",
    shadowOpacity: 0.35,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  menuButtonInline: {
    position: "relative",
    left: 0,
    top: 0,
    zIndex: 1,
    elevation: 4,
  },
  menuButtonHeader: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: "rgba(255, 255, 255, 0.14)",
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
});
