// src/accessibility/theming.js
import { StyleSheet } from 'react-native';

// Paletas base e para condições de daltonismo (valores ajustáveis)
export const basePalette = {
  background: '#FFFFFF',
  text: '#111111',
  primary: '#0A84FF',
  accent: '#FFD60A',
};

export const colorBlindPalettes = {
  none: basePalette,
  protanopia: {
    background: '#FFFFFF',
    text: '#0F1720',
    primary: '#0066CC',
    accent: '#E6A800',
  },
  deuteranopia: {
    background: '#FFFFFF',
    text: '#0F1720',
    primary: '#0055AA',
    accent: '#E68A00',
  },
  tritanopia: {
    background: '#FFFFFF',
    text: '#0F1720',
    primary: '#0A84FF',
    accent: '#B07AFF',
  },
};

// makeStyles: função principal que gera styles dinâmicos a partir do estado de acessibilidade
export function makeStyles(state = {}) {
  const palette = colorBlindPalettes[state.colorBlindMode || 'none'];
  const fontScale = typeof state.fontScale === 'number' ? state.fontScale : 1.0;
  const spacingMultiplier = state.spacingMode ? 1.25 : 1.0;

  return StyleSheet.create({
    // Container principal adaptável
    appBackground: {
      flex: 1,
      backgroundColor: state.darkMode ? '#0B0B0B' : (state.highContrast ? '#000000' : palette.background),
      padding: 12 * spacingMultiplier,
    },

    // Texto padrão
    text: {
      color: state.highContrast ? '#FFFF00' : (state.darkMode ? '#FFFFFF' : palette.text),
      fontSize: 16 * fontScale,
      lineHeight: Math.round(22 * fontScale * spacingMultiplier),
    },

    // Títulos
    title: {
      fontSize: 20 * fontScale,
      fontWeight: '700',
      color: state.highContrast ? '#FFFF00' : (state.darkMode ? '#FFFFFF' : palette.text),
    },

    // Links / botões de texto
    link: {
      textDecorationLine: 'underline',
      color: palette.primary,
      fontSize: 16 * fontScale,
    },

    // Peças menores (legendas, labels)
    small: {
      fontSize: 12 * fontScale,
      color: state.darkMode ? '#DDD' : palette.text,
    },

    // Card padrão
    card: {
      backgroundColor: state.darkMode ? '#111214' : '#FFFFFF',
      padding: 12 * spacingMultiplier,
      borderRadius: 10,
    },

    // Foco visível para acessibilidade (quando usar accessibilityState etc)
    focusOutline: {
      borderWidth: 2,
      borderColor: state.highContrast ? '#FFFF00' : (state.darkMode ? '#0A84FF' : '#0A84FF'),
    },

    // Ajustes para imagens que você queira adaptar: contêiner que pode ter filtros externos
    imageWrapper: {
      overflow: 'hidden',
      borderRadius: 8,
    },

    // Botões padrão
    button: {
      paddingVertical: 10 * spacingMultiplier,
      paddingHorizontal: 14 * spacingMultiplier,
      borderRadius: 10,
      backgroundColor: palette.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonText: {
      color: '#fff',
      fontSize: 16 * fontScale,
      fontWeight: '600',
    },

    // Pequeno utilitário para textos com alto contraste (ex.: badges)
    badge: {
      backgroundColor: state.highContrast ? '#000' : palette.accent,
      paddingHorizontal: 8,
      paddingVertical: 4,
      borderRadius: 6,
    },
    badgeText: {
      color: state.highContrast ? '#FFFF00' : '#000',
      fontSize: 12 * fontScale,
      fontWeight: '700',
    },
  });
}
