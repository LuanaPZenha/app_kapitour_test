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
  Image,
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

function StatCard({ icon, valor, label }) {
  return (
    <View style={styles.statCard}>
      <Ionicons name={icon} size={17} color={colors.accent} />
      <Text style={styles.statValor} numberOfLines={1}>
        {valor}
      </Text>
      <Text style={styles.statLabel} numberOfLines={2}>
        {label}
      </Text>
    </View>
  );
}

function MenuItem({ icon, label, subtitle, color = colors.accent, onPress }) {
  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={label}
      contentStyle={styles.menuItem}
    >
      <View
        style={[
          styles.menuIconWrap,
          { backgroundColor: `${color}1a`, borderColor: `${color}55` },
        ]}
      >
        <Ionicons name={icon} size={20} color={color} />
      </View>
      <View style={styles.menuTextWrap}>
        <Text style={styles.menuLabel}>{label}</Text>
        {subtitle ? <Text style={styles.menuSubtitle}>{subtitle}</Text> : null}
      </View>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </PressableScale>
  );
}

function SectionBlock({ title, subtitle, onSeeAll, children, empty }) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <View style={styles.sectionTitleWrap}>
          <Text style={styles.sectionTitle}>{title}</Text>
          {subtitle ? <Text style={styles.sectionSubtitle}>{subtitle}</Text> : null}
        </View>
        {onSeeAll ? (
          <PressableScale
            onPress={onSeeAll}
            accessibilityLabel={`Ver todos: ${title}`}
            contentStyle={styles.seeAllBtn}
          >
            <Text style={styles.seeAllText}>Ver todos</Text>
            <Ionicons name="chevron-forward" size={14} color={colors.accent} />
          </PressableScale>
        ) : null}
      </View>
      {empty ? (
        <View style={styles.emptyBlock}>
          <View style={styles.emptyIconWrap}>
            <Ionicons name={empty.icon} size={26} color={colors.accent} />
          </View>
          <Text style={styles.emptyText}>{empty.text}</Text>
        </View>
      ) : (
        children
      )}
    </View>
  );
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

  const [brandFontLoaded] = useFonts({
    Azonix: require("../assets/fonts/Azonix.otf"),
  });

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
          {/* Hero */}
          <View style={styles.hero}>
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
            <Text style={styles.heroSubtitle}>
              Seu passaporte turístico gamificado em Maricá
            </Text>
          </View>

          {/* Cartão do passaporte */}
          <View style={styles.passportCard}>
            <LinearGradient
              colors={["rgba(200,51,73,0.32)", "rgba(26,26,46,0.97)"]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.passportBg}
            >
              <Text style={styles.passportEyebrow}>PASSAPORTE DIGITAL</Text>

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
                <View style={styles.stampWrap}>
                  <Image source={KAPIPASS_STAMP} style={styles.stampImg} resizeMode="cover" />
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
          </View>

          {/* Estatísticas */}
          <View style={styles.statsRow}>
            <StatCard
              icon="location"
              valor={passaporte?.locais_visitados || 0}
              label="locais"
            />
            <StatCard
              icon="ribbon"
              valor={`${passaporte?.carimbos?.obtidos || 0}/${passaporte?.carimbos?.total || 0}`}
              label="carimbos"
            />
            <StatCard
              icon="trophy"
              valor={`${passaporte?.conquistas?.obtidas || 0}/${passaporte?.conquistas?.total || 0}`}
              label="conquistas"
            />
            <StatCard
              icon="trending-up"
              valor={`${passaporte?.progresso_geral || 0}%`}
              label="progresso"
            />
          </View>

          {/* Check-in */}
          <View style={styles.checkinCard}>
            <LinearGradient
              colors={["rgba(247,160,0,0.14)", "rgba(26,26,46,0.95)"]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.checkinBg}
            >
              <View style={styles.checkinIconWrap}>
                <Ionicons name="location" size={28} color={colors.accent} />
              </View>
              <Text style={styles.checkinTitle}>Check-in no ponto turístico</Text>
              <Text style={styles.checkinDesc}>
                Aproxime-se de um local para coletar carimbos, ganhar XP e desbloquear conquistas.
              </Text>
              <Button icon="navigate" onPress={fazerCheckin} loading={checkingIn} fullWidth>
                Fazer check-in agora
              </Button>
            </LinearGradient>
          </View>

          {/* Explore */}
          <Text style={styles.sectionTitle}>Explore</Text>
          <Text style={styles.sectionSubtitle}>Todas as áreas do seu passaporte gamificado</Text>
          <View style={[styles.menuCard, shadows.card]}>
            <MenuItem
              icon="ribbon"
              label="Carimbos"
              subtitle="Coleção de selos digitais"
              color="#f5b301"
              onPress={() => navigation.navigate("Carimbos")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="trophy"
              label="Conquistas"
              subtitle="Desafios e medalhas"
              color="#f7a000"
              onPress={() => navigation.navigate("Conquistas")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="albums"
              label="Coleções"
              subtitle="Álbuns temáticos"
              color="#4a9eff"
              onPress={() => navigation.navigate("Colecoes")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="flag"
              label="Missões"
              subtitle="Tarefas com recompensas"
              color={colors.primary}
              onPress={() => navigation.navigate("Missoes")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="leaf"
              label="EcoPass"
              subtitle="Turismo sustentável"
              color="#3ec97a"
              onPress={() => navigation.navigate("EcoPass")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="podium"
              label="Ranking"
              subtitle="Compare com outros viajantes"
              color="#9b6dff"
              onPress={() => navigation.navigate("Ranking")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="journal"
              label="Diário"
              subtitle="Registre sua jornada"
              color="#ff8a5c"
              onPress={() => navigation.navigate("Diario")}
            />
            <View style={styles.menuDivider} />
            <MenuItem
              icon="map"
              label="Tesouros"
              subtitle="Caça ao tesouro"
              color="#19c2c2"
              onPress={() => navigation.navigate("Tesouros")}
            />
          </View>

          {/* Carimbos preview */}
          <SectionBlock
            title="Meus Carimbos"
            subtitle={
              carimbos.length
                ? `${passaporte?.carimbos?.obtidos || 0} de ${passaporte?.carimbos?.total || carimbos.length} obtidos`
                : "Nenhum carimbo ainda"
            }
            onSeeAll={() => navigation.navigate("Carimbos")}
            empty={
              carimbosPreview.length === 0
                ? { icon: "ribbon-outline", text: "Faça check-in nos pontos para coletar carimbos." }
                : null
            }
          >
            <View style={styles.stampRow}>
              {carimbosPreview.map((c) => (
                <View key={c.id} style={styles.stampCol}>
                  <StampCard carimbo={c} onPress={() => navigation.navigate("Carimbos")} />
                </View>
              ))}
            </View>
          </SectionBlock>

          {/* Conquistas preview */}
          <SectionBlock
            title="Conquistas"
            subtitle={
              conquistas.length
                ? `${passaporte?.conquistas?.obtidas || 0} de ${passaporte?.conquistas?.total || conquistas.length} desbloqueadas`
                : "Nenhuma conquista ainda"
            }
            onSeeAll={() => navigation.navigate("Conquistas")}
            empty={
              conquistasPreview.length === 0
                ? { icon: "trophy-outline", text: "Explore Maricá para desbloquear conquistas." }
                : null
            }
          >
            <View style={styles.conqList}>
              {conquistasPreview.map((c) => (
                <AchievementCard key={c.id} conquista={c} />
              ))}
            </View>
          </SectionBlock>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
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
  hero: {
    marginBottom: spacing.lg,
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
  passportCard: {
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.35)",
    marginBottom: spacing.md,
    ...shadows.elevated,
  },
  passportBg: {
    padding: spacing.lg,
  },
  passportEyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 2,
    fontWeight: "700",
    marginBottom: spacing.sm,
  },
  passportTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: "rgba(255,255,255,0.12)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.3)",
  },
  avatarText: {
    ...typography.hero,
    fontSize: 22,
  },
  passportInfo: {
    flex: 1,
  },
  passportName: {
    ...typography.subtitle,
    fontSize: 18,
    color: colors.text,
  },
  levelBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 4,
    alignSelf: "flex-start",
    backgroundColor: "rgba(0,0,0,0.28)",
    paddingVertical: 3,
    paddingHorizontal: spacing.xs,
    borderRadius: radius.round,
  },
  levelText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: "600",
    fontSize: 11,
  },
  stampWrap: {
    width: 52,
    height: 52,
    borderRadius: 26,
    borderWidth: 2,
    borderColor: colors.accent,
    overflow: "hidden",
    backgroundColor: colors.cardBg,
  },
  stampImg: {
    width: "100%",
    height: "100%",
  },
  xpRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    marginTop: spacing.md,
    gap: spacing.sm,
  },
  xpLabel: {
    ...typography.subtitle,
    color: colors.text,
    fontSize: 18,
  },
  xpNext: {
    ...typography.caption,
    color: colors.textMuted,
    flex: 1,
    textAlign: "right",
    fontSize: 11,
  },
  progressTrack: {
    height: 8,
    borderRadius: 4,
    backgroundColor: "rgba(0,0,0,0.35)",
    overflow: "hidden",
    marginTop: spacing.sm,
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 4,
  },
  statsRow: {
    flexDirection: "row",
    gap: spacing.xs,
    marginBottom: spacing.lg,
  },
  statCard: {
    flex: 1,
    alignItems: "center",
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.xxs,
    gap: 2,
  },
  statValor: {
    ...typography.subtitle,
    fontSize: 14,
    color: colors.text,
    textAlign: "center",
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 9,
    textAlign: "center",
    textTransform: "lowercase",
  },
  checkinCard: {
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.3)",
    marginBottom: spacing.xl,
    ...shadows.card,
  },
  checkinBg: {
    alignItems: "center",
    padding: spacing.lg,
    gap: spacing.sm,
  },
  checkinIconWrap: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "rgba(247, 160, 0, 0.15)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xxs,
  },
  checkinTitle: {
    ...typography.subtitle,
    fontSize: 17,
    textAlign: "center",
  },
  checkinDesc: {
    ...typography.body,
    fontSize: 13,
    textAlign: "center",
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  sectionTitle: {
    ...typography.subtitle,
    fontSize: 16,
    marginBottom: spacing.xxs,
  },
  sectionSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  menuCard: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    marginBottom: spacing.xl,
    overflow: "hidden",
  },
  menuDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 68,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  menuIconWrap: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    borderWidth: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  menuTextWrap: {
    flex: 1,
    gap: 2,
  },
  menuLabel: {
    ...typography.subtitle,
    fontSize: 15,
  },
  menuSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 11,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  sectionTitleWrap: {
    flex: 1,
  },
  seeAllBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
    paddingTop: 2,
  },
  seeAllText: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: "600",
  },
  stampRow: {
    flexDirection: "row",
    gap: spacing.xs,
  },
  stampCol: {
    flex: 1,
  },
  conqList: {
    gap: spacing.sm,
  },
  emptyBlock: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    gap: spacing.sm,
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  emptyIconWrap: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  emptyText: {
    ...typography.body,
    fontSize: 13,
    color: colors.textSecondary,
    textAlign: "center",
    paddingHorizontal: spacing.lg,
  },
});
