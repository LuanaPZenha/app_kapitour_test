import React, { useCallback, useState } from "react";
import {
  View,
  Text,
  Image,
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
import SectionHeader from "../components/SectionHeader";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

function formatarData(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return "";
  }
}

export default function DiarioScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const [entradas, setEntradas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listDiario();
    if (!error) setEntradas(data || []);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
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
              <SectionHeader title="Diário de Viagem" subtitle="Suas memórias por Maricá" />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={entradas}
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
                <Ionicons name="journal-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>
                  Seu diário está vazio. Faça check-ins para criar memórias automaticamente.
                </Text>
              </View>
            }
            renderItem={({ item }) => (
              <View style={styles.card}>
                {item.foto ? (
                  <Image source={{ uri: item.foto }} style={styles.foto} resizeMode="cover" />
                ) : (
                  <View style={[styles.foto, styles.fotoPlaceholder]}>
                    <Ionicons name="image-outline" size={26} color={colors.disabled} />
                  </View>
                )}
                <View style={styles.cardInfo}>
                  <Text style={styles.ponto} numberOfLines={1}>
                    {item.ponto_nome || "Memória"}
                  </Text>
                  <Text style={styles.comentario} numberOfLines={3}>
                    {item.comentario}
                  </Text>
                  <Text style={styles.data}>{formatarData(item.data)}</Text>
                </View>
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
    flexDirection: "row",
    gap: spacing.sm,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.sm,
  },
  foto: {
    width: 72,
    height: 72,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceElevated,
  },
  fotoPlaceholder: { alignItems: "center", justifyContent: "center" },
  cardInfo: { flex: 1 },
  ponto: { ...typography.subtitle, fontSize: 15 },
  comentario: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  data: { ...typography.caption, color: colors.textMuted, marginTop: spacing.xxs },
  empty: { alignItems: "center", justifyContent: "center", paddingTop: spacing.xxl, gap: spacing.sm },
  emptyText: { ...typography.body, color: colors.textSecondary, textAlign: "center" },
});
