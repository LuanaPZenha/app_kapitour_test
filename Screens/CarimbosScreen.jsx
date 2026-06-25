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
import SectionHeader from "../components/SectionHeader";
import StampCard from "../components/StampCard";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

export default function CarimbosScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const [carimbos, setCarimbos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listCarimbos(userInfo.id);
    if (!error) setCarimbos(data || []);
    setLoading(false);
    setRefreshing(false);
  }, [userInfo?.id]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  const obtidos = carimbos.filter((c) => c.obtido).length;

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
              <SectionHeader
                title="Carimbos"
                subtitle={`${obtidos} de ${carimbos.length} coletados`}
              />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={carimbos}
            keyExtractor={(item) => String(item.id)}
            numColumns={3}
            columnWrapperStyle={styles.row}
            contentContainerStyle={styles.listContent}
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
                <Ionicons name="ribbon-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>Nenhum carimbo disponível ainda.</Text>
              </View>
            }
            renderItem={({ item }) => (
              <View style={styles.cell}>
                <StampCard carimbo={item} />
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
  header: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  titleCol: {
    flex: 1,
  },
  listContent: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.sm,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  row: {
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  cell: {
    flex: 1,
  },
  empty: {
    alignItems: "center",
    justifyContent: "center",
    paddingTop: spacing.xxl,
    gap: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
  },
});
