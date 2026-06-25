import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Image,
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
import SectionHeader from "../components/SectionHeader";
import PressableScale from "../components/PressableScale";
import IconButton from "../components/IconButton";
import { useAppAlert } from "../components/AppAlert";

// ──────────────────────────────────────────────
// RotaCard — card full-width para a lista de rotas
// ──────────────────────────────────────────────
function RotaCard({ rota, isFavorito, onPress, onToggleFavorito }) {
  return (
    <View style={[styles.card, shadows.elevated]}>
      <PressableScale
        onPress={onPress}
        accessibilityLabel={`Rota ${rota.nome}`}
        accessibilityHint="Abre detalhes desta rota"
        contentStyle={styles.cardInner}
      >
        {/* Imagem ou placeholder */}
        {rota.imagem ? (
          <Image
            source={{ uri: rota.imagem }}
            style={styles.cardImage}
            resizeMode="cover"
            accessibilityIgnoresInvertColors
          />
        ) : (
          <View style={[styles.cardImage, styles.cardPlaceholder]}>
            <Ionicons name="map-outline" size={48} color={colors.accent} />
          </View>
        )}

        {/* Gradiente sobre a imagem */}
        <LinearGradient
          colors={["transparent", "rgba(0,0,0,0.78)"]}
          style={styles.cardGradient}
        >
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle} numberOfLines={2}>
              {rota.nome}
            </Text>
            {rota.categorias && rota.categorias.length > 0 && (
              <View style={styles.tagsRow}>
                {rota.categorias.slice(0, 3).map((cat, i) => (
                  <View key={`${cat}-${i}`} style={styles.tag}>
                    <Text style={styles.tagText}>{cat}</Text>
                  </View>
                ))}
                {rota.categorias.length > 3 && (
                  <Text style={styles.tagMore}>+{rota.categorias.length - 3}</Text>
                )}
              </View>
            )}
          </View>
        </LinearGradient>
      </PressableScale>

      {/* Botão favorito */}
      <IconButton
        name={isFavorito ? "heart" : "heart-outline"}
        onPress={onToggleFavorito}
        accessibilityLabel={isFavorito ? "Remover dos favoritos" : "Adicionar aos favoritos"}
        color={isFavorito ? colors.primary : colors.text}
        style={styles.favoriteBtn}
      />
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
    setLoading(true);
    const { data: rotasData, error } = await dbApi.listRotas();
    if (error) {
      setLoading(false);
      return;
    }

    const completas = await Promise.all(
      (rotasData || []).map(async (rota) => {
        const { data: rotaPontos } = await dbApi.listRotaPontoByRota(rota.id);
        if (!rotaPontos || rotaPontos.length === 0) {
          return { ...rota, imagem: null, categorias: [], pontoId: null };
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
        };
      })
    );

    setRotas(completas);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchRotas();
    fetchUserInfo();
    fetchFavoritos();
  }, [fetchRotas, fetchUserInfo, fetchFavoritos]);

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
        <View style={styles.header}>
          <SectionHeader
            title="Rotas Turísticas"
            subtitle="Explore Maricá com roteiros planejados."
          />
        </View>

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
            ListEmptyComponent={
              <View style={styles.empty}>
                <Ionicons name="navigate-outline" size={44} color={colors.textSecondary} />
                <Text style={styles.emptyTitle}>Nenhuma rota disponível</Text>
                <Text style={styles.emptyBody}>
                  As rotas aparecerão aqui assim que forem cadastradas.
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
  header: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
    gap: spacing.md,
  },
  // ── RotaCard ──
  card: {
    width: "100%",
    borderRadius: radius.lg,
    overflow: "hidden",
    backgroundColor: colors.cardBg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    position: "relative",
  },
  cardInner: {
    width: "100%",
  },
  cardImage: {
    width: "100%",
    height: 190,
  },
  cardPlaceholder: {
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  cardGradient: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "65%",
    justifyContent: "flex-end",
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
  },
  cardContent: {
    gap: spacing.xs - 2,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 18,
    lineHeight: 24,
  },
  tagsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
    gap: spacing.xxs,
  },
  tag: {
    backgroundColor: "rgba(255,255,255,0.88)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.pill,
  },
  tagText: {
    color: colors.inputText,
    fontSize: 11,
    fontWeight: "600",
  },
  tagMore: {
    color: colors.text,
    fontSize: 11,
    fontWeight: "500",
    opacity: 0.8,
  },
  favoriteBtn: {
    position: "absolute",
    top: spacing.sm,
    right: spacing.sm,
    zIndex: 10,
  },
  // ── Empty state ──
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl * 2,
    gap: spacing.sm,
    paddingHorizontal: spacing.xl,
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
