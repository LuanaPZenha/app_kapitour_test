import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Animated,
  Easing,
} from "react-native";
import { useFonts } from "expo-font";
import Svg, {
  Circle,
  Path,
  G,
  Defs,
  LinearGradient as SvgGradient,
  Stop,
} from "react-native-svg";
import { colors } from "../theme/colors";
import { ACTIVE_BRAND_FONT, BRAND_FONT_CONFIG } from "../constants/brandFont";
import { CapybaraIcon } from "./CapybaraIcon";
import { AppMenuButtonInline } from "./AppDrawerMenu";
import { useAuth } from "../hooks/useAuth";

const { width: screenWidth } = Dimensions.get("window");

// ─────────────────────────────────────
// Ícone da bússola (estático — a animação fica no wrapper)
// ─────────────────────────────────────
export function CompassIcon({ size = 58 }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 72 72">
      <Defs>
        <SvgGradient id="ring" x1="0" y1="0" x2="1" y2="1">
          <Stop offset="0" stopColor="#ffffff" stopOpacity="0.55" />
          <Stop offset="1" stopColor={colors.accent} stopOpacity="0.9" />
        </SvgGradient>
        <SvgGradient id="north" x1="0.5" y1="0" x2="0.5" y2="1">
          <Stop offset="0" stopColor="#ff6b7f" />
          <Stop offset="1" stopColor={colors.primary} />
        </SvgGradient>
      </Defs>

      <Circle cx="36" cy="36" r="33" fill="rgba(255,255,255,0.07)" />
      <Circle cx="36" cy="36" r="33" stroke="url(#ring)" strokeWidth="1.8" fill="none" />

      {[-90, 0, 90, 180].map((angle) => (
        <Circle
          key={angle}
          cx={36 + 26 * Math.cos((angle * Math.PI) / 180)}
          cy={36 + 26 * Math.sin((angle * Math.PI) / 180)}
          r="1.8"
          fill="rgba(255,255,255,0.55)"
        />
      ))}

      <G>
        <Path d="M36 10 L41.5 36 L36 31 L30.5 36 Z" fill="url(#north)" />
        <Path d="M36 62 L30.5 36 L36 41 L41.5 36 Z" fill="rgba(255,255,255,0.28)" />
      </G>

      <Circle cx="36" cy="36" r="4.5" fill={colors.accent} />
      <Circle cx="36" cy="36" r="2" fill="#fff" />

      <Path
        d="M36 18 C33 24 33 30 36 34 C39 30 39 24 36 18 Z"
        fill="none"
        stroke="rgba(255,255,255,0.35)"
        strokeWidth="1.2"
      />
    </Svg>
  );
}

// ─────────────────────────────────────
// Cursor piscante para o efeito typewriter
// ─────────────────────────────────────
function Cursor({ style }) {
  const blink = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(blink, { toValue: 0, duration: 400, useNativeDriver: true }),
        Animated.timing(blink, { toValue: 1, duration: 400, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  return <Animated.Text style={[style, { opacity: blink }]}>|</Animated.Text>;
}

// ─────────────────────────────────────
// Logo principal
// ─────────────────────────────────────
export default function BrandLogo({ showTagline = true, compact = false, showMascot = true }) {
  const { isLogged } = useAuth();
  const fontConfig = BRAND_FONT_CONFIG[ACTIVE_BRAND_FONT];

  const [fontsLoaded] = useFonts({
    Azonix: require("../assets/fonts/Azonix.otf"),
    Headache: require("../assets/fonts/Headache.ttf"),
  });

  // ── Typewriter state ──
  const fullWordmark = fontConfig.wordmark;          // "KAPITOUR"
  const accentFrom = fontConfig.accentFrom;          // 3 → "KAP" | "ITOUR"
  const mainPart = fullWordmark.slice(0, accentFrom);
  const accentPart = fullWordmark.slice(accentFrom);

  const [typedMain, setTypedMain] = useState("");
  const [typedAccent, setTypedAccent] = useState("");
  const [typewriterDone, setTypewriterDone] = useState(false);

  // ── Animation values ──
  const compassSpin = useRef(new Animated.Value(0)).current;
  const compassScale = useRef(new Animated.Value(0.7)).current;
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const mascotSlide = useRef(new Animated.Value(20)).current;
  const mascotOpacity = useRef(new Animated.Value(0)).current;

  // ── Derived interpolations ──
  const spinDeg = compassSpin.interpolate({
    inputRange: [0, 1],
    outputRange: ["0deg", "360deg"],
  });

  useEffect(() => {
    if (!fontsLoaded) return;

    // 1. Bússola entra com spin + scale
    Animated.parallel([
      Animated.timing(compassSpin, {
        toValue: 1,
        duration: 700,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.spring(compassScale, {
        toValue: 1,
        friction: 5,
        tension: 80,
        useNativeDriver: true,
      }),
    ]).start(() => {
      // 2. Pulso contínuo após entrada
      Animated.loop(
        Animated.sequence([
          Animated.timing(compassScale, {
            toValue: 1.07,
            duration: 1800,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(compassScale, {
            toValue: 1,
            duration: 1800,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ])
      ).start();
    });

    // 3. Typewriter do nome (começa junto com a bússola)
    let i = 0;
    const msPerChar = compact ? 55 : 70;
    const iv = setInterval(() => {
      i += 1;
      const current = fullWordmark.slice(0, i);
      if (i <= mainPart.length) {
        setTypedMain(current);
        setTypedAccent("");
      } else {
        setTypedMain(mainPart);
        setTypedAccent(current.slice(mainPart.length));
      }
      if (i >= fullWordmark.length) {
        clearInterval(iv);
        setTypewriterDone(true);
      }
    }, msPerChar);

    // 4. Mascote desliza + aparece
    if (!compact) {
      Animated.parallel([
        Animated.timing(mascotOpacity, {
          toValue: 1,
          duration: 500,
          delay: 400,
          useNativeDriver: true,
        }),
        Animated.spring(mascotSlide, {
          toValue: 0,
          friction: 6,
          tension: 60,
          delay: 400,
          useNativeDriver: true,
        }),
      ]).start();
    }

    return () => clearInterval(iv);
  }, [fontsLoaded]);

  // 5. Tagline faz fade-in após typewriter
  useEffect(() => {
    if (!typewriterDone || compact) return;
    Animated.timing(taglineOpacity, {
      toValue: 1,
      duration: 500,
      delay: 100,
      useNativeDriver: true,
    }).start();
  }, [typewriterDone, compact]);

  if (!fontsLoaded) {
    return <View style={[styles.placeholder, compact && styles.placeholderCompact]} />;
  }

  const iconSize = compact ? 46 : isLogged ? 50 : 58;
  const mascotSize = compact ? 40 : isLogged ? 44 : 54;
  const titleSize = compact
    ? fontConfig.titleSize.compact
    : isLogged
      ? fontConfig.titleSize.normal - 3
      : fontConfig.titleSize.normal;
  const sloganSize = compact ? 11 : isLogged ? 12 : 13;
  const showMascotNow = showMascot && !compact && (!isLogged || screenWidth >= 360);

  return (
    <View style={[styles.container, compact && styles.containerCompact]}>
      {isLogged ? (
        <View style={styles.menuAbsolute} pointerEvents="box-none">
          <AppMenuButtonInline />
        </View>
      ) : null}

      <View style={[styles.row, isLogged && styles.rowWithMenu]}>
        {/* Bússola animada */}
        <Animated.View
          style={[
            styles.iconWrap,
            {
              transform: [{ rotate: spinDeg }, { scale: compassScale }],
            },
          ]}
        >
          <CompassIcon size={iconSize} />
        </Animated.View>

        {/* Bloco de texto */}
        <View style={styles.textBlock}>
          {/* Wordmark com typewriter */}
          <View style={styles.wordmarkRow}>
            <Text
              style={[
                styles.wordmark,
                {
                  fontFamily: fontConfig.family,
                  fontSize: titleSize,
                  letterSpacing: isLogged ? fontConfig.titleLetterSpacing * 0.85 : fontConfig.titleLetterSpacing,
                },
              ]}
              numberOfLines={1}
              adjustsFontSizeToFit
              minimumFontScale={0.82}
            >
              {typedMain}
              <Text style={styles.wordmarkAccent}>{typedAccent}</Text>
            </Text>
            {/* Cursor piscante enquanto escreve */}
            {!typewriterDone ? (
              <Cursor
                style={[
                  styles.wordmark,
                  {
                    fontSize: titleSize,
                    color: colors.accent,
                    marginLeft: 1,
                  },
                ]}
              />
            ) : null}
          </View>

          {/* Tagline com fade-in */}
          {showTagline && !compact ? (
            <Animated.Text
              style={[
                styles.slogan,
                { fontSize: sloganSize, opacity: taglineOpacity },
              ]}
            >
              Seu guia turístico digital de{" "}
              <Text
                style={[
                  styles.sloganCity,
                  {
                    fontFamily: fontConfig.family,
                    letterSpacing: fontConfig.taglineLetterSpacing,
                  },
                ]}
              >
                Maricá
              </Text>
            </Animated.Text>
          ) : null}
        </View>

        {/* Mascote com slide + fade */}
        {showMascotNow ? (
          <Animated.View
            style={[
              styles.mascotWrap,
              {
                opacity: mascotOpacity,
                transform: [{ translateY: mascotSlide }],
              },
            ]}
          >
            <CapybaraIcon size={mascotSize} />
          </Animated.View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    alignItems: "center",
    paddingVertical: 4,
    position: "relative",
  },
  containerCompact: {
    paddingVertical: 0,
  },
  placeholder: {
    width: screenWidth,
    height: 88,
  },
  placeholderCompact: {
    height: 58,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    paddingHorizontal: 16,
    maxWidth: "100%",
  },
  rowWithMenu: {
    paddingLeft: 48,
    paddingRight: 10,
    justifyContent: "flex-start",
  },
  menuAbsolute: {
    position: "absolute",
    left: 10,
    top: 0,
    bottom: 0,
    justifyContent: "center",
    zIndex: 2,
  },
  iconWrap: {
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    elevation: 6,
  },
  mascotWrap: {
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 4,
    marginLeft: 2,
  },
  textBlock: {
    justifyContent: "center",
    flexShrink: 1,
    flexGrow: 0,
    maxWidth: screenWidth - 180,
  },
  wordmarkRow: {
    flexDirection: "row",
    alignItems: "center",
    flexShrink: 1,
  },
  wordmark: {
    color: "#ffffff",
    includeFontPadding: false,
  },
  wordmarkAccent: {
    color: colors.accent,
  },
  slogan: {
    color: "rgba(255, 255, 255, 0.78)",
    marginTop: 4,
    lineHeight: 16,
    fontWeight: "600",
    includeFontPadding: false,
    flexShrink: 1,
  },
  sloganCity: {
    color: colors.accent,
  },
});
