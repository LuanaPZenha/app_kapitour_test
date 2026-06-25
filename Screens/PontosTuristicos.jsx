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
import SectionHeader from "../components/SectionHeader";
import PontoListItem from "../components/PontoListItem";
import PointDetail from "../components/PointDetail";
import PressableScale from "../components/PressableScale";
import { getIconForCategory } from "../utils/categoryIcons";

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

  const renderCategoria = (cat) => {
    const active = categoriaId === cat.id;
    const iconName = getIconForCategory(cat.nome);

    return (
      <PressableScale
        key={cat.id}
        onPress={() => setCategoriaId((prev) => (prev === cat.id ? null : cat.id))}
        accessibilityLabel={`Filtrar por ${cat.nome}`}
        accessibilityState={{ selected: active }}
        contentStyle={[styles.chip, active && styles.chipActive]}
      >
        <Ionicons name={iconName} size={18} color={active ? colors.text : colors.inputText} />
        <Text style={[styles.chipText, active && styles.chipTextActive]}>{cat.nome}</Text>
      </PressableScale>
    );
  };

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <View style={styles.header}>
          <SectionHeader
            title="Pontos Turísticos"
            subtitle={
              loading
                ? "Carregando pontos…"
                : `${pontosFiltrados.length} ${pontosFiltrados.length === 1 ? "local encontrado" : "locais encontrados"} em Maricá`
            }
          />
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.chipsRow}
        >
          <PressableScale
            onPress={() => setCategoriaId(null)}
            accessibilityLabel="Mostrar todos os pontos"
            accessibilityState={{ selected: categoriaId === null }}
            contentStyle={[styles.chip, categoriaId === null && styles.chipActive]}
          >
            <Ionicons
              name="apps-outline"
              size={18}
              color={categoriaId === null ? colors.text : colors.inputText}
            />
            <Text style={[styles.chipText, categoriaId === null && styles.chipTextActive]}>
              Todos
            </Text>
          </PressableScale>
          {categorias.map(renderCategoria)}
        </ScrollView>

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
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
            }
            ListEmptyComponent={
              <View style={styles.empty}>
                <Ionicons name="location-outline" size={40} color={colors.textSecondary} />
                <Text style={styles.emptyText}>Nenhum ponto encontrado nesta categoria.</Text>
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
  flex: {
    flex: 1,
  },
  header: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
  },
  chipsRow: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: spacing.sm,
    gap: spacing.xs,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    minHeight: layout.minTouchTarget,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
    backgroundColor: "rgba(255,255,255,0.92)",
    marginRight: spacing.xs,
  },
  chipActive: {
    backgroundColor: colors.primary,
  },
  chipText: {
    ...typography.caption,
    color: colors.inputText,
    fontWeight: "600",
  },
  chipTextActive: {
    color: colors.text,
  },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl,
    gap: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    textAlign: "center",
  },
});
