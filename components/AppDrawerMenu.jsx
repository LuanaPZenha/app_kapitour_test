import React, { createContext, useContext, useEffect, useState } from "react";
import {
  Modal,
  View,
  Text,
  StyleSheet,
  Pressable,
  ScrollView,
  Dimensions,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import Animated, {
  Easing,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withSpring,
  withTiming,
} from "react-native-reanimated";
import { useAuth } from "../hooks/useAuth";
import { useAccessibility } from "../src/accessibility/AccessibilityContext";
import PressableScale from "./PressableScale";
import { CompassIcon } from "./BrandLogo";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { spacing, radius } from "../theme/spacing";
import { shadows } from "../theme/shadows";
import { typography } from "../theme/typography";

const { width: SCREEN_WIDTH } = Dimensions.get("window");
const DRAWER_WIDTH = Math.min(SCREEN_WIDTH * 0.86, 340);

const DrawerContext = createContext({ open: () => {}, close: () => {}, activeRoute: null });

export function useAppDrawer() {
  return useContext(DrawerContext);
}

const MENU_SECTIONS = [
  {
    title: "Explorar",
    items: [
      { route: "Inicio", label: "Início", icon: "home-outline", tint: colors.primary },
      { route: "Mapa", label: "Mapa", icon: "map-outline", tint: colors.accent },
      { route: "Rotas", label: "Rotas", icon: "navigate-outline", tint: colors.primary },
      { route: "Pontos", label: "Pontos Turísticos", icon: "location-outline", tint: colors.accent },
      { route: "Clima", label: "Clima", icon: "partly-sunny-outline", tint: "#5eb3ff" },
    ],
  },
  {
    title: "KapiPass & Ofertas",
    items: [
      { route: "KapiPass", label: "KapiPass", icon: "ribbon-outline", tint: colors.accent },
      { route: "Cupons", label: "Cupons", icon: "ticket-outline", tint: colors.primary },
    ],
  },
  {
    title: "Conta",
    items: [
      { route: "Perfil", label: "Meu Perfil", icon: "person-circle-outline", tint: colors.accent },
      { route: "Contato", label: "Contato", icon: "mail-outline", tint: colors.primary },
    ],
  },
];

const SPRING_DRAWER = { damping: 24, stiffness: 260, mass: 0.85 };
const SPRING_ITEM = { damping: 18, stiffness: 220, mass: 0.6 };

function MenuItemRow({ item, index, active, onPress, menuOpen, dark }) {
  const opacity = useSharedValue(0);
  const translateX = useSharedValue(-20);

  useEffect(() => {
    if (menuOpen) {
      const delay = 90 + index * 42;
      opacity.value = withDelay(delay, withTiming(1, { duration: 320, easing: Easing.out(Easing.cubic) }));
      translateX.value = withDelay(delay, withSpring(0, SPRING_ITEM));
    } else {
      opacity.value = 0;
      translateX.value = -20;
    }
  }, [menuOpen, index]);

  const animStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <Animated.View style={animStyle}>
      <PressableScale
        onPress={onPress}
        scaleTo={0.98}
        accessibilityLabel={item.label}
        contentStyle={[
          styles.menuItem,
          dark ? styles.menuItemDark : styles.menuItemLight,
          active && styles.menuItemActive,
        ]}
      >
        {active ? (
          <LinearGradient
            colors={gradients.cta.colors}
            start={gradients.cta.start}
            end={gradients.cta.end}
            style={styles.menuItemAccent}
          />
        ) : (
          <View style={[styles.menuItemAccent, { backgroundColor: item.tint, opacity: 0.85 }]} />
        )}
        <View style={[styles.menuIconWrap, { backgroundColor: `${item.tint}22` }]}>
          <Ionicons name={item.icon} size={20} color={active ? colors.text : item.tint} />
        </View>
        <Text
          style={[
            styles.menuLabel,
            dark ? styles.menuLabelDark : styles.menuLabelLight,
            active && styles.menuLabelActive,
          ]}
          numberOfLines={1}
        >
          {item.label}
        </Text>
        <Ionicons
          name="chevron-forward"
          size={16}
          color={active ? colors.accent : dark ? "rgba(255,255,255,0.35)" : "rgba(26,26,46,0.35)"}
        />
      </PressableScale>
    </Animated.View>
  );
}

function MenuTrigger({ onPress, variant = "floating", iconSize = 22 }) {
  const isHeader = variant === "header";

  return (
    <PressableScale
      onPress={onPress}
      scaleTo={0.92}
      accessibilityLabel="Abrir menu"
      hitSlop={10}
      contentStyle={[
        styles.menuTrigger,
        isHeader ? styles.menuTriggerHeader : styles.menuTriggerFloating,
        !isHeader && shadows.brand,
      ]}
    >
      {isHeader ? (
        <View style={styles.menuTriggerHeaderInner}>
          <Ionicons name="menu" size={iconSize} color={colors.text} />
        </View>
      ) : (
        <LinearGradient
          colors={gradients.cta.colors}
          start={gradients.cta.start}
          end={gradients.cta.end}
          style={styles.menuTriggerGradient}
        >
          <Ionicons name="menu" size={iconSize} color={colors.text} />
        </LinearGradient>
      )}
    </PressableScale>
  );
}

export function AppDrawerProvider({ children, activeRoute = null }) {
  const [visible, setVisible] = useState(false);
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { state } = useAccessibility();
  const { userInfo, signOut } = useAuth();
  const dark = state?.darkMode ?? true;

  const overlayOpacity = useSharedValue(0);
  const drawerX = useSharedValue(-DRAWER_WIDTH);

  const open = () => setVisible(true);

  const finishClose = () => setVisible(false);

  const close = () => {
    overlayOpacity.value = withTiming(0, { duration: 240, easing: Easing.in(Easing.cubic) });
    drawerX.value = withTiming(
      -DRAWER_WIDTH,
      { duration: 280, easing: Easing.in(Easing.cubic) },
      (finished) => {
        if (finished) runOnJS(finishClose)();
      }
    );
  };

  useEffect(() => {
    if (visible) {
      drawerX.value = -DRAWER_WIDTH;
      overlayOpacity.value = 0;
      overlayOpacity.value = withTiming(1, { duration: 280, easing: Easing.out(Easing.cubic) });
      drawerX.value = withSpring(0, SPRING_DRAWER);
    }
  }, [visible]);

  const goTo = (route) => {
    close();
    setTimeout(() => {
      const rootState = navigation.getState?.();
      const rootRoutes = rootState?.routeNames ?? [];
      if (rootRoutes.includes(route)) {
        navigation.navigate(route);
        return;
      }
      navigation.navigate("Main", { screen: route });
    }, 220);
  };

  const handleSignOut = async () => {
    close();
    setTimeout(async () => {
      await signOut();
    }, 220);
  };

  const overlayStyle = useAnimatedStyle(() => ({
    opacity: overlayOpacity.value,
  }));

  const drawerStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: drawerX.value }],
  }));

  let itemIndex = 0;
  const displayName = userInfo?.nome?.split(" ")[0] || "Explorador";

  return (
    <DrawerContext.Provider value={{ open, close, activeRoute }}>
      {children}
      <Modal visible={visible} transparent animationType="none" onRequestClose={close} statusBarTranslucent>
        <View style={styles.modalRoot}>
          <Pressable style={StyleSheet.absoluteFill} onPress={close} accessibilityLabel="Fechar menu">
            <Animated.View style={[styles.overlay, overlayStyle]} />
          </Pressable>

          <Animated.View
            style={[
              styles.drawer,
              drawerStyle,
              shadows.elevated,
              { width: DRAWER_WIDTH, paddingBottom: insets.bottom + spacing.sm },
            ]}
          >
            <LinearGradient
              colors={dark ? ["#c83349", "#1a1a2e", "#0f142c"] : ["#c83349", "#e8e8f0", "#ffffff"]}
              locations={[0, 0.42, 1]}
              start={{ x: 0, y: 0 }}
              end={{ x: 0.3, y: 1 }}
              style={[styles.drawerHeader, { paddingTop: insets.top + spacing.sm }]}
            >
              <View style={styles.headerTopRow}>
                <View style={styles.brandRow}>
                  <View style={styles.compassWrap}>
                    <CompassIcon size={36} />
                  </View>
                  <View style={styles.brandText}>
                    <Text style={styles.brandTitle}>
                      Kapi<Text style={styles.brandAccent}>tour</Text>
                    </Text>
                    <Text style={styles.brandSubtitle}>Menu de navegação</Text>
                  </View>
                </View>
                <PressableScale
                  onPress={close}
                  scaleTo={0.9}
                  accessibilityLabel="Fechar menu"
                  contentStyle={styles.closeBtn}
                >
                  <Ionicons name="close" size={22} color={colors.text} />
                </PressableScale>
              </View>

              <View style={styles.userChip}>
                <LinearGradient
                  colors={["rgba(255,255,255,0.18)", "rgba(255,255,255,0.06)"]}
                  style={styles.userChipGradient}
                >
                  <View style={styles.userAvatar}>
                    <Text style={styles.userAvatarText}>{displayName.charAt(0).toUpperCase()}</Text>
                  </View>
                  <View style={styles.userInfo}>
                    <Text style={styles.userGreeting}>Olá, {displayName}</Text>
                    <Text style={styles.userHint}>Maricá te espera</Text>
                  </View>
                  <Ionicons name="sparkles-outline" size={18} color={colors.accent} />
                </LinearGradient>
              </View>
            </LinearGradient>

            <ScrollView
              style={[styles.menuScroll, dark ? styles.menuScrollDark : styles.menuScrollLight]}
              contentContainerStyle={styles.menuScrollContent}
              showsVerticalScrollIndicator={false}
            >
              {MENU_SECTIONS.map((section) => (
                <View key={section.title} style={styles.section}>
                  <Text style={[styles.sectionTitle, dark && styles.sectionTitleDark]}>
                    {section.title}
                  </Text>
                  {section.items.map((item) => {
                    const idx = itemIndex;
                    itemIndex += 1;
                    return (
                      <MenuItemRow
                        key={item.route}
                        item={item}
                        index={idx}
                        active={activeRoute === item.route}
                        menuOpen={visible}
                        dark={dark}
                        onPress={() => goTo(item.route)}
                      />
                    );
                  })}
                </View>
              ))}

              <PressableScale
                onPress={handleSignOut}
                scaleTo={0.98}
                accessibilityLabel="Sair da conta"
                contentStyle={[styles.logoutBtn, dark ? styles.logoutBtnDark : styles.logoutBtnLight]}
              >
                <Ionicons name="log-out-outline" size={20} color={colors.primary} />
                <Text style={styles.logoutText}>Sair da conta</Text>
              </PressableScale>
            </ScrollView>
          </Animated.View>
        </View>
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

export function AppMenuButtonInline() {
  const { open } = useAppDrawer();
  const { isLogged } = useAuth();

  if (!isLogged) return null;

  return <MenuTrigger onPress={open} variant="header" iconSize={20} />;
}

export function AppFloatingMenuButton() {
  const { open, activeRoute } = useAppDrawer();
  const insets = useSafeAreaInsets();
  const { isLogged } = useAuth();

  if (!isLogged || activeRoute === "Inicio") return null;

  return (
    <View style={[styles.floatingWrap, { top: insets.top + spacing.xs }]} pointerEvents="box-none">
      <MenuTrigger onPress={open} variant="floating" iconSize={22} />
    </View>
  );
}

const styles = StyleSheet.create({
  modalRoot: {
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.overlay,
  },
  drawer: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    overflow: "hidden",
    borderTopRightRadius: radius.lg + 4,
    borderBottomRightRadius: radius.lg + 4,
  },
  drawerHeader: {
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
  },
  headerTopRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: spacing.md,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
  },
  compassWrap: {
    ...shadows.soft,
  },
  brandText: {
    flex: 1,
  },
  brandTitle: {
    ...typography.subtitle,
    fontSize: 18,
    letterSpacing: 0.5,
  },
  brandAccent: {
    color: colors.accent,
  },
  brandSubtitle: {
    ...typography.caption,
    color: "rgba(255,255,255,0.72)",
    marginTop: 2,
  },
  closeBtn: {
    width: 36,
    height: 36,
    borderRadius: radius.round,
    backgroundColor: "rgba(255,255,255,0.14)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },
  userChip: {
    borderRadius: radius.md,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  userChipGradient: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.sm,
    gap: spacing.sm,
  },
  userAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(255,255,255,0.2)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1.5,
    borderColor: colors.accent,
  },
  userAvatarText: {
    ...typography.subtitle,
    fontSize: 17,
    color: colors.text,
  },
  userInfo: {
    flex: 1,
  },
  userGreeting: {
    ...typography.subtitle,
    fontSize: 15,
  },
  userHint: {
    ...typography.caption,
    color: "rgba(255,255,255,0.65)",
    marginTop: 1,
  },
  menuScroll: {
    flex: 1,
  },
  menuScrollDark: {
    backgroundColor: colors.bgDark,
  },
  menuScrollLight: {
    backgroundColor: "#f4f4f8",
  },
  menuScrollContent: {
    paddingHorizontal: spacing.md,
    paddingTop: spacing.md,
    paddingBottom: spacing.xl,
  },
  section: {
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.caption,
    fontSize: 11,
    letterSpacing: 1.2,
    textTransform: "uppercase",
    color: "rgba(26,26,46,0.45)",
    marginBottom: spacing.xs,
    marginLeft: spacing.xxs,
  },
  sectionTitleDark: {
    color: "rgba(255,255,255,0.4)",
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.sm,
    marginBottom: spacing.xs,
    borderRadius: radius.md,
    overflow: "hidden",
    borderWidth: 1,
  },
  menuItemDark: {
    backgroundColor: colors.cardBg,
    borderColor: colors.borderSubtle,
  },
  menuItemLight: {
    backgroundColor: "#ffffff",
    borderColor: "rgba(26,26,46,0.08)",
  },
  menuItemActive: {
    borderColor: "rgba(247,160,0,0.45)",
    backgroundColor: colors.surfaceElevated,
  },
  menuItemAccent: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    width: 3,
    borderTopLeftRadius: radius.md,
    borderBottomLeftRadius: radius.md,
  },
  menuIconWrap: {
    width: 36,
    height: 36,
    borderRadius: radius.sm + 2,
    alignItems: "center",
    justifyContent: "center",
  },
  menuLabel: {
    ...typography.subtitle,
    fontSize: 15,
    flex: 1,
  },
  menuLabelDark: {
    color: colors.text,
  },
  menuLabelLight: {
    color: colors.cardBg,
  },
  menuLabelActive: {
    color: colors.text,
  },
  logoutBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    marginTop: spacing.md,
    paddingVertical: spacing.sm + 2,
    borderRadius: radius.md,
    borderWidth: 1,
  },
  logoutBtnDark: {
    backgroundColor: "rgba(200,51,73,0.12)",
    borderColor: "rgba(200,51,73,0.35)",
  },
  logoutBtnLight: {
    backgroundColor: "rgba(200,51,73,0.08)",
    borderColor: "rgba(200,51,73,0.25)",
  },
  logoutText: {
    ...typography.button,
    color: colors.primary,
    fontSize: 14,
  },
  floatingWrap: {
    position: "absolute",
    left: spacing.md,
    zIndex: 99998,
  },
  menuTrigger: {
    overflow: "hidden",
  },
  menuTriggerFloating: {
    width: 46,
    height: 46,
    borderRadius: 23,
  },
  menuTriggerGradient: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 23,
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.22)",
  },
  menuTriggerHeader: {
    width: 38,
    height: 38,
    borderRadius: 19,
  },
  menuTriggerHeaderInner: {
    width: "100%",
    height: "100%",
    borderRadius: 19,
    backgroundColor: "rgba(255,255,255,0.14)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },
});
