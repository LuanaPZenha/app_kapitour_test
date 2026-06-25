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
import CollectionCard from "../components/CollectionCard";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { layout, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

export default function ColecoesScreen() {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const [colecoes, setColecoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!userInfo?.id) {
      setLoading(false);
      return;
    }
    const { data, error } = await kapipassApi.listColecoes(userInfo.id);
    if (!error) setColecoes(data || []);
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
              <SectionHeader title="Coleções" subtitle="Complete coleções temáticas de Maricá" />
            </View>
          </View>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={colecoes}
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
                <Ionicons name="albums-outline" size={48} color={colors.disabled} />
                <Text style={styles.emptyText}>Nenhuma coleção disponível.</Text>
              </View>
            }
            renderItem={({ item }) => <CollectionCard colecao={item} />}
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
  empty: { alignItems: "center", justifyContent: "center", paddingTop: spacing.xxl, gap: spacing.sm },
  emptyText: { ...typography.body, color: colors.textSecondary },
});
