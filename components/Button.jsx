import React from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

export default function Button({
  variant = "primary",
  onPress,
  icon,
  children,
  style,
  fullWidth = false,
  disabled = false,
  loading = false,
  accessibilityLabel,
}) {
  const isGhost = variant === "ghost";
  const isBusy = disabled || loading;
  const textColor = isGhost ? colors.text : colors.text;

  const content = (
    <View style={[styles.row, fullWidth && styles.rowFullWidth]}>
      {loading ? (
        <ActivityIndicator size="small" color={textColor} />
      ) : icon ? (
        <Ionicons name={icon} size={fullWidth ? 17 : 18} color={textColor} />
      ) : null}
      <Text
        style={[
          styles.label,
          { color: textColor },
          fullWidth && styles.labelFullWidth,
          loading && styles.labelLoading,
        ]}
        numberOfLines={1}
        adjustsFontSizeToFit={fullWidth}
        minimumFontScale={fullWidth ? 0.96 : 1}
      >
        {loading ? "Carregando..." : children}
      </Text>
    </View>
  );

  const label = accessibilityLabel || (typeof children === "string" ? children : undefined);

  if (isGhost) {
    return (
      <PressableScale
        onPress={onPress}
        disabled={isBusy}
        accessibilityLabel={label}
        accessibilityState={{ disabled: isBusy, busy: loading }}
        style={[fullWidth && styles.fullWidthTouchable, style]}
        contentStyle={[
          styles.buttonBase,
          styles.ghost,
          fullWidth && styles.fullWidth,
          isBusy && styles.disabled,
        ]}
      >
        {content}
      </PressableScale>
    );
  }

  return (
    <PressableScale
      onPress={onPress}
      disabled={isBusy}
      accessibilityLabel={label}
      accessibilityState={{ disabled: isBusy, busy: loading }}
      style={[fullWidth && styles.fullWidthTouchable, style]}
      contentStyle={[fullWidth && styles.fullWidth, isBusy && styles.disabled]}
    >
      <LinearGradient
        {...gradients.button}
        style={[styles.buttonBase, fullWidth && styles.fullWidth, shadows.brand]}
      >
        {content}
      </LinearGradient>
    </PressableScale>
  );
}

const styles = StyleSheet.create({
  buttonBase: {
    minHeight: layout.minTouchTarget,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.sm,
    alignItems: "center",
    justifyContent: "center",
  },
  ghost: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: colors.border,
  },
  fullWidthTouchable: {
    width: "100%",
  },
  fullWidth: {
    width: "100%",
    minHeight: layout.minTouchTarget,
    paddingVertical: 0,
    paddingHorizontal: spacing.sm,
  },
  disabled: {
    opacity: 0.55,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  rowFullWidth: {
    justifyContent: "center",
    width: "100%",
  },
  label: {
    ...typography.button,
  },
  labelFullWidth: {
    flexShrink: 1,
    textAlign: "center",
    fontSize: 16,
  },
  labelLoading: {
    opacity: 0.9,
  },
});
