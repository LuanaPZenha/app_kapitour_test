import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  Animated,
  Dimensions,
  Linking,
  StatusBar,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import Button from "../components/Button";
import Card from "../components/Card";
import LiveWeather from "../components/LiveWeather";
import WeatherTips from "../components/WeatherTips";
import SectionHeader from "../components/SectionHeader";
import PressableScale from "../components/PressableScale";
import { gradients } from "../theme/gradients";
import { spacing, layout, radius } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import ContainerImg from "../components/ContainerImg";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { useNavigation } from "@react-navigation/native";

const { width } = Dimensions.get("window");
const CARD_WIDTH = width * 0.6;
const PARTNER_CARD_HEIGHT = 280;
const PARTNER_LOGO_HEIGHT = 115;

const QUICK_ACTIONS = [
  { key: "mapa", label: "Mapa", icon: "map", route: "Mapa", tint: colors.primary },
  { key: "rotas", label: "Rotas", icon: "navigate", route: "Rotas", tint: colors.accent },
  { key: "pontos", label: "Pontos", icon: "location", route: "Pontos", tint: colors.primary },
  { key: "kapi", label: "KapiPass", icon: "ribbon", route: "KapiPass", tint: colors.accent },
];

const PATROCINADORES = [
  {
    id: "1",
    title: "AGM Maricá",
    description: "Parceria com a AGM Associação dos Guias de Turismo de Maricá.",
    imageUri: "https://github.com/Kapitour/Imgs-Padr-o/blob/main/home/agm.png?raw=true",
    buttonText: "Guias de Turismo",
    onPress: () =>
      Linking.openURL(
        "https://wa.me/5521971292030?text=Olá%20vim%20pela%20Kapitour%20e%20gostaria%20de%20contratar%20um%20guia%20de%20turismo!"
      ),
    style: "circle",
  },
  {
    id: "2",
    title: "Vassouras Tec",
    description: "Incubadora tecnológica da Univassouras.",
    imageUri: "https://github.com/Kapitour/Imgs-Padr-o/blob/main/VassourasT%C3%A9c.png?raw=true",
    buttonText: "Conheça Vassouras Tec",
    onPress: () => Linking.openURL("https://univassouras.edu.br/vassourastec/"),
    style: "incubadora",
  },
];

export default function Home() {
  const navigation = useNavigation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [weatherInfo, setWeatherInfo] = useState(null);

  const flatListRef = useRef(null);
  const scrollX = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => {
        const nextIndex = (prev + 1) % PATROCINADORES.length;
        flatListRef.current?.scrollToIndex({ index: nextIndex, animated: true });
        return nextIndex;
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const renderPatrocinador = ({ item, index }) => {
    const inputRange = [
      (index - 1) * CARD_WIDTH,
      index * CARD_WIDTH,
      (index + 1) * CARD_WIDTH,
    ];
    const scale = scrollX.interpolate({
      inputRange,
      outputRange: [0.92, 1, 0.92],
      extrapolate: "clamp",
    });

    return (
      <Animated.View
        style={{
          width: CARD_WIDTH,
          height: PARTNER_CARD_HEIGHT,
          marginHorizontal: spacing.xs,
          transform: [{ scale }],
        }}
      >
        <Card
          imageUrl={item.imageUri}
          imageFit="logo"
          logoShape={item.style === "circle" ? "circle" : "rounded"}
          imageHeight={PARTNER_LOGO_HEIGHT}
          title={item.title}
          description={item.description}
          style={{ height: "100%" }}
        >
          {item.buttonText ? (
            <Button icon="arrow-forward" onPress={item.onPress} fullWidth>
              {item.buttonText}
            </Button>
          ) : null}
        </Card>
      </Animated.View>
    );
  };

  return (
    <LinearGradient {...gradients.appBg} style={styles.safeArea}>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" backgroundColor="#c83349" />
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.topImageWrapper}>
            <ContainerImg />
          </View>

          <View style={styles.heroGreeting}>
            <View style={styles.heroTitleRow}>
              <View style={styles.heroIconWrap}>
                <Ionicons name="compass" size={22} color={colors.accent} />
              </View>
              <Text style={styles.heroTitle}>Bem-vindo a Maricá</Text>
            </View>
            <Text style={styles.heroSubtitle}>
              Explore praias, trilhas, gastronomia e muito mais pela cidade.
            </Text>
          </View>

          <View style={styles.content}>
            {/* Atalhos rápidos */}
            <View style={styles.quickRow}>
              {QUICK_ACTIONS.map((action) => (
                <PressableScale
                  key={action.key}
                  onPress={() => navigation.navigate(action.route)}
                  accessibilityLabel={action.label}
                  style={styles.quickTile}
                >
                  <View
                    style={[
                      styles.quickIconWrap,
                      { borderColor: `${action.tint}55` },
                    ]}
                  >
                    <Ionicons name={action.icon} size={24} color={action.tint} />
                  </View>
                  <Text style={styles.quickLabel} numberOfLines={1}>
                    {action.label}
                  </Text>
                </PressableScale>
              ))}
            </View>

            {/* KapiPass — card de destaque */}
            <View style={styles.section}>
              <SectionHeader
                title="Seu KapiPass"
                subtitle="Passaporte turístico gamificado: colete carimbos e suba de nível."
              />
              <View style={styles.featureCard}>
                <LinearGradient
                  colors={["rgba(200,51,73,0.28)", "rgba(26,26,46,0.96)"]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.featureBg}
                >
                  <Text style={styles.featureEyebrow}>PASSAPORTE DIGITAL</Text>
                  <View style={styles.kapiStampWrap}>
                    <Image
                      source={require("../assets/kapipass_carimbo.png")}
                      style={styles.kapiStamp}
                      resizeMode="cover"
                    />
                  </View>
                  <Text style={styles.kapiTitle}>Comece a explorar Maricá</Text>
                  <Text style={styles.kapiDesc}>
                    Faça check-in nos pontos turísticos, ganhe XP e desbloqueie conquistas.
                  </Text>
                  <View style={styles.kapiAction}>
                    <Button icon="trophy" onPress={() => navigation.navigate("KapiPass")} fullWidth>
                      Abrir KapiPass
                    </Button>
                  </View>
                </LinearGradient>
              </View>
            </View>

            {/* Previsão do tempo */}
            <View style={styles.section}>
              <SectionHeader
                title="Previsão do Tempo"
                subtitle="Clima de Maricá em tempo real, com a hora de Brasília."
              />
              <LiveWeather onInfo={setWeatherInfo} />
              <WeatherTips weatherInfo={weatherInfo} />
            </View>

            {/* Parceiros */}
            <View style={styles.section}>
              <SectionHeader
                title="Nossos Parceiros"
                subtitle="Quem acredita e apoia o turismo em Maricá."
              />
              <View style={styles.carouselContainer}>
                <Animated.FlatList
                  ref={flatListRef}
                  data={PATROCINADORES}
                  keyExtractor={(item) => item.id}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  pagingEnabled
                  snapToInterval={CARD_WIDTH + spacing.md}
                  decelerationRate="fast"
                  contentContainerStyle={{ paddingHorizontal: spacing.xs }}
                  renderItem={renderPatrocinador}
                  initialNumToRender={PATROCINADORES.length}
                  getItemLayout={(_, index) => ({
                    length: CARD_WIDTH + spacing.md,
                    offset: (CARD_WIDTH + spacing.md) * index,
                    index,
                  })}
                  onScrollToIndexFailed={(info) => {
                    const offset = (CARD_WIDTH + spacing.md) * info.index;
                    flatListRef.current?.scrollToOffset({ offset, animated: true });
                  }}
                  onMomentumScrollEnd={(e) => {
                    const idx = Math.round(
                      e.nativeEvent.contentOffset.x / (CARD_WIDTH + spacing.md)
                    );
                    setCurrentIndex(Math.max(0, Math.min(idx, PATROCINADORES.length - 1)));
                  }}
                  onScroll={Animated.event(
                    [{ nativeEvent: { contentOffset: { x: scrollX } } }],
                    { useNativeDriver: true }
                  )}
                />
              </View>
              <View style={styles.dotsRow}>
                {PATROCINADORES.map((_, i) => (
                  <View
                    key={i}
                    style={[styles.dot, i === currentIndex && styles.dotActive]}
                  />
                ))}
              </View>
            </View>
          </View>

          <LinearGradient {...gradients.appBg} style={styles.footer}>
            <Text style={styles.footerText}>© 2026 Kapitour · Maricá, RJ</Text>
          </LinearGradient>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingTop: spacing.lg,
    paddingHorizontal: layout.contentPadding,
    paddingBottom: spacing.xxl + spacing.lg,
  },
  topImageWrapper: {
    alignItems: "center",
    marginHorizontal: -layout.contentPadding,
  },
  heroGreeting: {
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  heroTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  heroIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(247, 160, 0, 0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  heroTitle: {
    ...typography.hero,
    fontSize: 22,
  },
  heroSubtitle: {
    ...typography.body,
    marginTop: spacing.xs,
    lineHeight: 20,
    marginLeft: 36 + spacing.xs,
  },
  content: {
    marginTop: spacing.md,
  },
  section: {
    marginBottom: spacing.xl,
  },
  // ── Atalhos rápidos ──
  quickRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.xl,
  },
  quickTile: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: spacing.xxs,
  },
  quickIconWrap: {
    width: 62,
    height: 62,
    borderRadius: 20,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
    ...shadows.soft,
  },
  quickLabel: {
    ...typography.caption,
    color: colors.text,
    marginTop: spacing.xs,
    textAlign: "center",
  },
  // ── Card de destaque KapiPass ──
  featureCard: {
    width: "100%",
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.35)",
    marginTop: spacing.sm,
    ...shadows.card,
  },
  featureBg: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  featureEyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 2,
    fontWeight: "700",
    marginBottom: spacing.xxs,
  },
  kapiStampWrap: {
    width: 124,
    height: 124,
    borderRadius: 62,
    padding: 4,
    backgroundColor: colors.cardBg,
    borderWidth: 2,
    borderColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
    ...shadows.accent,
  },
  kapiStamp: {
    width: "100%",
    height: "100%",
    borderRadius: 58,
  },
  kapiTitle: {
    ...typography.subtitle,
    fontSize: 20,
    color: colors.text,
    textAlign: "center",
  },
  kapiDesc: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
  },
  kapiAction: {
    width: "100%",
    marginTop: spacing.xs,
  },
  // ── Carrossel de parceiros ──
  carouselContainer: {
    height: PARTNER_CARD_HEIGHT + spacing.md,
    marginTop: spacing.sm,
  },
  dotsRow: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: colors.border,
  },
  dotActive: {
    width: 20,
    backgroundColor: colors.accent,
  },
  footer: {
    padding: layout.contentPadding,
    alignItems: "center",
    justifyContent: "center",
  },
  footerText: {
    ...typography.caption,
    color: "#fff",
  },
});
