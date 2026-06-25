import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

/**
 * Cartão de coleção temática com percentual de conclusão.
 * Props:
 *  - colecao : { nome, descricao, total, concluidos, percentual }
 */
export default function CollectionCard({ colecao }) {
  const percentual = colecao?.percentual || 0;
  const completa = percentual >= 100;

  return (
    <View style={styles.card}>
      <View style={styles.iconWrap}>
        <Ionicons
          name={completa ? "albums" : "albums-outline"}
          size={24}
          color={completa ? colors.accent : colors.primary}
        />
      </View>
      <View style={styles.info}>
        <Text style={styles.nome} numberOfLines={1}>
          {colecao?.nome}
        </Text>
        <Text style={styles.descricao} numberOfLines={2}>
          {colecao?.descricao}
        </Text>
        <View style={styles.track}>
          <View style={[styles.fill, { width: `${percentual}%` }]} />
        </View>
        <Text style={styles.meta}>
          {colecao?.concluidos || 0}/{colecao?.total || 0} locais · {percentual}%
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    gap: spacing.sm,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
  },
  iconWrap: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "rgba(200,51,73,0.15)",
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
  descricao: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
    marginBottom: spacing.xs,
  },
  track: {
    height: 8,
    borderRadius: 4,
    backgroundColor: "rgba(255,255,255,0.12)",
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 4,
  },
  meta: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: spacing.xxs,
  },
});
