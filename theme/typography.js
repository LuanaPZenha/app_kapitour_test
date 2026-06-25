import { Platform } from "react-native";
import { colors } from "./colors";

const base = Platform.select({
  ios: "System",
  android: "Roboto",
  default: "System",
});

export const typography = {
  hero: {
    fontFamily: base,
    fontSize: 24,
    lineHeight: 32,
    fontWeight: "700",
    color: colors.text,
  },
  title: {
    fontFamily: base,
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "700",
    color: colors.text,
  },
  subtitle: {
    fontFamily: base,
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "600",
    color: colors.text,
  },
  body: {
    fontFamily: base,
    fontSize: 15,
    lineHeight: 22,
    fontWeight: "400",
    color: colors.textSecondary,
  },
  caption: {
    fontFamily: base,
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "500",
    color: colors.textMuted,
  },
  button: {
    fontFamily: base,
    fontSize: 15,
    lineHeight: 20,
    fontWeight: "700",
    color: colors.text,
  },
};
