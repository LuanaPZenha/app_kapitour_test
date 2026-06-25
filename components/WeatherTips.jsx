import React, { useMemo } from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { getWeatherAlerts } from "../utils/weatherSuggestions";

const LEVEL_STYLE = {
  danger: {
    bg: "rgba(200, 51, 73, 0.14)",
    border: "rgba(200, 51, 73, 0.45)",
    iconColor: "#e65a6d",
  },
  warning: {
    bg: "rgba(247, 160, 0, 0.12)",
    border: "rgba(247, 160, 0, 0.40)",
    iconColor: colors.accent,
  },
  tip: {
    bg: "rgba(255, 255, 255, 0.06)",
    border: colors.borderSubtle,
    iconColor: colors.textSecondary,
  },
};

export default function WeatherTips({ weatherInfo }) {
  const alerts = useMemo(() => getWeatherAlerts(weatherInfo), [weatherInfo]);

  if (!weatherInfo || alerts.length === 0) return null;

  return (
    <View style={styles.wrap}>
      <View style={styles.divider} />

      <View style={styles.headlineRow}>
        <View style={styles.shieldWrap}>
          <Ionicons name="shield-checkmark-outline" size={15} color={colors.accent} />
        </View>
        <Text style={styles.headline}>Alertas para hoje</Text>
      </View>

      <View style={styles.list}>
        {alerts.map((alert, i) => {
          const s = LEVEL_STYLE[alert.level];
          return (
            <View
              key={i}
              style={[styles.alertCard, { backgroundColor: s.bg, borderColor: s.border }]}
            >
              <Ionicons name={alert.icon} size={20} color={s.iconColor} style={styles.alertIcon} />
              <Text style={styles.alertText}>{alert.message}</Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    marginTop: spacing.md,
  },
  divider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginBottom: spacing.md,
  },
  headlineRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  shieldWrap: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: "rgba(247, 160, 0, 0.14)",
    alignItems: "center",
    justifyContent: "center",
  },
  headline: {
    ...typography.subtitle,
    fontSize: 15,
  },
  list: {
    gap: spacing.xs,
  },
  alertCard: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: radius.md,
    borderWidth: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  alertIcon: {
    flexShrink: 0,
  },
  alertText: {
    ...typography.body,
    fontSize: 13,
    lineHeight: 19,
    color: colors.textMuted,
    flex: 1,
  },
});
