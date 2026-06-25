import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

/**
 * Cartão de conquista do KapiPass.
 * Props:
 *  - conquista : { nome, descricao, icone, xp_bonus, desbloqueada }
 */
export default function AchievementCard({ conquista }) {
  const desbloqueada = !!conquista?.desbloqueada;

  return (
    <View
      style={[styles.card, desbloqueada ? styles.cardUnlocked : styles.cardLocked]}
      accessibilityLabel={`Conquista ${conquista?.nome}${desbloqueada ? ", desbloqueada" : ", bloqueada"}`}
    >
      <View
        style={[
          styles.iconWrap,
          { backgroundColor: desbloqueada ? "rgba(247,160,0,0.15)" : "rgba(255,255,255,0.06)" },
        ]}
      >
        <Ionicons
          name={conquista?.icone || "trophy-outline"}
          size={24}
          color={desbloqueada ? colors.accent : colors.disabled}
        />
      </View>

      <View style={styles.info}>
        <Text style={[styles.nome, !desbloqueada && styles.textLocked]} numberOfLines={1}>
          {conquista?.nome}
        </Text>
        <Text style={styles.descricao} numberOfLines={2}>
          {conquista?.descricao}
        </Text>
      </View>

      <View style={styles.trailing}>
        {desbloqueada ? (
          <Ionicons name="checkmark-circle" size={20} color={colors.accent} />
        ) : (
          <Ionicons name="lock-closed" size={18} color={colors.disabled} />
        )}
        <Text style={[styles.xp, !desbloqueada && styles.textLocked]}>+{conquista?.xp_bonus || 0}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    padding: spacing.sm,
    gap: spacing.sm,
  },
  cardUnlocked: {
    borderColor: "rgba(247,160,0,0.35)",
  },
  cardLocked: {
    borderColor: colors.borderSubtle,
    opacity: 0.85,
  },
  iconWrap: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  info: {
    flex: 1,
  },
  nome: {
    ...typography.subtitle,
    fontSize: 15,
  },
  textLocked: {
    color: colors.textSecondary,
  },
  descricao: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  trailing: {
    alignItems: "center",
    gap: 2,
  },
  xp: {
    ...typography.caption,
    fontSize: 11,
    color: colors.accent,
    fontWeight: "700",
  },
});
