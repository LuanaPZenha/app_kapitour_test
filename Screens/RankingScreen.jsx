import React, { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { kapipassApi } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import SectionHeader from "../components/SectionHeader";
import PressableScale from "../components/PressableScale";
import RankingCard from "../components/RankingCard";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

const CATEGORIAS = [
  { id: "exploradores", label: "Exploradores" },
  { id: "trilheiros", label: "Trilheiros" },
  { id: "colecionadores", label: "Colecionadores" },
  { id: "ecopass", label: "EcoPass" },
  { id: "xp", label: "XP" },
];

export default function RankingScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const [categoria, setCategoria] = useState("exploradores");
  const [itens, setItens] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (cat) => {
    setLoading(true);
    const { data, error } = await kapipassApi.getRankings(cat, 1, 50);
    if (!error) setItens(data?.itens || []);
    setLoading(false);
  }, []);

  useEffect(() => {
    load(categoria);
  }, [categoria, load]);

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <View style={styles.header}>
          <View style={styles.titleRow}>
            <Ionicons
              name="chevron-back"
              size={26}
              color={colors.text}
              onPress={() => navigation.goBack()}
            />
            <View style={styles.titleCol}>
              <SectionHeader title="Rankings" subtitle="Veja quem mais explora Maricá" />
            </View>
          </View>
        </View>

        <View style={styles.chipsWrap}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipsContent}
          >
            {CATEGORIAS.map((cat) => {
              const ativo = cat.id === categoria;
              return (
                <PressableScale
                  key={cat.id}
                  onPress={() => setCategoria(cat.id)}
                  accessibilityLabel={`Ranking ${cat.label}`}
                  contentStyle={[styles.chip, ativo && styles.chipAtivo]}
                >
                  <Text style={[styles.chipText, ativo && styles.chipTextAtivo]}>
                    {cat.label}
                  </Text>
                </PressableScale>
              );
            })}
          </ScrollView>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={itens}
            keyExtractor={(item) => String(item.usuario_id)}
            contentContainerStyle={styles.listContent}
            ItemSeparatorComponent={() => <View style={{ height: spacing.xs }} />}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Ionicons name="podium-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>Sem dados nesta categoria ainda.</Text>
              </View>
            }
            renderItem={({ item }) => (
              <RankingCard item={item} destaque={item.usuario_id === userInfo?.id} />
            )}
          />
        )}
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  header: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
  },
  titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  titleCol: { flex: 1 },
  chipsWrap: {
    marginTop: spacing.xs,
  },
  chipsContent: {
    paddingHorizontal: layout.contentPadding,
    gap: spacing.xs,
  },
  chip: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: radius.round,
    backgroundColor: colors.cardBg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  chipAtivo: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: "600",
  },
  chipTextAtivo: {
    color: colors.text,
  },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl,
    gap: spacing.sm,
  },
  emptyText: { ...typography.body, color: colors.textSecondary },
});
