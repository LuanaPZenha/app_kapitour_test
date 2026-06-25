import React, { useCallback, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect, useNavigation } from "@react-navigation/native";

import { kapipassApi } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import { useAppAlert } from "../components/AppAlert";
import SectionHeader from "../components/SectionHeader";
import PressableScale from "../components/PressableScale";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

export default function EcoPassScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const { showAlert } = useAppAlert();
  const [eco, setEco] = useState({ pontuacao_eco_total: 0, atividades: [] });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listEco(userInfo.id);
    if (!error && data) setEco(data);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const registrar = useCallback(
    async (atividade) => {
      const { data, error } = await kapipassApi.registrarEco(atividade.id);
      if (error) {
        showAlert({
          icon: "alert-circle-outline",
          iconColor: colors.primary,
          title: "Ops",
          message: error.message,
          buttons: [{ text: "OK" }],
        });
        return;
      }
      showAlert({
        icon: "leaf",
        iconColor: "#34c759",
        title: "Atividade registrada!",
        message: data?.message || "Obrigado por cuidar de Maricá!",
        buttons: [{ text: "Boa!" }],
      });
      load();
    },
    [load, showAlert]
  );

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
              <SectionHeader title="EcoPass" subtitle="Turismo sustentável e ecológico" />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={eco.atividades}
            keyExtractor={(item) => String(item.id)}
            contentContainerStyle={styles.listContent}
            ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
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
            ListHeaderComponent={
              <View style={[styles.scoreCard, shadows.elevated]}>
                <Ionicons name="leaf" size={28} color="#34c759" />
                <Text style={styles.scoreValor}>{eco.pontuacao_eco_total}</Text>
                <Text style={styles.scoreLabel}>EcoPontos acumulados</Text>
              </View>
            }
            renderItem={({ item }) => (
              <View style={styles.card}>
                <View style={styles.ecoIcon}>
                  <Ionicons name="leaf-outline" size={20} color="#34c759" />
                </View>
                <View style={styles.cardInfo}>
                  <Text style={styles.nome}>{item.nome}</Text>
                  <Text style={styles.descricao} numberOfLines={2}>
                    {item.descricao}
                  </Text>
                  <Text style={styles.meta}>
                    +{item.pontuacao_eco} EcoPontos · +{item.xp_recompensa} XP
                    {item.vezes_registrada ? ` · feito ${item.vezes_registrada}x` : ""}
                  </Text>
                </View>
                <PressableScale
                  onPress={() => registrar(item)}
                  accessibilityLabel={`Registrar ${item.nome}`}
                  contentStyle={styles.addBtn}
                >
                  <Ionicons name="add" size={22} color={colors.text} />
                </PressableScale>
              </View>
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
  header: { paddingHorizontal: layout.contentPadding, paddingTop: spacing.md },
  titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  titleCol: { flex: 1 },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.sm,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  scoreCard: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: "rgba(52,199,89,0.3)",
    padding: spacing.lg,
    alignItems: "center",
    marginBottom: spacing.md,
    gap: 4,
  },
  scoreValor: { ...typography.hero, color: "#34c759" },
  scoreLabel: { ...typography.caption, color: colors.textSecondary },
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
  },
  ecoIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(52,199,89,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardInfo: { flex: 1 },
  nome: { ...typography.subtitle, fontSize: 15 },
  descricao: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  meta: { ...typography.caption, color: "#34c759", marginTop: spacing.xxs },
  addBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    alignItems: "center",
    justifyContent: "center",
  },
});
