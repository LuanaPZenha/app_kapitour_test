import React from "react";
import { Image } from "react-native";

const capybaraMascot = require("../assets/images/capybara-mascot.png");

export function CapybaraIcon({ size = 54 }) {
  return (
    <Image
      source={capybaraMascot}
      style={{ width: size, height: size }}
      resizeMode="contain"
    />
  );
}
