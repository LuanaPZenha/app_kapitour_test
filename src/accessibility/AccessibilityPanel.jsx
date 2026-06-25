import React from "react";
import {
  View,
  Text,
  Switch,
  TouchableOpacity,
  StyleSheet,
  Pressable,
  Platform,
} from "react-native";
import * as Speech from "expo-speech";
import { Ionicons } from "@expo/vector-icons";
import { useAccessibility } from "./AccessibilityContext";
import { speak as ttsSpeak, stopSpeaking as ttsStop } from "./tts";

const ACCENT = "#c83349";
const ACCENT_DARK = "#ff6b81";
const SURFACE_LIGHT = "#f5f5f7";
const SURFACE_DARK = "#1c1c1e";
const CARD_LIGHT = "#ffffff";
const CARD_DARK = "#2c2c2e";
const TEXT_LIGHT = "#1a1a1a";
const TEXT_DARK = "#f0f0f0";
const MUTED_LIGHT = "#6e6e73";
const MUTED_DARK = "#9d9da0";
const BORDER_LIGHT = "rgba(0,0,0,0.08)";
const BORDER_DARK = "rgba(255,255,255,0.08)";

function Row({ icon, label, dark, children }) {
  return (
    <View style={[styles.row, { borderBottomColor: dark ? BORDER_DARK : BORDER_LIGHT }]}>
      <View style={styles.rowLeft}>
        <View style={[styles.iconWrap, { backgroundColor: dark ? "#3a3a3c" : "#f0f0f2" }]}>
          <Ionicons name={icon} size={18} color={dark ? ACCENT_DARK : ACCENT} />
        </View>
        <Text style={[styles.rowLabel, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>{label}</Text>
      </View>
      <View style={styles.rowRight}>{children}</View>
    </View>
  );
}

function StepButton({ label, onPress, dark }) {
  return (
    <TouchableOpacity
      onPress={onPress}
      accessibilityLabel={label}
      activeOpacity={0.7}
      style={[styles.stepBtn, { backgroundColor: dark ? "#3a3a3c" : "#e8e8ed" }]}
    >
      <Text style={[styles.stepBtnText, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>{label}</Text>
    </TouchableOpacity>
  );
}

export default function AccessibilityPanel({ onClose = () => {} }) {
  const { state, update, reset } = useAccessibility();
  const dark = !!state.darkMode;

  // Fala diretamente (sem checar ttsEnabled) — para feedback do próprio painel
  const sayNow = (text) => {
    const rate = Math.max(0.5, Math.min(1.8, state.ttsRate || 1.0));
    if (Platform.OS === "web") {
      window.speechSynthesis?.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = "pt-BR";
      utter.rate = rate;
      window.speechSynthesis.speak(utter);
    } else {
      Speech.stop();
      Speech.speak(text, { language: "pt-BR", rate });
    }
  };

  const decFont = () => {
    const next = Math.max(0.8, Math.round(((state.fontScale || 1) - 0.1) * 10) / 10);
    update({ fontScale: next });
    ttsSpeak(`Tamanho da fonte: ${next.toFixed(1)} vezes`);
  };
  const incFont = () => {
    const next = Math.min(1.8, Math.round(((state.fontScale || 1) + 0.1) * 10) / 10);
    update({ fontScale: next });
    ttsSpeak(`Tamanho da fonte: ${next.toFixed(1)} vezes`);
  };

  const speakSample = () => {
    sayNow("Narração de voz ativada no Kapitour. Toque em qualquer elemento para ouvi-lo.");
  };

  const stopSpeaking = () => {
    ttsStop();
  };

  const toggleDarkMode = (v) => {
    update({ darkMode: v });
    ttsSpeak(v ? "Tema escuro ativado" : "Tema claro ativado");
  };

  const toggleTTS = (v) => {
    update({ ttsEnabled: v });
    // Fala diretamente pois o estado ainda pode não ter propagado
    if (v) sayNow("Narração ativada");
    else sayNow("Narração desativada");
  };

  const decRate = () => {
    const next = Math.max(0.5, +((state.ttsRate || 1) - 0.2).toFixed(1));
    update({ ttsRate: next });
    ttsSpeak(`Velocidade: ${next.toFixed(1)} vezes`);
  };

  const incRate = () => {
    const next = Math.min(1.8, +((state.ttsRate || 1) + 0.2).toFixed(1));
    update({ ttsRate: next });
    ttsSpeak(`Velocidade: ${next.toFixed(1)} vezes`);
  };

  const handleReset = () => {
    reset();
    sayNow("Configurações restauradas para o padrão");
  };

  return (
    <View style={[styles.sheet, { backgroundColor: dark ? SURFACE_DARK : SURFACE_LIGHT }]}>
      {/* Handle */}
      <View style={styles.handleWrap}>
        <View style={[styles.handle, { backgroundColor: dark ? "#4a4a4c" : "#c7c7cc" }]} />
      </View>

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Ionicons
            name="accessibility-outline"
            size={22}
            color={dark ? ACCENT_DARK : ACCENT}
            style={{ marginRight: 8 }}
          />
          <Text style={[styles.title, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>
            Acessibilidade
          </Text>
        </View>
        <Pressable
          onPress={onClose}
          accessibilityLabel="Fechar painel"
          hitSlop={12}
          style={({ pressed }) => [
            styles.closeBtn,
            { backgroundColor: dark ? "#3a3a3c" : "#e8e8ed", opacity: pressed ? 0.6 : 1 },
          ]}
        >
          <Ionicons name="close" size={16} color={dark ? TEXT_DARK : TEXT_LIGHT} />
        </Pressable>
      </View>

      {/* Seção: Aparência */}
      <Text style={[styles.sectionLabel, { color: dark ? MUTED_DARK : MUTED_LIGHT }]}>
        APARÊNCIA
      </Text>
      <View style={[styles.card, { backgroundColor: dark ? CARD_DARK : CARD_LIGHT }]}>
        <Row icon="moon-outline" label="Tema escuro" dark={dark}>
          <Switch
            value={dark}
            onValueChange={toggleDarkMode}
            trackColor={{ false: "#d1d1d6", true: ACCENT }}
            thumbColor="#fff"
          />
        </Row>

        <Row icon="text-outline" label="Tamanho da fonte" dark={dark}>
          <View style={styles.fontRow}>
            <StepButton label="−" onPress={decFont} dark={dark} />
            <Text style={[styles.fontValue, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>
              {(state.fontScale || 1).toFixed(1)}×
            </Text>
            <StepButton label="+" onPress={incFont} dark={dark} />
          </View>
        </Row>
      </View>

      {/* Seção: Leitor de Tela */}
      <Text style={[styles.sectionLabel, { color: dark ? MUTED_DARK : MUTED_LIGHT }]}>
        LEITOR DE TELA
      </Text>
      <View style={[styles.card, { backgroundColor: dark ? CARD_DARK : CARD_LIGHT }]}>
        <Row icon="volume-high-outline" label="Narração de voz" dark={dark}>
          <Switch
            value={!!state.ttsEnabled}
            onValueChange={toggleTTS}
            trackColor={{ false: "#d1d1d6", true: ACCENT }}
            thumbColor="#fff"
          />
        </Row>

        <Row icon="speedometer-outline" label="Velocidade" dark={dark}>
          <View style={styles.fontRow}>
            <StepButton label="−" onPress={decRate} dark={dark} />
            <Text style={[styles.fontValue, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>
              {(state.ttsRate || 1.0).toFixed(1)}×
            </Text>
            <StepButton label="+" onPress={incRate} dark={dark} />
          </View>
        </Row>

        <View style={[styles.row, { borderBottomWidth: 0 }]}>
          <TouchableOpacity
            onPress={speakSample}
            activeOpacity={0.75}
            accessibilityLabel="Ouvir texto de exemplo"
            style={[
              styles.ttsBtn,
              { backgroundColor: dark ? "#3a3a3c" : "#e8e8ed", flex: 1, marginRight: 8 },
            ]}
          >
            <Ionicons name="play-outline" size={15} color={dark ? TEXT_DARK : TEXT_LIGHT} style={{ marginRight: 5 }} />
            <Text style={[styles.ttsBtnText, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>
              Ouvir exemplo
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={stopSpeaking}
            activeOpacity={0.75}
            accessibilityLabel="Parar narração"
            style={[styles.ttsBtn, { backgroundColor: dark ? "#3a3a3c" : "#e8e8ed", flex: 1 }]}
          >
            <Ionicons name="stop-outline" size={15} color={dark ? TEXT_DARK : TEXT_LIGHT} style={{ marginRight: 5 }} />
            <Text style={[styles.ttsBtnText, { color: dark ? TEXT_DARK : TEXT_LIGHT }]}>
              Parar
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Restaurar padrões */}
      <TouchableOpacity
        onPress={handleReset}
        activeOpacity={0.75}
        accessibilityLabel="Restaurar configurações padrão"
        style={[styles.resetBtn, { borderColor: dark ? BORDER_DARK : BORDER_LIGHT }]}
      >
        <Ionicons name="refresh-outline" size={16} color={dark ? MUTED_DARK : MUTED_LIGHT} style={{ marginRight: 6 }} />
        <Text style={[styles.resetText, { color: dark ? MUTED_DARK : MUTED_LIGHT }]}>
          Restaurar padrões
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  sheet: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  handleWrap: {
    alignItems: "center",
    paddingTop: 10,
    paddingBottom: 4,
  },
  handle: {
    width: 36,
    height: 4,
    borderRadius: 2,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 14,
  },
  headerLeft: {
    flexDirection: "row",
    alignItems: "center",
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
    letterSpacing: 0.2,
  },
  closeBtn: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  sectionLabel: {
    fontSize: 11,
    fontWeight: "600",
    letterSpacing: 0.8,
    marginBottom: 6,
    marginLeft: 4,
    marginTop: 16,
  },
  card: {
    borderRadius: 12,
    overflow: "hidden",
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  rowLeft: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  rowRight: {
    marginLeft: 12,
  },
  iconWrap: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  rowLabel: {
    fontSize: 15,
    fontWeight: "500",
  },
  fontRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  fontValue: {
    fontSize: 14,
    fontWeight: "600",
    minWidth: 38,
    textAlign: "center",
  },
  stepBtn: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
  },
  stepBtnText: {
    fontSize: 18,
    fontWeight: "600",
    lineHeight: 22,
  },
  ttsBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    height: 38,
    borderRadius: 8,
  },
  ttsBtnText: {
    fontSize: 13,
    fontWeight: "500",
  },
  resetBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 20,
    paddingVertical: 13,
    borderRadius: 12,
    borderWidth: StyleSheet.hairlineWidth,
  },
  resetText: {
    fontSize: 14,
    fontWeight: "500",
  },
});
