import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Animated,
  Easing,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect, useNavigation } from "@react-navigation/native";
import * as Location from "expo-location";
import { useFonts } from "expo-font";

import { kapipassApi, dbApi } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import { useAppAlert } from "../components/AppAlert";
import SectionHeader from "../components/SectionHeader";
import Button from "../components/Button";
import PressableScale from "../components/PressableScale";
import StampCard, { KAPIPASS_STAMP } from "../components/StampCard";
import AchievementCard from "../components/AchievementCard";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

function distancia(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export default function KapiPassScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const { showAlert } = useAppAlert();

  const [passaporte, setPassaporte] = useState(null);
  const [carimbos, setCarimbos] = useState([]);
  const [conquistas, setConquistas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [checkingIn, setCheckingIn] = useState(false);

  // Fonte Azonix apenas para o título do KapiPass (não afeta a Home)
  const [brandFontLoaded] = useFonts({
    Azonix: require("../assets/fonts/Azonix.otf"),
  });

  // Animação da capivara no título (balanço + leve rotação)
  const capyAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(capyAnim, {
          toValue: 1,
          duration: 1100,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(capyAnim, {
          toValue: 0,
          duration: 1100,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [capyAnim]);

  const capyTranslateY = capyAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -6],
  });
  const capyRotate = capyAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["-6deg", "6deg"],
  });

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const [pass, cars, conqs] = await Promise.all([
      kapipassApi.getPassaporte(),
      kapipassApi.listCarimbos(userInfo.id),
      kapipassApi.listConquistas(userInfo.id),
    ]);
    if (!pass.error) setPassaporte(pass.data);
    if (!cars.error) setCarimbos(cars.data || []);
    if (!conqs.error) setConquistas(conqs.data || []);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const fazerCheckin = useCallback(async () => {
    try {
      setCheckingIn(true);
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        showAlert({
          icon: "location-outline",
          iconColor: colors.accent,
          title: "Localização necessária",
          message: "Precisamos da sua localização para validar o check-in no ponto turístico.",
          buttons: [{ text: "OK" }],
        });
        return;
      }

      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      const { latitude, longitude } = loc.coords;

      const { data: pontos, error } = await dbApi.listPontos();
      if (error || !pontos?.length) {
        showAlert({
          icon: "alert-circle-outline",
          iconColor: colors.primary,
          title: "Erro",
          message: error?.message || "Não foi possível carregar os pontos turísticos.",
          buttons: [{ text: "OK" }],
        });
        return;
      }

      const comCoord = pontos.filter((p) => p.latitude != null && p.longitude != null);
      if (!comCoord.length) {
        showAlert({
          icon: "alert-circle-outline",
          iconColor: colors.primary,
          title: "Sem pontos próximos",
          message: "Nenhum ponto turístico com localização cadastrada foi encontrado.",
          buttons: [{ text: "OK" }],
        });
        return;
      }

      let maisProximo = comCoord[0];
      let menorDist = distancia(latitude, longitude, maisProximo.latitude, maisProximo.longitude);
      for (const p of comCoord) {
        const d = distancia(latitude, longitude, p.latitude, p.longitude);
        if (d < menorDist) {
          menorDist = d;
          maisProximo = p;
        }
      }

      const res = await kapipassApi.checkin(maisProximo.id, latitude, longitude);
      if (res.error) {
        showAlert({
          icon: "walk-outline",
          iconColor: colors.primary,
          title: "Check-in não realizado",
          message: res.error.message,
          buttons: [{ text: "Entendi" }],
        });
        return;
      }

      const r = res.data;
      const partes = [r.mensagem];
      if (r.xp_ganho > 0) partes.push(`+${r.xp_ganho} XP`);
      if (r.novo_carimbo) partes.push(`Novo carimbo: ${r.novo_carimbo.nome}`);
      if (r.novas_conquistas?.length) {
        partes.push(`Conquista: ${r.novas_conquistas.map((c) => c.nome).join(", ")}`);
      }
      const ganhouRecompensa = r.novo_carimbo || r.novas_conquistas?.length;
      showAlert({
        image: ganhouRecompensa ? KAPIPASS_STAMP : undefined,
        icon: ganhouRecompensa ? undefined : "checkmark-circle",
        iconColor: colors.accent,
        title: maisProximo.nome,
        message: partes.join("\n"),
        buttons: [{ text: "Boa!" }],
      });
      load();
    } catch (e) {
      showAlert({
        icon: "alert-circle-outline",
        iconColor: colors.primary,
        title: "Erro no check-in",
        message: e?.message || "Não foi possível concluir o check-in.",
        buttons: [{ text: "OK" }],
      });
    } finally {
      setCheckingIn(false);
    }
  }, [load, showAlert]);

  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={[styles.flex, styles.center]} edges={["top"]}>
          <ActivityIndicator size="large" color={colors.accent} />
        </SafeAreaView>
      </LinearGradient>
    );
  }

  const nome = passaporte?.usuario?.nome || userInfo?.nome || "Viajante";
  const inicial = nome.trim().charAt(0).toUpperCase();
  const progressoNivel = passaporte?.xp?.progresso_nivel || 0;
  const carimbosPreview = carimbos.slice(0, 3);
  const conquistasPreview = conquistas.slice(0, 3);

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <ScrollView
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                load();
              }}
              tintColor={colors.accent}
            />
          }
        >
          <View style={styles.header}>
            <View style={styles.heroTitleRow}>
              <View style={styles.heroIconWrap}>
                <Ionicons name="compass" size={22} color={colors.accent} />
              </View>
              <Text
                style={[
                  styles.heroTitle,
                  brandFontLoaded && {
                    fontFamily: "Azonix",
                    fontWeight: "normal",
                    letterSpacing: 1.5,
                  },
                ]}
              >
                Kapi
                <Text
                  style={[
                    styles.heroTitleAccent,
                    brandFontLoaded && { fontFamily: "Azonix", fontWeight: "normal" },
                  ]}
                >
                  Pass
                </Text>
              </Text>
              <Animated.Image
                source={KAPIPASS_STAMP}
                style={[
                  styles.heroCapy,
                  { transform: [{ translateY: capyTranslateY }, { rotate: capyRotate }] },
                ]}
                resizeMode="cover"
              />
            </View>
            <Text style={styles.heroSubtitle}>Seu passaporte turístico gamificado</Text>
          </View>

          {/* Cartão do passaporte */}
          <LinearGradient {...gradients.redDiagonal} style={[styles.passport, shadows.elevated]}>
            <View style={styles.passportTop}>
              <View style={styles.avatar}>
                <Text style={styles.avatarText}>{inicial}</Text>
              </View>
              <View style={styles.passportInfo}>
                <Text style={styles.passportName} numberOfLines={1}>
                  {nome}
                </Text>
                <View style={styles.levelBadge}>
                  <Ionicons name="star" size={12} color={colors.accent} />
                  <Text style={styles.levelText}>
                    Nível {passaporte?.nivel?.atual} · {passaporte?.nivel?.nome}
                  </Text>
                </View>
              </View>
            </View>

            <View style={styles.xpRow}>
              <Text style={styles.xpLabel}>{passaporte?.xp?.total || 0} XP</Text>
              {passaporte?.nivel?.proximo_nome ? (
                <Text style={styles.xpNext}>
                  Próximo: {passaporte.nivel.proximo_nome} ({passaporte?.xp?.proximo_nivel} XP)
                </Text>
              ) : (
                <Text style={styles.xpNext}>Nível máximo!</Text>
              )}
            </View>
            <View style={styles.progressTrack}>
              <View style={[styles.progressFill, { width: `${progressoNivel}%` }]} />
            </View>
          </LinearGradient>

          {/* Estatísticas */}
          <View style={styles.statsGrid}>
            <StatCard
              icon="location"
              valor={passaporte?.locais_visitados || 0}
              label="Locais visitados"
            />
            <StatCard
              icon="ribbon"
              valor={`${passaporte?.carimbos?.obtidos || 0}/${passaporte?.carimbos?.total || 0}`}
              label="Carimbos"
            />
            <StatCard
              icon="trophy"
              valor={`${passaporte?.conquistas?.obtidas || 0}/${passaporte?.conquistas?.total || 0}`}
              label="Conquistas"
            />
            <StatCard
              icon="trending-up"
              valor={`${passaporte?.progresso_geral || 0}%`}
              label="Progresso geral"
            />
          </View>

          {/* Check-in */}
          <View style={styles.section}>
            <Button icon="location" onPress={fazerCheckin} loading={checkingIn} fullWidth>
              Fazer check-in agora
            </Button>
            <Text style={styles.checkinHint}>
              Aproxime-se de um ponto turístico para coletar o carimbo e ganhar XP.
            </Text>
          </View>

          {/* Acesso rápido */}
          <View style={styles.section}>
            <SectionHeader title="Explore" />
            <View style={styles.menuGrid}>
              <MenuItem icon="ribbon" label="Carimbos" color="#f5b301" onPress={() => navigation.navigate("Carimbos")} />
              <MenuItem icon="trophy" label="Conquistas" color="#f7a000" onPress={() => navigation.navigate("Conquistas")} />
              <MenuItem icon="albums" label="Coleções" color="#4a9eff" onPress={() => navigation.navigate("Colecoes")} />
              <MenuItem icon="flag" label="Missões" color="#c83349" onPress={() => navigation.navigate("Missoes")} />
              <MenuItem icon="leaf" label="EcoPass" color="#3ec97a" onPress={() => navigation.navigate("EcoPass")} />
              <MenuItem icon="podium" label="Ranking" color="#9b6dff" onPress={() => navigation.navigate("Ranking")} />
              <MenuItem icon="journal" label="Diário" color="#ff8a5c" onPress={() => navigation.navigate("Diario")} />
              <MenuItem icon="map" label="Tesouros" color="#19c2c2" onPress={() => navigation.navigate("Tesouros")} />
            </View>
          </View>

          {/* Carimbos */}
          <View style={styles.section}>
            <SectionHeader
              title="Meus Carimbos"
              action={
                <Ionicons
                  name="chevron-forward"
                  size={22}
                  color={colors.accent}
                  onPress={() => navigation.navigate("Carimbos")}
                />
              }
            />
            <View style={styles.stampRow}>
              {carimbosPreview.map((c) => (
                <View key={c.id} style={styles.stampCol}>
                  <StampCard carimbo={c} onPress={() => navigation.navigate("Carimbos")} />
                </View>
              ))}
            </View>
          </View>

          {/* Conquistas */}
          <View style={styles.section}>
            <SectionHeader
              title="Conquistas"
              action={
                <Ionicons
                  name="chevron-forward"
                  size={22}
                  color={colors.accent}
                  onPress={() => navigation.navigate("Conquistas")}
                />
              }
            />
            <View style={styles.conqList}>
              {conquistasPreview.map((c) => (
                <AchievementCard key={c.id} conquista={c} />
              ))}
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

function StatCard({ icon, valor, label }) {
  return (
    <View style={styles.statCard}>
      <Ionicons name={icon} size={22} color={colors.accent} />
      <Text style={styles.statValor}>{valor}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function MenuItem({ icon, label, color = colors.accent, onPress }) {
  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={label}
      contentStyle={styles.menuItem}
    >
      <View
        style={[
          styles.menuIconWrap,
          { backgroundColor: `${color}1f`, borderColor: `${color}66` },
        ]}
      >
        <Ionicons name={icon} size={22} color={color} />
      </View>
      <Text style={styles.menuLabel} numberOfLines={1}>
        {label}
      </Text>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </PressableScale>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { alignItems: "center", justifyContent: "center" },
  content: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  header: {
    marginBottom: spacing.sm,
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
    fontSize: 24,
  },
  heroTitleAccent: {
    color: colors.accent,
  },
  heroCapy: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginLeft: spacing.xxs,
    borderWidth: 1.5,
    borderColor: colors.accent,
  },
  heroSubtitle: {
    ...typography.body,
    marginTop: spacing.xs,
    lineHeight: 20,
    marginLeft: 36 + spacing.xs,
  },
  passport: {
    borderRadius: radius.lg + 4,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  passportTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "rgba(255,255,255,0.18)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.35)",
  },
  avatarText: {
    ...typography.hero,
    fontSize: 26,
  },
  passportInfo: {
    flex: 1,
  },
  passportName: {
    ...typography.title,
    color: colors.text,
  },
  levelBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 4,
    alignSelf: "flex-start",
    backgroundColor: "rgba(0,0,0,0.25)",
    paddingVertical: 3,
    paddingHorizontal: spacing.xs,
    borderRadius: radius.round,
  },
  levelText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: "600",
  },
  xpRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    marginTop: spacing.md,
  },
  xpLabel: {
    ...typography.subtitle,
    color: colors.text,
  },
  xpNext: {
    ...typography.caption,
    color: "rgba(255,255,255,0.85)",
  },
  progressTrack: {
    height: 10,
    borderRadius: 5,
    backgroundColor: "rgba(0,0,0,0.3)",
    overflow: "hidden",
    marginTop: spacing.xs,
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 5,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  statCard: {
    flexGrow: 1,
    flexBasis: "47%",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
    alignItems: "center",
    gap: 4,
  },
  statValor: {
    ...typography.title,
    color: colors.text,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
  },
  section: {
    marginBottom: spacing.lg,
  },
  menuGrid: {
    marginTop: spacing.sm,
    gap: spacing.sm,
  },
  menuItem: {
    width: "100%",
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.cardBg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  menuIconWrap: {
    width: 46,
    height: 46,
    borderRadius: radius.md,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  menuLabel: {
    ...typography.subtitle,
    fontSize: 15,
    color: colors.text,
    flex: 1,
  },
  checkinHint: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: spacing.xs,
  },
  stampRow: {
    flexDirection: "row",
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  stampCol: {
    flex: 1,
  },
  conqList: {
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
});
