import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

const MEDALHAS = {
  1: "#f7c948",
  2: "#c0c0c0",
  3: "#cd7f32",
};

/**
 * Linha de ranking.
 * Props:
 *  - item     : { posicao, nome, valor, unidade }
 *  - destaque : boolean (usuário atual)
 */
export default function RankingCard({ item, destaque = false }) {
  const corMedalha = MEDALHAS[item?.posicao];

  return (
    <View style={[styles.card, destaque && styles.destaque]}>
      <View style={styles.posWrap}>
        {corMedalha ? (
          <Ionicons name="medal" size={22} color={corMedalha} />
        ) : (
          <Text style={styles.pos}>{item?.posicao}</Text>
        )}
      </View>
      <Text style={[styles.nome, destaque && styles.nomeDestaque]} numberOfLines={1}>
        {item?.nome}
      </Text>
      <View style={styles.valorWrap}>
        <Text style={styles.valor}>{item?.valor}</Text>
        <Text style={styles.unidade}>{item?.unidade}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.cardBg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  destaque: {
    borderColor: colors.accent,
    backgroundColor: "rgba(247,160,0,0.08)",
  },
  posWrap: {
    width: 28,
    alignItems: "center",
  },
  pos: {
    ...typography.subtitle,
    color: colors.textSecondary,
  },
  nome: {
    ...typography.subtitle,
    fontSize: 15,
    flex: 1,
  },
  nomeDestaque: {
    color: colors.accent,
  },
  valorWrap: {
    alignItems: "flex-end",
  },
  valor: {
    ...typography.subtitle,
    color: colors.text,
  },
  unidade: {
    ...typography.caption,
    fontSize: 10,
    color: colors.textSecondary,
  },
});
