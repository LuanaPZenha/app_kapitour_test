import React, { useState } from "react";
import { TouchableOpacity, View, Modal, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import AccessibilityPanel from "./AccessibilityPanel";
import { useAccessibility } from "./AccessibilityContext";

const ACCENT = "#c83349";

export default function FloatingAccessibilityButton() {
  const [open, setOpen] = useState(false);
  const { state } = useAccessibility();
  const insets = useSafeAreaInsets();

  const bottomPosition = insets.bottom + 16;

  return (
    <>
      <TouchableOpacity
        accessibilityLabel="Abrir configurações de acessibilidade"
        accessibilityRole="button"
        activeOpacity={0.85}
        onPress={() => setOpen(true)}
        style={[styles.button, { bottom: bottomPosition }]}
      >
        <Ionicons name="accessibility-outline" size={24} color="#fff" />
      </TouchableOpacity>

      <Modal
        visible={open}
        animationType="slide"
        onRequestClose={() => setOpen(false)}
        transparent
        statusBarTranslucent
      >
        <TouchableOpacity
          style={styles.backdrop}
          activeOpacity={1}
          onPress={() => setOpen(false)}
        >
          <View onStartShouldSetResponder={() => true}>
            <AccessibilityPanel onClose={() => setOpen(false)} />
          </View>
        </TouchableOpacity>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  button: {
    position: "absolute",
    right: 18,
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: ACCENT,
    justifyContent: "center",
    alignItems: "center",
    elevation: 8,
    shadowColor: ACCENT,
    shadowOpacity: 0.45,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    zIndex: 99999,
  },
  backdrop: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(0,0,0,0.4)",
  },
});
