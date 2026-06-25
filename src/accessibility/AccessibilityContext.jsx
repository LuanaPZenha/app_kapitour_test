import React, { createContext, useContext, useEffect, useState } from 'react';
import { Appearance, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { registerStateGetter } from './tts';

const STORAGE_KEY = '@accessibility_prefs';

// estado padrão
const defaultState = {
  darkMode: Appearance.getColorScheme() === 'dark',
  fontScale: 1.0,
  ttsBuffer: '',
  ttsRate: 1.0,
  ttsEnabled: false,
};

const AccessibilityContext = createContext({
  state: defaultState,
  update: () => {},
  reset: async () => {},
  ready: false,
});

export const AccessibilityProvider = ({ children }) => {
  const [state, setState] = useState(defaultState);
  const [ready, setReady] = useState(false);

  // carrega prefs do armazenamento
  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          setState(prev => ({ ...prev, ...parsed }));
        }
      } catch (e) {
        console.warn('Failed to load accessibility prefs', e);
      } finally {
        setReady(true);
      }
    })();
  }, []);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    const styleId = 'a11y-styles';
    let tag = document.getElementById(styleId);
    if (!tag) {
      tag = document.createElement('style');
      tag.id = styleId;
      tag.type = 'text/css';
      tag.appendChild(document.createTextNode(`
        :root{ --font-scale: 1; --base-font-size: calc(16px * var(--font-scale)); }
        body{ font-size: var(--base-font-size); }
        .a11y-dark { background:#0b0b0b !important; color:#fff !important; }
      `));
      document.head.appendChild(tag);
    }
  }, []);

  // salva prefs quando state muda
  useEffect(() => {
    (async () => {
      try {
        await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch (e) {
        console.warn('Failed to save accessibility prefs', e);
      }
    })();
  }, [state]);

  // aplica classes/variáveis no DOM (web)
  useEffect(() => {
    if (Platform.OS !== 'web') return;
    try {
      const root = document.documentElement;
      const body = document.body;
      if (!root || !body) return;

      const scale = state.fontScale || 1;
      root.style.setProperty('--font-scale', String(scale));
      

      root.classList.toggle('a11y-dark', !!state.darkMode);

      

      
    } catch (e) {}
  }, [state.darkMode, state.fontScale]);

  // Mantém o getter do TTS sincronizado com o estado atual
  useEffect(() => {
    registerStateGetter(() => state);
  }, [state]);

  const update = updates => setState(prev => ({ ...prev, ...updates }));

  const reset = async () => {
    const initial = { ...defaultState, darkMode: Appearance.getColorScheme() === 'dark' };
    setState(initial);
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.warn('Failed to remove accessibility prefs', e);
    }
  };

  return (
    <AccessibilityContext.Provider value={{ state, update, reset, ready }}>
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => {
  const ctx = useContext(AccessibilityContext);
  if (!ctx) throw new Error('useAccessibility must be used within AccessibilityProvider');
  return ctx;
};
