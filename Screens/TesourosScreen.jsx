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
import { KAPIPASS_STAMP } from "../components/StampCard";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

export default function TesourosScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const { showAlert } = useAppAlert();
  const [tesouros, setTesouros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listTesouros();
    if (!error) setTesouros(data || []);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const concluir = useCallback(
    (tesouro) => {
      showAlert({
        icon: "key-outline",
        iconColor: colors.accent,
        title: tesouro.nome,
        message: `Você desvendou a pista?\n\n"${tesouro.pista}"\n\nConfirmar conclusão deste tesouro?`,
        buttons: [
          { text: "Ainda não", style: "cancel" },
          {
            text: "Encontrei!",
            onPress: async () => {
              const { data, error } = await kapipassApi.concluirTesouro(tesouro.id);
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
              const recompensas = data?.recompensas?.length
                ? `\nRecompensas: ${data.recompensas.join(", ")}`
                : "";
              showAlert({
                image: KAPIPASS_STAMP,
                iconColor: colors.accent,
                title: "Tesouro encontrado!",
                message: `${data?.message || ""}${recompensas}`,
                buttons: [{ text: "Incrível!" }],
              });
              load();
            },
          },
        ],
      });
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
              <SectionHeader title="Caça ao Tesouro" subtitle="Desvende pistas e ganhe recompensas raras" />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={tesouros}
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
                <Ionicons name="map-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>Nenhum tesouro disponível ainda.</Text>
              </View>
            }
            renderItem={({ item }) => (
              <View style={[styles.card, item.concluido && styles.cardDone]}>
                <View style={styles.cardTop}>
                  <View style={styles.iconWrap}>
                    <Ionicons
                      name={item.concluido ? "trophy" : "lock-closed"}
                      size={20}
                      color={item.concluido ? colors.accent : colors.primary}
                    />
                  </View>
                  <View style={styles.cardInfo}>
                    <Text style={styles.nome}>{item.nome}</Text>
                    <Text style={styles.descricao} numberOfLines={2}>
                      {item.descricao}
                    </Text>
                  </View>
                  <Text style={styles.xp}>+{item.xp_bonus}</Text>
                </View>

                <View style={styles.pistaBox}>
                  <Ionicons name="search-outline" size={14} color={colors.accent} />
                  <Text style={styles.pista}>{item.pista}</Text>
                </View>

                {item.concluido ? (
                  <Text style={styles.doneText}>Tesouro encontrado!</Text>
                ) : (
                  <PressableScale
                    onPress={() => concluir(item)}
                    accessibilityLabel={`Resolver tesouro ${item.nome}`}
                    contentStyle={styles.btn}
                  >
                    <Text style={styles.btnText}>Já encontrei</Text>
                  </PressableScale>
                )}
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
  card: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
  },
  cardDone: {
    borderColor: "rgba(247,160,0,0.4)",
  },
  cardTop: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
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
  pistaBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: "rgba(247,160,0,0.08)",
    borderRadius: radius.md,
    padding: spacing.sm,
    marginTop: spacing.sm,
  },
  pista: { ...typography.caption, color: colors.textMuted, flex: 1, fontStyle: "italic" },
  doneText: {
    ...typography.caption,
    color: colors.accent,
    marginTop: spacing.sm,
    fontWeight: "700",
  },
  btn: {
    marginTop: spacing.sm,
    backgroundColor: "rgba(247,160,0,0.15)",
    borderWidth: 1,
    borderColor: "rgba(247,160,0,0.4)",
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    alignItems: "center",
  },
  btnText: { ...typography.button, color: colors.accent },
  empty: { alignItems: "center", justifyContent: "center", paddingTop: spacing.xxl, gap: spacing.sm },
  emptyText: { ...typography.body, color: colors.textSecondary },
});
