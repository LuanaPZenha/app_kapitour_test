import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";
import { spacing } from "../theme/spacing";

/**
 * Cabeçalho de seção com barra de acento lateral e slot de ação.
 * Props:
 *  - title      : texto principal (obrigatório)
 *  - subtitle   : texto secundário abaixo do título (opcional)
 *  - action     : elemento React à direita (opcional)
 *  - style      : override de estilo externo (opcional)
 *  - noAccent   : oculta a barra colorida (opcional, default false)
 */
export default function SectionHeader({ title, subtitle, action, style, noAccent = false }) {
  return (
    <View style={[styles.wrapper, style]} accessibilityRole="header">
      <View style={styles.row}>
        <View style={styles.titleRow}>
          {!noAccent && <View style={styles.accentBar} />}
          <Text style={styles.title}>{title}</Text>
        </View>
        {action ? <View style={styles.actionSlot}>{action}</View> : null}
      </View>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    marginBottom: spacing.sm,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
    gap: spacing.xs,
  },
  accentBar: {
    width: 3,
    height: 20,
    borderRadius: 2,
    backgroundColor: colors.primary,
  },
  title: {
    ...typography.title,
    flex: 1,
  },
  actionSlot: {
    marginLeft: spacing.sm,
  },
  subtitle: {
    ...typography.body,
    marginTop: spacing.xxs + 2,
    marginLeft: 3 + spacing.xs, // align with title (accentBar width + gap)
  },
});
