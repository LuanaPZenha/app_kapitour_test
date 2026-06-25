import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { getIconForCategory } from "../utils/categoryIcons";

export default function PontoListItem({ ponto, categoriaNome, onPress, showOrder, completed }) {
  const icon = getIconForCategory(categoriaNome || ponto.nome);

  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={`Ponto turístico ${ponto.nome}`}
      accessibilityHint="Abre detalhes do ponto"
      contentStyle={[styles.card, shadows.card, completed && styles.cardCompleted]}
    >
      {showOrder != null ? (
        <View style={[styles.orderBadge, completed && styles.orderBadgeDone]}>
          {completed ? (
            <Ionicons name="checkmark" size={14} color={colors.text} />
          ) : (
            <Text style={styles.orderText}>{showOrder}</Text>
          )}
        </View>
      ) : null}

      {ponto.url_img ? (
        <Image
          source={{ uri: ponto.url_img }}
          style={styles.thumb}
          resizeMode="cover"
          accessibilityIgnoresInvertColors
        />
      ) : (
        <View style={styles.iconWrap}>
          <Ionicons name={icon} size={22} color={colors.accent} />
        </View>
      )}

      <View style={styles.content}>
        {!showOrder ? <Text style={styles.eyebrow}>PONTO TURÍSTICO</Text> : null}
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

      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
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
    padding: spacing.sm,
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  cardCompleted: {
    borderLeftColor: colors.accent,
    opacity: 0.85,
  },
  orderBadge: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: colors.primary,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  orderBadgeDone: {
    backgroundColor: colors.accent,
  },
  orderText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: "700",
    fontSize: 12,
  },
  thumb: {
    width: 64,
    height: 64,
    borderRadius: radius.md,
    flexShrink: 0,
  },
  iconWrap: {
    width: 64,
    height: 64,
    borderRadius: radius.md,
    backgroundColor: "rgba(200, 51, 73, 0.15)",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  content: {
    flex: 1,
    gap: spacing.xxs,
  },
  eyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 1.2,
    fontWeight: "700",
    fontSize: 9,
  },
  title: {
    ...typography.subtitle,
    fontSize: 16,
    lineHeight: 22,
  },
  description: {
    ...typography.body,
    fontSize: 12,
    lineHeight: 17,
    color: colors.textSecondary,
  },
  tag: {
    alignSelf: "flex-start",
    marginTop: spacing.xxs,
    backgroundColor: colors.badgeBg,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.25)",
  },
  tagText: {
    ...typography.caption,
    color: colors.accent,
    fontSize: 10,
    fontWeight: "600",
  },
});
