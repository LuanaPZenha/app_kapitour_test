import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { getIconForCategory } from "../utils/categoryIcons";

export default function PontoListItem({ ponto, categoriaNome, onPress }) {
  const icon = getIconForCategory(categoriaNome || ponto.nome);

  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={`Ponto turístico ${ponto.nome}`}
      accessibilityHint="Abre detalhes do ponto"
      contentStyle={[styles.card, shadows.card]}
    >
      <View style={styles.iconWrap}>
        <Ionicons name={icon} size={22} color={colors.accent} />
      </View>
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={2}>
          {ponto.nome}
        </Text>
        {ponto.descricao ? (
          <Text style={styles.description} numberOfLines={2}>
            {ponto.descricao}
          </Text>
        ) : null}
        {categoriaNome ? (
          <View style={styles.tag}>
            <Text style={styles.tagText}>{categoriaNome}</Text>
          </View>
        ) : null}
      </View>
      <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
    </PressableScale>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
    padding: spacing.md,
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  iconWrap: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: "rgba(200, 51, 73, 0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    flex: 1,
    gap: spacing.xxs,
  },
  title: {
    ...typography.subtitle,
    fontSize: 16,
  },
  description: {
    ...typography.body,
    fontSize: 13,
  },
  tag: {
    alignSelf: "flex-start",
    marginTop: spacing.xxs,
    backgroundColor: colors.badgeBg,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xxs,
  },
  tagText: {
    ...typography.caption,
    color: colors.accent,
  },
});
