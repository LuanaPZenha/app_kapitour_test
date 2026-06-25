import React from "react";
import { View, TextInput, StyleSheet } from "react-native";
import IconButton from "./IconButton";
import { colors } from "../theme/colors";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

export default function TextField({
  value,
  onChangeText,
  placeholder,
  secureTextEntry,
  keyboardType = "default",
  autoCapitalize = "none",
  editable = true,
  accessibilityLabel,
  showPasswordToggle,
  isPasswordVisible,
  onTogglePassword,
  style,
}) {
  return (
    <View style={[styles.wrapper, style]}>
      <TextInput
        style={[styles.input, showPasswordToggle && styles.inputWithToggle]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.inputPlaceholder}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
        autoCapitalize={autoCapitalize}
        editable={editable}
        accessibilityLabel={accessibilityLabel || placeholder}
        textContentType={secureTextEntry ? "password" : "emailAddress"}
      />
      {showPasswordToggle ? (
        <IconButton
          name={isPasswordVisible ? "eye-off-outline" : "eye-outline"}
          onPress={onTogglePassword}
          accessibilityLabel={
            isPasswordVisible ? "Ocultar senha" : "Mostrar senha"
          }
          color={colors.inputPlaceholder}
          variant="ghost"
          style={styles.toggle}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: "relative",
    marginBottom: spacing.md,
  },
  input: {
    backgroundColor: colors.inputBg,
    color: colors.inputText,
    minHeight: layout.minTouchTarget + spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    ...typography.body,
    fontSize: 16,
    color: colors.inputText,
  },
  inputWithToggle: {
    paddingRight: layout.minTouchTarget + spacing.xs,
  },
  toggle: {
    position: "absolute",
    right: 0,
    top: 0,
    bottom: 0,
    justifyContent: "center",
  },
});
