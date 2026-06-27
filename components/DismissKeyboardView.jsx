import React from "react";
import { Keyboard, Platform, TouchableWithoutFeedback } from "react-native";

/**
 * Fecha o teclado ao tocar fora dos campos (mobile).
 * No web, não usa TouchableWithoutFeedback — evita perder foco ao digitar.
 */
export default function DismissKeyboardView({ children }) {
  if (Platform.OS === "web") {
    return children;
  }

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
      {children}
    </TouchableWithoutFeedback>
  );
}
