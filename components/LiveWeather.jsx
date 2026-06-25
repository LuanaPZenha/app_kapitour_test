import React, { useCallback, useEffect, useState } from "react";
import { View, Text, Image, StyleSheet, ActivityIndicator } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { getWeatherByCity } from "../Screens/weatherApi";
import { getCapybaraWeatherInfo, getAccentColor } from "../Screens/WeatherScreen";

const DIAS = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];
const MESES = [
  "jan", "fev", "mar", "abr", "mai", "jun",
  "jul", "ago", "set", "out", "nov", "dez",
];

// Brasília é UTC-3 fixo (sem horário de verão desde 2019).
// Lê os campos UTC de um instante deslocado em -3h para obter o relógio de Brasília
// sem depender de suporte a Intl/timeZone (limitado no Hermes/Android).
function getBrasiliaParts() {
  const brt = new Date(Date.now() - 3 * 60 * 60 * 1000);
  const hh = String(brt.getUTCHours()).padStart(2, "0");
  const mm = String(brt.getUTCMinutes()).padStart(2, "0");
  const ss = String(brt.getUTCSeconds()).padStart(2, "0");
  const dia = DIAS[brt.getUTCDay()];
  const data = `${String(brt.getUTCDate()).padStart(2, "0")} ${MESES[brt.getUTCMonth()]}`;
  return { hora: `${hh}:${mm}`, segundos: ss, dia, data };
}

export default function LiveWeather() {
  const [weather, setWeather] = useState(null);
  const [info, setInfo] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | ok | error
  const [clock, setClock] = useState(getBrasiliaParts());

  const fetchNow = useCallback(async () => {
    const data = await getWeatherByCity("Maricá");
    if (data) {
      setWeather(data);
      setInfo(getCapybaraWeatherInfo(data));
      setStatus("ok");
    } else {
      setStatus((prev) => (prev === "ok" ? "ok" : "error"));
    }
  }, []);

  // Busca inicial + atualização periódica (a cada 10 min)
  useEffect(() => {
    fetchNow();
    const id = setInterval(fetchNow, 10 * 60 * 1000);
    return () => clearInterval(id);
  }, [fetchNow]);

  // Rebusca ao voltar o foco para a Home
  useFocusEffect(
    useCallback(() => {
      fetchNow();
    }, [fetchNow])
  );

  // Relógio de Brasília em tempo real (1s)
  useEffect(() => {
    const id = setInterval(() => setClock(getBrasiliaParts()), 1000);
    return () => clearInterval(id);
  }, []);

  const accent =
    info ? getAccentColor(info.weatherCondition, info.tempCategory) : colors.accent;
  const sugestao = info
    ? info.capybaraSuggestion.split("Clique aqui")[0].trim()
    : "";

  return (
    <View style={styles.card}>
      {/* Relógio de Brasília */}
      <View style={styles.clockRow}>
        <View style={styles.clockLeft}>
          <Ionicons name="time-outline" size={16} color={colors.textSecondary} />
          <Text style={styles.clockLabel}>Horário de Brasília</Text>
        </View>
        <Text style={styles.clockTime}>
          {clock.hora}
          <Text style={styles.clockSeconds}> {clock.segundos}</Text>
        </Text>
      </View>
      <Text style={styles.clockDate}>
        {clock.dia}, {clock.data}
      </Text>

      <View style={styles.divider} />

      {status === "loading" ? (
        <View style={styles.feedback}>
          <ActivityIndicator color={colors.accent} />
          <Text style={styles.feedbackText}>Carregando o clima…</Text>
        </View>
      ) : status === "error" ? (
        <View style={styles.feedback}>
          <Ionicons name="cloud-offline-outline" size={28} color={colors.textSecondary} />
          <Text style={styles.feedbackText}>
            Não foi possível carregar o clima agora.
          </Text>
        </View>
      ) : (
        <View style={styles.weatherBody}>
          <Image
            source={{ uri: info.capybaraImage }}
            style={styles.capy}
            resizeMode="contain"
          />
          <View style={styles.tempRow}>
            <Ionicons name={info.icon} size={22} color={accent} />
            <Text style={styles.temp}>{Math.round(weather.main.temp)}°C</Text>
          </View>
          <Text style={[styles.condition, { color: accent }]}>{info.title}</Text>
          {sugestao ? <Text style={styles.suggestion}>{sugestao}</Text> : null}

          <View style={styles.metaRow}>
            <View style={styles.metaItem}>
              <Ionicons name="water-outline" size={15} color={colors.textSecondary} />
              <Text style={styles.metaText}>{weather.main.humidity}%</Text>
            </View>
            <View style={styles.metaItem}>
              <Ionicons name="navigate-outline" size={15} color={colors.textSecondary} />
              <Text style={styles.metaText}>
                {Math.round(weather.wind.speed * 3.6)} km/h
              </Text>
            </View>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: "100%",
    backgroundColor: "transparent",
    paddingVertical: spacing.xs,
  },
  clockRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  clockLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
  },
  clockLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  clockTime: {
    ...typography.hero,
    fontSize: 26,
    fontVariant: ["tabular-nums"],
  },
  clockSeconds: {
    ...typography.subtitle,
    fontSize: 14,
    color: colors.textSecondary,
  },
  clockDate: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: "capitalize",
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginVertical: spacing.sm,
  },
  feedback: {
    alignItems: "center",
    gap: spacing.xs,
    paddingVertical: spacing.lg,
  },
  feedbackText: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
  },
  weatherBody: {
    alignItems: "center",
  },
  capy: {
    width: "100%",
    height: 190,
    marginBottom: spacing.xs,
  },
  tempRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  temp: {
    ...typography.hero,
    fontSize: 40,
    fontWeight: "300",
  },
  condition: {
    ...typography.subtitle,
    textAlign: "center",
    marginTop: 2,
  },
  suggestion: {
    ...typography.body,
    fontSize: 13,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: spacing.xs,
  },
  metaRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.lg,
    marginTop: spacing.md,
  },
  metaItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
  },
  metaText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
