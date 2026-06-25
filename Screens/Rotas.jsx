import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Image,
  RefreshControl,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { dbApi } from "../lib/api";
import DetalhesRota from "./DetalhesRotas";
import { useAuth } from "../hooks/useAuth";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { radius, spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { handleError } from "../utils/errors";
import PressableScale from "../components/PressableScale";
import IconButton from "../components/IconButton";
import { useAppAlert } from "../components/AppAlert";

// ──────────────────────────────────────────────
// RotaCard — layout horizontal profissional
// ──────────────────────────────────────────────
function RotaCard({ rota, isFavorito, onPress, onToggleFavorito }) {
  const paradas = rota.pontoCount ?? 0;

  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={`Rota ${rota.nome}`}
      accessibilityHint="Abre detalhes desta rota"
      contentStyle={[styles.card, shadows.card]}
    >
      {/* Thumbnail */}
      {rota.imagem ? (
        <Image
          source={{ uri: rota.imagem }}
          style={styles.thumb}
          resizeMode="cover"
          accessibilityIgnoresInvertColors
        />
      ) : (
        <View style={[styles.thumb, styles.thumbPlaceholder]}>
          <Ionicons name="map-outline" size={28} color={colors.accent} />
        </View>
      )}

      {/* Conteúdo */}
      <View style={styles.cardBody}>
        <Text style={styles.eyebrow}>ROTEIRO PLANEJADO</Text>
        <Text style={styles.cardTitle} numberOfLines={2}>
          {rota.nome}
        </Text>

        {rota.descricao ? (
          <Text style={styles.cardDesc} numberOfLines={2}>
            {rota.descricao}
          </Text>
        ) : null}

        <View style={styles.metaRow}>
          <View style={styles.metaItem}>
            <Ionicons name="location-outline" size={13} color={colors.accent} />
            <Text style={styles.metaText}>
              {paradas} {paradas === 1 ? "parada" : "paradas"}
            </Text>
          </View>
          {rota.categorias?.length > 0 ? (
            <View style={styles.metaItem}>
              <Ionicons name="pricetag-outline" size={13} color={colors.textSecondary} />
              <Text style={styles.metaText} numberOfLines={1}>
                {rota.categorias.slice(0, 2).join(" · ")}
              </Text>
            </View>
          ) : null}
        </View>

        {rota.categorias?.length > 0 ? (
          <View style={styles.tagsRow}>
            {rota.categorias.slice(0, 3).map((cat, i) => (
              <View key={`${cat}-${i}`} style={styles.tag}>
                <Text style={styles.tagText}>{cat}</Text>
              </View>
            ))}
          </View>
        ) : null}
      </View>

      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} style={styles.chevron} />

      <IconButton
        name={isFavorito ? "heart" : "heart-outline"}
        onPress={onToggleFavorito}
        accessibilityLabel={isFavorito ? "Remover dos favoritos" : "Adicionar aos favoritos"}
        color={isFavorito ? colors.primary : colors.textSecondary}
        style={styles.favoriteBtn}
      />
    </PressableScale>
  );
}

// ──────────────────────────────────────────────
// Cabeçalho da lista
// ──────────────────────────────────────────────
function ListHeader({ total }) {
  return (
    <View style={styles.hero}>
      <View style={styles.heroTitleRow}>
        <View style={styles.heroIconWrap}>
          <Ionicons name="navigate" size={22} color={colors.accent} />
        </View>
        <Text style={styles.heroTitle}>Rotas Turísticas</Text>
      </View>
      <Text style={styles.heroSubtitle}>
        Roteiros planejados para explorar o melhor de Maricá com organização e praticidade.
      </Text>

      {!total ? null : (
        <View style={styles.statsBanner}>
          <View style={styles.statsIconWrap}>
            <Ionicons name="trail-sign-outline" size={18} color={colors.accent} />
          </View>
          <Text style={styles.statsText}>
            {total} {total === 1 ? "roteiro disponível" : "roteiros disponíveis"} em Maricá
          </Text>
        </View>
      )}
    </View>
  );
}

// ──────────────────────────────────────────────
// Tela principal
// ──────────────────────────────────────────────
export default function Rotas() {
  const [rotas, setRotas] = useState([]);
  const [rotaSelecionada, setRotaSelecionada] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [favoritos, setFavoritos] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const { user } = useAuth();
  const { showAlert } = useAppAlert();

  const fetchUserInfo = useCallback(async () => {
    if (!user?.id) return;
    try {
      const { data } = await dbApi.getUserByAuthId(user.id);
      if (data) setUserInfo(data);
    } catch {}
  }, [user]);

  const fetchFavoritos = useCallback(async () => {
    if (!user?.id) return;
    try {
      const { data: userData } = await dbApi.getUserByAuthId(user.id);
      if (!userData) return;
      const { data } = await dbApi.listFavoritos(userData.id);
      setFavoritos((data || []).map((f) => f.ponto_id));
    } catch {}
  }, [user]);

  const fetchRotas = useCallback(async () => {
    const { data: rotasData, error } = await dbApi.listRotas();
    if (error) return;

    const completas = await Promise.all(
      (rotasData || []).map(async (rota) => {
        const { data: rotaPontos } = await dbApi.listRotaPontoByRota(rota.id);
        if (!rotaPontos || rotaPontos.length === 0) {
          return { ...rota, imagem: null, categorias: [], pontoId: null, pontoCount: 0 };
        }

        const pontoIds = rotaPontos.map((p) => p.ponto_id).filter(Boolean);
        const primeiroPontoId = pontoIds[0];

        const { data: pontos } = await dbApi.getPontosByIds([primeiroPontoId]);
        const { data: pontoCategorias } = await dbApi.listPontoCategoriaByPontos(pontoIds);
        const { data: categorias } = await dbApi.listCategorias();

        const catIds = [...new Set((pontoCategorias || []).map((pc) => pc.categoria_id))];
        const catNomes = (categorias || [])
          .filter((c) => catIds.includes(c.id))
          .map((c) => c.nome);

        return {
          ...rota,
          imagem: pontos?.[0]?.url_img || null,
          categorias: catNomes,
          pontoId: primeiroPontoId,
          pontoCount: pontoIds.length,
        };
      })
    );

    setRotas(completas);
  }, []);

  useEffect(() => {
    (async () => {
      await Promise.all([fetchRotas(), fetchUserInfo(), fetchFavoritos()]);
      setLoading(false);
    })();
  }, [fetchRotas, fetchUserInfo, fetchFavoritos]);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchRotas(), fetchFavoritos()]);
    setRefreshing(false);
  };

  const isFavorito = (pontoId) => favoritos.includes(pontoId);

  const toggleFavorito = async (pontoId) => {
    if (!user?.id || !userInfo) {
      showAlert({
        icon: "person-outline",
        iconColor: colors.accent,
        title: "Login necessário",
        message: "Você precisa estar logado para salvar favoritos.",
        buttons: [{ text: "Entendi" }],
      });
      return;
    }
    try {
      if (isFavorito(pontoId)) {
        await dbApi.removeFavorito(userInfo.id, pontoId);
        setFavoritos((prev) => prev.filter((id) => id !== pontoId));
      } else {
        await dbApi.addFavorito(userInfo.id, pontoId);
        setFavoritos((prev) => [...prev, pontoId]);
      }
    } catch (err) {
      handleError("Rotas.toggleFavorito", err, "Não foi possível atualizar o favorito.");
    }
  };

  if (rotaSelecionada) {
    return <DetalhesRota rota={rotaSelecionada} voltar={() => setRotaSelecionada(null)} />;
  }

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={rotas}
            keyExtractor={(item) => String(item.id)}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            ListHeaderComponent={<ListHeader total={rotas.length} />}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
            }
            ListEmptyComponent={
              <View style={styles.empty}>
                <View style={styles.emptyIconWrap}>
                  <Ionicons name="navigate-outline" size={36} color={colors.accent} />
                </View>
                <Text style={styles.emptyTitle}>Nenhuma rota disponível</Text>
                <Text style={styles.emptyBody}>
                  Os roteiros aparecerão aqui assim que forem cadastrados.
                </Text>
              </View>
            }
            renderItem={({ item }) => (
              <RotaCard
                rota={item}
                isFavorito={isFavorito(item.pontoId)}
                onPress={() => setRotaSelecionada(item)}
                onToggleFavorito={() => toggleFavorito(item.pontoId)}
              />
            )}
          />
        )}
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
    gap: spacing.sm,
  },
  // ── Hero ──
  hero: {
    paddingTop: spacing.md,
    paddingBottom: spacing.lg,
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
  statsBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginTop: spacing.md,
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  statsIconWrap: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  statsText: {
    ...typography.caption,
    color: colors.textMuted,
    fontWeight: "600",
    flex: 1,
  },
  // ── RotaCard ──
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
    padding: spacing.sm,
    gap: spacing.sm,
    position: "relative",
  },
  thumb: {
    width: 88,
    height: 88,
    borderRadius: radius.md,
    flexShrink: 0,
  },
  thumbPlaceholder: {
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  cardBody: {
    flex: 1,
    gap: spacing.xxs,
    paddingRight: spacing.lg,
  },
  eyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 1.2,
    fontWeight: "700",
    fontSize: 9,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 16,
    lineHeight: 22,
  },
  cardDesc: {
    ...typography.body,
    fontSize: 12,
    lineHeight: 17,
    color: colors.textSecondary,
  },
  metaRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginTop: spacing.xxs,
  },
  metaItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
  },
  metaText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 11,
  },
  tagsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xxs,
    marginTop: spacing.xxs,
  },
  tag: {
    backgroundColor: colors.badgeBg,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.25)",
  },
  tagText: {
    ...typography.caption,
    color: colors.accent,
    fontSize: 10,
    fontWeight: "600",
  },
  chevron: {
    position: "absolute",
    right: spacing.sm,
    top: "50%",
    marginTop: -9,
  },
  favoriteBtn: {
    position: "absolute",
    top: spacing.xs,
    right: spacing.xs,
    zIndex: 10,
  },
  // ── Empty state ──
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl,
    gap: spacing.sm,
    paddingHorizontal: spacing.xl,
  },
  emptyIconWrap: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xs,
  },
  emptyTitle: {
    ...typography.subtitle,
    textAlign: "center",
  },
  emptyBody: {
    ...typography.body,
    textAlign: "center",
  },
});
