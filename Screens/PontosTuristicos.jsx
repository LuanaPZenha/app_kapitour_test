import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ScrollView,
  ActivityIndicator,
  Modal,
  RefreshControl,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { dbApi } from "../lib/api";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import PontoListItem from "../components/PontoListItem";
import PointDetail from "../components/PointDetail";
import PressableScale from "../components/PressableScale";
import { getIconForCategory } from "../utils/categoryIcons";

function ListHeader({ total, categorias, categoriaId, onSelectCategoria }) {
  const renderChip = (cat) => {
    const active = categoriaId === cat.id;
    const iconName = getIconForCategory(cat.nome);
    return (
      <PressableScale
        key={cat.id}
        onPress={() => onSelectCategoria(active ? null : cat.id)}
        accessibilityLabel={`Filtrar por ${cat.nome}`}
        accessibilityState={{ selected: active }}
        contentStyle={[styles.chip, active && styles.chipActive]}
      >
        <Ionicons name={iconName} size={16} color={active ? colors.text : colors.accent} />
        <Text style={[styles.chipText, active && styles.chipTextActive]}>{cat.nome}</Text>
      </PressableScale>
    );
  };

  return (
    <View style={styles.hero}>
      <View style={styles.heroTitleRow}>
        <View style={styles.heroIconWrap}>
          <Ionicons name="location" size={22} color={colors.accent} />
        </View>
        <Text style={styles.heroTitle}>Pontos Turísticos</Text>
      </View>
      <Text style={styles.heroSubtitle}>
        Descubra praias, trilhas, patrimônio histórico e muito mais em Maricá.
      </Text>

      <View style={styles.statsBanner}>
        <View style={styles.statsIconWrap}>
          <Ionicons name="pin-outline" size={18} color={colors.accent} />
        </View>
        <Text style={styles.statsText}>
          {total} {total === 1 ? "local encontrado" : "locais encontrados"} em Maricá
        </Text>
      </View>

      <Text style={styles.filterLabel}>Filtrar por categoria</Text>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chipsRow}
      >
        <PressableScale
          onPress={() => onSelectCategoria(null)}
          accessibilityLabel="Mostrar todos os pontos"
          accessibilityState={{ selected: categoriaId === null }}
          contentStyle={[styles.chip, categoriaId === null && styles.chipActive]}
        >
          <Ionicons
            name="apps-outline"
            size={16}
            color={categoriaId === null ? colors.text : colors.accent}
          />
          <Text style={[styles.chipText, categoriaId === null && styles.chipTextActive]}>
            Todos
          </Text>
        </PressableScale>
        {categorias.map(renderChip)}
      </ScrollView>
    </View>
  );
}

export default function PontosTuristicos() {
  const [categorias, setCategorias] = useState([]);
  const [pontos, setPontos] = useState([]);
  const [pontoCategorias, setPontoCategorias] = useState([]);
  const [categoriaId, setCategoriaId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPonto, setSelectedPonto] = useState(null);

  const loadData = useCallback(async () => {
    const [catRes, pontosRes] = await Promise.all([
      dbApi.listCategorias(),
      dbApi.listPontos(),
    ]);

    if (!catRes.error && catRes.data) {
      setCategorias(catRes.data);
      await AsyncStorage.setItem(
        "cache:categorias",
        JSON.stringify({ ts: Date.now(), data: catRes.data })
      );
    }

    if (!pontosRes.error && pontosRes.data) {
      setPontos(pontosRes.data);
      await AsyncStorage.setItem(
        "cache:pontos:all",
        JSON.stringify({ ts: Date.now(), data: pontosRes.data })
      );

      const ids = pontosRes.data.map((p) => p.id);
      const relRes = await dbApi.listPontoCategoriaByPontos(ids);
      if (!relRes.error) {
        setPontoCategorias(relRes.data || []);
      }
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const cachedCats = await AsyncStorage.getItem("cache:categorias");
        const cachedPontos = await AsyncStorage.getItem("cache:pontos:all");
        if (cachedCats) setCategorias(JSON.parse(cachedCats).data || []);
        if (cachedPontos) setPontos(JSON.parse(cachedPontos).data || []);
      } catch {
        // noop
      }
      await loadData();
      setLoading(false);
    })();
  }, [loadData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const categoriaPorPonto = useMemo(() => {
    const catMap = new Map(categorias.map((c) => [c.id, c.nome]));
    const result = new Map();
    pontoCategorias.forEach((rel) => {
      if (!result.has(rel.ponto_id)) {
        result.set(rel.ponto_id, catMap.get(rel.categoria_id));
      }
    });
    return result;
  }, [categorias, pontoCategorias]);

  const pontosFiltrados = useMemo(() => {
    if (!categoriaId) {
      return [...pontos].sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
    }
    const ids = new Set(
      pontoCategorias
        .filter((rel) => rel.categoria_id === categoriaId)
        .map((rel) => rel.ponto_id)
    );
    return pontos
      .filter((p) => ids.has(p.id))
      .sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
  }, [pontos, pontoCategorias, categoriaId]);

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={pontosFiltrados}
            keyExtractor={(item) => String(item.id)}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            ListHeaderComponent={
              <ListHeader
                total={pontosFiltrados.length}
                categorias={categorias}
                categoriaId={categoriaId}
                onSelectCategoria={setCategoriaId}
              />
            }
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
            }
            ListEmptyComponent={
              <View style={styles.empty}>
                <View style={styles.emptyIconWrap}>
                  <Ionicons name="location-outline" size={36} color={colors.accent} />
                </View>
                <Text style={styles.emptyTitle}>Nenhum ponto encontrado</Text>
                <Text style={styles.emptyBody}>
                  Tente outra categoria ou volte mais tarde.
                </Text>
              </View>
            }
            renderItem={({ item }) => (
              <PontoListItem
                ponto={item}
                categoriaNome={categoriaPorPonto.get(item.id)}
                onPress={() => setSelectedPonto(item)}
              />
            )}
          />
        )}

        <Modal visible={!!selectedPonto} animationType="slide" onRequestClose={() => setSelectedPonto(null)}>
          {selectedPonto ? (
            <PointDetail point={selectedPonto} onClose={() => setSelectedPonto(null)} />
          ) : null}
        </Modal>
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
  },
  hero: {
    paddingTop: spacing.md,
    paddingBottom: spacing.md,
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
  filterLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.md,
    marginBottom: spacing.xs,
    textTransform: "uppercase",
    letterSpacing: 0.8,
    fontWeight: "600",
  },
  chipsRow: {
    gap: spacing.xs,
    paddingBottom: spacing.sm,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    marginRight: spacing.xs,
  },
  chipActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipText: {
    ...typography.caption,
    color: colors.textMuted,
    fontWeight: "600",
  },
  chipTextActive: {
    color: colors.text,
  },
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
