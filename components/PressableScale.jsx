import React from "react";
import { Pressable } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from "react-native-reanimated";
import { speak } from "../src/accessibility/tts";

const SPRING = { damping: 18, stiffness: 320, mass: 0.35 };

/**
 * Feedback tátil sutil (scale 0.97) — padrão de apps premium sem alterar identidade visual.
 */
export default function PressableScale({
  children,
  onPress,
  disabled = false,
  style,
  contentStyle,
  accessibilityLabel,
  accessibilityRole = "button",
  accessibilityHint,
  hitSlop = 8,
  scaleTo = 0.97,
}) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Pressable
      onPress={(e) => {
        if (accessibilityLabel) speak(accessibilityLabel);
        onPress?.(e);
      }}
      disabled={disabled}
      hitSlop={hitSlop}
      accessibilityRole={accessibilityRole}
      accessibilityLabel={accessibilityLabel}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled }}
      onPressIn={() => {
        if (!disabled) scale.value = withSpring(scaleTo, SPRING);
      }}
      onPressOut={() => {
        scale.value = withSpring(1, SPRING);
      }}
      style={style}
    >
      <Animated.View style={[contentStyle, animatedStyle]}>{children}</Animated.View>
    </Pressable>
  );
}
