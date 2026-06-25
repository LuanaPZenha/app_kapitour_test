/**
 * Utilitário central de narração de voz (TTS) do Kapitour.
 *
 * Qualquer arquivo pode chamar `speak("texto")` sem precisar do contexto React.
 * O AccessibilityContext registra um getter de estado ao montar/atualizar,
 * então speak() sempre consulta ttsEnabled e ttsRate atuais.
 */

import * as Speech from "expo-speech";
import { Platform } from "react-native";

let _getState = () => ({ ttsEnabled: false, ttsRate: 1.0 });

/** Chamado pelo AccessibilityContext a cada mudança de estado. */
export function registerStateGetter(fn) {
  _getState = fn;
}

/**
 * Narra `text` se a narração estiver ativada.
 * Interrompe qualquer fala em andamento antes de iniciar.
 */
export function speak(text) {
  if (!text || !text.trim()) return;
  const { ttsEnabled, ttsRate } = _getState();
  if (!ttsEnabled) return;

  const rate = Math.max(0.5, Math.min(1.8, ttsRate || 1.0));

  if (Platform.OS === "web") {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text.trim());
    utter.lang = "pt-BR";
    utter.rate = rate;
    window.speechSynthesis.speak(utter);
    return;
  }

  Speech.stop();
  Speech.speak(text.trim(), { language: "pt-BR", rate });
}

/** Para qualquer narração em andamento. */
export function stopSpeaking() {
  if (Platform.OS === "web") {
    window.speechSynthesis?.cancel();
  } else {
    Speech.stop();
  }
}

/** Retorna verdadeiro se narração está ativa — útil para lógica condicional. */
export function isTTSEnabled() {
  return !!_getState().ttsEnabled;
}
