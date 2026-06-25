/**
 * AppAlert — substituto estilizado para Alert.alert().
 *
 * Uso (qualquer componente):
 *   import { useAppAlert } from "../components/AppAlert";
 *   const { showAlert } = useAppAlert();
 *   showAlert({
 *     title: "Sair",
 *     message: "Tem certeza?",
 *     icon: "log-out-outline",          // nome Ionicons (opcional)
 *     iconColor: colors.primary,        // cor do ícone (opcional)
 *     buttons: [
 *       { text: "Cancelar", style: "cancel" },
 *       { text: "Sair", style: "destructive", onPress: handleLogout },
 *     ],
 *   });
 *
 * Registrar uma vez na raiz:
 *   import { AppAlertHost } from "../components/AppAlert";
 *   // dentro do JSX do App.js:
 *   <AppAlertHost />
 */

import React, { createContext, useContext, useState, useCallback } from "react";
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Pressable,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

// ─────────────────────────────────────
// Contexto
// ─────────────────────────────────────
const AlertContext = createContext(null);

export function AppAlertProvider({ children }) {
  const [config, setConfig] = useState(null);

  const showAlert = useCallback((cfg) => {
    setConfig(cfg);
  }, []);

  const dismiss = useCallback(() => {
    setConfig(null);
  }, []);

  const handlePress = useCallback(
    (btn) => {
      dismiss();
      btn?.onPress?.();
    },
    [dismiss]
  );

  return (
    <AlertContext.Provider value={{ showAlert }}>
      {children}
      <Modal
        visible={!!config}
        transparent
        animationType="fade"
        statusBarTranslucent
        onRequestClose={dismiss}
      >
        <Pressable style={styles.overlay} onPress={dismiss}>
          <Pressable style={[styles.box, shadows.elevated]} onPress={() => {}}>
            {/* Ícone opcional */}
            {config?.icon ? (
              <View
                style={[
                  styles.iconWrap,
                  { backgroundColor: `${config.iconColor || colors.primary}22` },
                ]}
              >
                <Ionicons
                  name={config.icon}
                  size={30}
                  color={config.iconColor || colors.primary}
                />
              </View>
            ) : null}

            {/* Barra de acento */}
            <View style={styles.accentBar} />

            {/* Título */}
            {config?.title ? (
              <Text style={styles.title}>{config.title}</Text>
            ) : null}

            {/* Mensagem */}
            {config?.message ? (
              <Text style={styles.message}>{config.message}</Text>
            ) : null}

            {/* Botões */}
            <View
              style={[
                styles.buttonsRow,
                config?.buttons?.length === 1 && styles.buttonsSingle,
              ]}
            >
              {(config?.buttons || [{ text: "OK" }]).map((btn, i) => (
                <TouchableOpacity
                  key={i}
                  style={[
                    styles.btn,
                    btn.style === "cancel" && styles.btnCancel,
                    btn.style === "destructive" && styles.btnDestructive,
                    (!btn.style || btn.style === "default") && styles.btnDefault,
                    config?.buttons?.length === 1 && styles.btnFull,
                  ]}
                  activeOpacity={0.75}
                  onPress={() => handlePress(btn)}
                >
                  <Text
                    style={[
                      styles.btnText,
                      btn.style === "cancel" && styles.btnTextCancel,
                      btn.style === "destructive" && styles.btnTextDestructive,
                    ]}
                  >
                    {btn.text}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </AlertContext.Provider>
  );
}

/** Hook para acionar o alert de qualquer componente. */
export function useAppAlert() {
  const ctx = useContext(AlertContext);
  if (!ctx) throw new Error("useAppAlert deve ser usado dentro de AppAlertProvider");
  return ctx;
}

/** Componente vazio — mantido por compatibilidade caso queira importar separado. */
export function AppAlertHost() {
  return null;
}

// ─────────────────────────────────────
// Estilos
// ─────────────────────────────────────
const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.62)",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.xl,
  },
  box: {
    width: "100%",
    maxWidth: 360,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg + 4,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    overflow: "hidden",
    paddingTop: spacing.xl,
    paddingBottom: spacing.md,
    paddingHorizontal: spacing.lg,
    alignItems: "center",
  },
  accentBar: {
    width: 36,
    height: 3,
    borderRadius: 2,
    backgroundColor: colors.primary,
    marginBottom: spacing.md,
  },
  iconWrap: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  title: {
    ...typography.subtitle,
    fontSize: 18,
    textAlign: "center",
    marginBottom: spacing.xs,
  },
  message: {
    ...typography.body,
    textAlign: "center",
    lineHeight: 21,
    marginBottom: spacing.xl,
  },
  buttonsRow: {
    flexDirection: "row",
    gap: spacing.sm,
    width: "100%",
  },
  buttonsSingle: {
    justifyContent: "center",
  },
  btn: {
    flex: 1,
    paddingVertical: spacing.sm + 2,
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
  },
  btnFull: {
    flex: 1,
  },
  btnDefault: {
    backgroundColor: colors.primary,
  },
  btnCancel: {
    backgroundColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  btnDestructive: {
    backgroundColor: "rgba(200,51,73,0.18)",
    borderWidth: 1,
    borderColor: "rgba(200,51,73,0.4)",
  },
  btnText: {
    ...typography.button,
    fontSize: 14,
    color: colors.text,
  },
  btnTextCancel: {
    color: colors.textSecondary,
    fontWeight: "500",
  },
  btnTextDestructive: {
    color: colors.primary,
    fontWeight: "700",
  },
});
