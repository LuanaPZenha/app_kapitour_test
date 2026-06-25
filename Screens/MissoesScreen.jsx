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

export default function MissoesScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const { showAlert } = useAppAlert();
  const [missoes, setMissoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listMissoes(userInfo.id);
    if (!error) setMissoes(data || []);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const aceitar = useCallback(
    async (missao) => {
      const { error } = await kapipassApi.aceitarMissao(missao.id);
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
              <SectionHeader title="Missões" subtitle="Complete desafios e ganhe XP" />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={missoes}
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
            ListEmptyComponent={
              <View style={styles.empty}>
                <Ionicons name="flag-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>Nenhuma missão disponível.</Text>
              </View>
            }
            renderItem={({ item }) => {
              const pct = item.objetivo_quantidade
                ? Math.min(100, Math.round((item.progresso / item.objetivo_quantidade) * 100))
                : 0;
              return (
                <View style={styles.card}>
                  <View style={styles.cardTop}>
                    <View style={styles.iconWrap}>
                      <Ionicons
                        name={item.concluida ? "checkmark-done" : "flag"}
                        size={20}
                        color={item.concluida ? colors.accent : colors.primary}
                      />
                    </View>
                    <View style={styles.cardInfo}>
                      <Text style={styles.nome}>{item.nome}</Text>
                      <Text style={styles.descricao} numberOfLines={2}>
                        {item.descricao}
                      </Text>
                    </View>
                    <Text style={styles.xp}>+{item.xp}</Text>
                  </View>

                  {item.aceita ? (
                    <>
                      <View style={styles.track}>
                        <View style={[styles.fill, { width: `${pct}%` }]} />
                      </View>
                      <Text style={styles.progresso}>
                        {item.concluida
                          ? "Concluída!"
                          : `${item.progresso}/${item.objetivo_quantidade} · ${pct}%`}
                      </Text>
                    </>
                  ) : (
                    <PressableScale
                      onPress={() => aceitar(item)}
                      accessibilityLabel={`Aceitar missão ${item.nome}`}
                      contentStyle={styles.aceitarBtn}
                    >
                      <Text style={styles.aceitarText}>Aceitar missão</Text>
                    </PressableScale>
                  )}
                </View>
              );
            }}
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
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.sm,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  card: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
  },
  cardTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  iconWrap: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(200,51,73,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardInfo: { flex: 1 },
  nome: { ...typography.subtitle, fontSize: 15 },
  descricao: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  xp: { ...typography.subtitle, color: colors.accent },
  track: {
    height: 8,
    borderRadius: 4,
    backgroundColor: "rgba(255,255,255,0.12)",
    overflow: "hidden",
    marginTop: spacing.sm,
  },
  fill: { height: "100%", backgroundColor: colors.accent, borderRadius: 4 },
  progresso: { ...typography.caption, color: colors.textMuted, marginTop: spacing.xxs },
  aceitarBtn: {
    marginTop: spacing.sm,
    backgroundColor: "rgba(247,160,0,0.15)",
    borderWidth: 1,
    borderColor: "rgba(247,160,0,0.4)",
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    alignItems: "center",
  },
  aceitarText: { ...typography.button, color: colors.accent },
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl,
    gap: spacing.sm,
  },
  emptyText: { ...typography.body, color: colors.textSecondary },
});
