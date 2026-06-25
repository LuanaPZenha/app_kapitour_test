import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

export const KAPIPASS_STAMP = require("../assets/kapipass_carimbo.png");

const RARIDADE_COR = {
  comum: colors.textSecondary,
  raro: "#4aa3ff",
  epico: "#b06bff",
  lendario: colors.accent,
};

/**
 * Carimbo digital do KapiPass.
 * Props:
 *  - carimbo : { nome, descricao, imagem, raridade, xp_recompensa, obtido }
 *  - onPress : callback opcional
 */
export default function StampCard({ carimbo, onPress }) {
  const obtido = !!carimbo?.obtido;
  const corRaridade = RARIDADE_COR[carimbo?.raridade] || colors.textSecondary;

  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={`Carimbo ${carimbo?.nome}${obtido ? ", obtido" : ", bloqueado"}`}
      contentStyle={[styles.card, obtido ? shadows.accent : null, !obtido && styles.locked]}
    >
      <View style={[styles.imageWrap, { borderColor: obtido ? corRaridade : colors.borderSubtle }]}>
        <Image
          source={KAPIPASS_STAMP}
          style={[styles.image, !obtido && styles.imageLocked]}
          resizeMode="cover"
        />
        {!obtido ? (
          <View style={styles.lockBadge}>
            <Ionicons name="lock-closed" size={14} color={colors.text} />
          </View>
        ) : null}
      </View>

      <Text style={[styles.nome, !obtido && styles.textLocked]} numberOfLines={2}>
        {carimbo?.nome}
      </Text>

      <View style={styles.metaRow}>
        <Text style={[styles.raridade, { color: obtido ? corRaridade : colors.disabled }]}>
          {carimbo?.raridade || "comum"}
        </Text>
        <Text style={styles.xp}>+{carimbo?.xp_recompensa || 0} XP</Text>
      </View>
    </PressableScale>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.sm,
    alignItems: "center",
  },
  locked: {
    opacity: 0.7,
  },
  imageWrap: {
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 2,
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    marginBottom: spacing.xs,
  },
  image: {
    width: "100%",
    height: "100%",
  },
  imageLocked: {
    opacity: 0.35,
  },
  lockBadge: {
    position: "absolute",
    right: 2,
    bottom: 2,
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: colors.overlay,
    alignItems: "center",
    justifyContent: "center",
  },
  nome: {
    ...typography.caption,
    color: colors.text,
    fontWeight: "600",
    textAlign: "center",
    minHeight: 32,
  },
  textLocked: {
    color: colors.textSecondary,
  },
  metaRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    width: "100%",
    marginTop: spacing.xxs,
    gap: spacing.xxs,
  },
  raridade: {
    ...typography.caption,
    fontSize: 10,
    textTransform: "capitalize",
  },
  xp: {
    ...typography.caption,
    fontSize: 10,
    color: colors.accent,
    fontWeight: "700",
  },
});
