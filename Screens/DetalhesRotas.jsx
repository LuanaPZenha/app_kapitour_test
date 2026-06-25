import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Linking,
  ActivityIndicator,
  Alert,
  Dimensions,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { dbApi } from "../lib/api";
import { LinearGradient } from "expo-linear-gradient";
import { salvarProgressoRota, carregarProgressoRota } from "../utils/progressManager";
import ProgressBar from "../components/ProgressBar";
import RatingStars from "../components/RatingStars";
import Card from "../components/Card";
import Button from "../components/Button";
import IconButton from "../components/IconButton";
import PontoListItem from "../components/PontoListItem";
import { submitRating, getAverageRating } from "../services/ratings";
import { colors } from "../theme/colors";
import { prefetchImages } from "../utils/images";
import { gradients } from "../theme/gradients";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { useAuth } from "../hooks/useAuth";

export default function DetalhesRota({ rota, voltar }) {
  const [pontos, setPontos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isStarted, setIsStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentRating, setCurrentRating] = useState(0);
  const [avgRating, setAvgRating] = useState(null);
  const windowHeight = Dimensions.get("window").height;
  const { userInfo } = useAuth();
  const cardMinHeight = Math.max(300, windowHeight * 0.45);

  useEffect(() => {
    const fetchPontosDaRota = async () => {
      const { data: relData, error: errorRel } = await dbApi.listRotaPontoByRota(rota.id);
      const relacionamentos = relData || [];

      if (errorRel) {
        console.error("Erro rota_ponto:", errorRel);
        setLoading(false);
        return;
      }

      const pontoIds = relacionamentos.map((rel) => rel.ponto_id);
      const { data: pontosData, error: errorPontos } = await dbApi.getPontosByIds(pontoIds);

      if (errorPontos) {
        console.error("Erro pontos_turisticos:", errorPontos);
      } else {
        const progressoSalvo = await carregarProgressoRota(rota.id);
        const orderedIds = relacionamentos.sort((a, b) => a.ordem - b.ordem).map((r) => r.ponto_id);
        const orderedPontos = orderedIds
          .map((id) => pontosData.find((p) => p.id === id))
          .filter(Boolean);

        const pontosComProgresso = orderedPontos.map((p) => {
          const pontoSalvo = progressoSalvo?.find((ps) => ps.id === p.id);
          return {
            ...p,
            completed: pontoSalvo ? pontoSalvo.completed : false,
            rating: pontoSalvo && typeof pontoSalvo.rating === "number" ? pontoSalvo.rating : null,
          };
        });

        setPontos(pontosComProgresso);
      }

      setLoading(false);
    };

    fetchPontosDaRota();
  }, [rota.id]);

  useEffect(() => {
    if (isStarted) {
      prefetchImages([
        pontos[currentIndex]?.url_img,
        pontos[currentIndex + 1]?.url_img,
      ]);
    }
  }, [isStarted, currentIndex, pontos]);

  useEffect(() => {
    const loadAvg = async () => {
      const id = pontos[currentIndex]?.id;
      if (isStarted && id) {
        try {
          const avg = await getAverageRating(id);
          setAvgRating(avg);
        } catch {
          setAvgRating(null);
        }
      } else {
        setAvgRating(null);
      }
    };
    loadAvg();
  }, [isStarted, currentIndex, pontos]);

  const progresso = pontos.length
    ? (pontos.filter((p) => p.completed).length / pontos.length) * 100
    : 0;

  const concluidos = pontos.filter((p) => p.completed).length;

  const iniciarRota = () => {
    const firstIncompleteIndex = pontos.findIndex((p) => !p.completed);
    setCurrentIndex(firstIncompleteIndex >= 0 ? firstIncompleteIndex : 0);
    setCurrentRating(0);
    setIsStarted(true);
  };

  const avancarPonto = async () => {
    if (currentRating === 0) {
      Alert.alert("Avaliação necessária", "Avalie este ponto antes de prosseguir.");
      return;
    }
    const updated = [...pontos];
    updated[currentIndex] = { ...updated[currentIndex], completed: true, rating: currentRating };
    setPontos(updated);
    await salvarProgressoRota(rota.id, updated);
    try {
      await submitRating(updated[currentIndex].id, userInfo?.id ?? null, currentRating);
    } catch {}
    const nextIndex = currentIndex + 1;
    if (nextIndex >= updated.length) {
      setIsStarted(false);
    } else {
      setCurrentIndex(nextIndex);
      setCurrentRating(0);
    }
  };

  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.center}>
          <ActivityIndicator size="large" color={colors.accent} />
          <Text style={styles.loadingText}>Carregando roteiro…</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
        >
          {/* Topo: voltar + progresso */}
          <View style={styles.topBar}>
            <IconButton
              name="arrow-back"
              onPress={voltar}
              accessibilityLabel="Voltar"
              color={colors.text}
              style={styles.backBtn}
            />
            {isStarted ? (
              <View style={styles.progressWrap}>
                <ProgressBar
                  percent={progresso}
                  badgeText={`Ponto ${currentIndex + 1} de ${pontos.length}`}
                />
              </View>
            ) : null}
          </View>

          {!isStarted ? (
            <>
              {/* Intro da rota */}
              <View style={styles.hero}>
                <Text style={styles.eyebrow}>ROTEIRO PLANEJADO</Text>
                <Text style={styles.heroTitle}>{rota.nome}</Text>
                {rota.descricao ? (
                  <Text style={styles.heroSubtitle}>{rota.descricao}</Text>
                ) : null}
              </View>

              <View style={styles.statsRow}>
                <View style={styles.statCard}>
                  <Ionicons name="location-outline" size={18} color={colors.accent} />
                  <Text style={styles.statValue}>{pontos.length}</Text>
                  <Text style={styles.statLabel}>paradas</Text>
                </View>
                <View style={styles.statCard}>
                  <Ionicons name="checkmark-circle-outline" size={18} color={colors.accent} />
                  <Text style={styles.statValue}>{concluidos}</Text>
                  <Text style={styles.statLabel}>concluídas</Text>
                </View>
                <View style={styles.statCard}>
                  <Ionicons name="trending-up-outline" size={18} color={colors.accent} />
                  <Text style={styles.statValue}>{Math.round(progresso)}%</Text>
                  <Text style={styles.statLabel}>progresso</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <LinearGradient
                  colors={["rgba(200,51,73,0.22)", "rgba(26,26,46,0.96)"]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.featureBg}
                >
                  <Ionicons name="navigate" size={32} color={colors.accent} />
                  <Text style={styles.featureTitle}>Pronto para explorar?</Text>
                  <Text style={styles.featureDesc}>
                    Siga o roteiro parada a parada, avalie cada local e acompanhe seu progresso.
                  </Text>
                  <Button icon="play" onPress={iniciarRota} fullWidth>
                    {concluidos > 0 ? "Continuar rota" : "Iniciar rota"}
                  </Button>
                </LinearGradient>
              </View>

              {/* Itinerário */}
              <Text style={styles.sectionTitle}>Itinerário</Text>
              {pontos.map((ponto, index) => (
                <PontoListItem
                  key={ponto.id}
                  ponto={ponto}
                  showOrder={index + 1}
                  completed={ponto.completed}
                  onPress={() => {}}
                />
              ))}
            </>
          ) : (
            <>
              <Text style={styles.activeLabel}>Parada atual</Text>
              <Card
                imageUrl={pontos[currentIndex]?.url_img}
                title={pontos[currentIndex]?.nome}
                description={pontos[currentIndex]?.descricao}
                showBack={currentIndex > 0}
                onBack={() => {
                  const prev = currentIndex - 1;
                  setCurrentIndex(prev);
                  setCurrentRating(pontos[prev]?.rating || 0);
                }}
                style={[styles.activeCard, shadows.elevated, { minHeight: cardMinHeight }]}
              >
                {avgRating !== null ? (
                  <View style={styles.avgRow}>
                    <Ionicons name="star" size={16} color={colors.accent} />
                    <Text style={styles.avgText}>Média: {avgRating}</Text>
                  </View>
                ) : null}

                <Text style={styles.ratingLabel}>Sua avaliação</Text>
                <RatingStars value={currentRating} onChange={setCurrentRating} />

                <View style={styles.actionCol}>
                  <Button
                    icon="navigate"
                    onPress={() =>
                      Linking.openURL(
                        `https://www.google.com/maps/dir/?api=1&destination=${pontos[currentIndex]?.latitude},${pontos[currentIndex]?.longitude}`
                      )
                    }
                    fullWidth
                  >
                    Abrir no GPS
                  </Button>
                  <Button icon="arrow-forward" onPress={avancarPonto} fullWidth>
                    {currentIndex + 1 >= pontos.length ? "Concluir rota" : "Próximo ponto"}
                  </Button>
                </View>
              </Card>
            </>
          )}
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { flex: 1 },
  content: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  loadingText: {
    ...typography.body,
    color: colors.textMuted,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.sm,
    paddingTop: spacing.sm,
    marginBottom: spacing.md,
  },
  backBtn: {
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  progressWrap: {
    flex: 1,
    paddingTop: spacing.xs,
  },
  hero: {
    marginBottom: spacing.md,
  },
  eyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 2,
    fontWeight: "700",
    marginBottom: spacing.xxs,
  },
  heroTitle: {
    ...typography.hero,
    fontSize: 24,
    lineHeight: 30,
  },
  heroSubtitle: {
    ...typography.body,
    marginTop: spacing.xs,
    lineHeight: 22,
  },
  statsRow: {
    flexDirection: "row",
    gap: spacing.sm,
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
    gap: 2,
  },
  statValue: {
    ...typography.subtitle,
    fontSize: 18,
    color: colors.text,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 10,
  },
  featureCard: {
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.35)",
    marginBottom: spacing.xl,
    ...shadows.card,
  },
  featureBg: {
    alignItems: "center",
    padding: spacing.lg,
    gap: spacing.sm,
  },
  featureTitle: {
    ...typography.subtitle,
    fontSize: 18,
    textAlign: "center",
  },
  featureDesc: {
    ...typography.body,
    fontSize: 13,
    textAlign: "center",
    marginBottom: spacing.xs,
  },
  sectionTitle: {
    ...typography.subtitle,
    marginBottom: spacing.sm,
  },
  activeLabel: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 1.2,
    fontWeight: "700",
    marginBottom: spacing.sm,
    textTransform: "uppercase",
  },
  activeCard: {
    width: "100%",
    marginBottom: spacing.md,
  },
  avgRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  avgText: {
    ...typography.caption,
    color: colors.textMuted,
  },
  ratingLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    fontWeight: "600",
  },
  actionCol: {
    gap: spacing.sm,
    marginTop: spacing.md,
    width: "100%",
  },
});
