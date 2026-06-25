import React from "react";
import { StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { shadows } from "../theme/shadows";

/** Alvo de toque mínimo 44pt (HIG) com ícone centralizado. */
export default function IconButton({
  name,
  onPress,
  accessibilityLabel,
  color = colors.text,
  size = 20,
  variant = "overlay",
  style,
  disabled = false,
}) {
  const isOverlay = variant === "overlay";

  return (
    <PressableScale
      onPress={onPress}
      disabled={disabled}
      accessibilityLabel={accessibilityLabel}
      accessibilityRole="button"
      style={style}
      contentStyle={[
        styles.base,
        isOverlay ? styles.overlay : styles.ghost,
        disabled && styles.disabled,
      ]}
    >
      <Ionicons name={name} size={size} color={color} />
    </PressableScale>
  );
}

const styles = StyleSheet.create({
  base: {
    minWidth: layout.minTouchTarget,
    minHeight: layout.minTouchTarget,
    borderRadius: radius.round,
    alignItems: "center",
    justifyContent: "center",
  },
  overlay: {
    backgroundColor: colors.overlay,
    ...shadows.soft,
  },
  ghost: {
    backgroundColor: "transparent",
  },
  disabled: {
    opacity: 0.5,
  },
});
