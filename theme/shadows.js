import { Platform } from "react-native";

/** Sombras sutis — profundidade sem competir com o gradiente da marca. */
export const shadows = {
  card: Platform.select({
    ios: {
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.22,
      shadowRadius: 8,
    },
    android: { elevation: 4 },
    default: {},
  }),
  elevated: Platform.select({
    ios: {
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.28,
      shadowRadius: 12,
    },
    android: { elevation: 8 },
    default: {},
  }),
  soft: Platform.select({
    ios: {
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.14,
      shadowRadius: 4,
    },
    android: { elevation: 2 },
    default: {},
  }),
  /** Sombra colorida — usada em botões primários e FABs para profundidade com identidade. */
  brand: Platform.select({
    ios: {
      shadowColor: "#c83349",
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.38,
      shadowRadius: 10,
    },
    android: { elevation: 6 },
    default: {},
  }),
  /** Sombra de acento dourado — para elementos de destaque/badge. */
  accent: Platform.select({
    ios: {
      shadowColor: "#f7a000",
      shadowOffset: { width: 0, height: 3 },
      shadowOpacity: 0.3,
      shadowRadius: 7,
    },
    android: { elevation: 5 },
    default: {},
  }),
};
