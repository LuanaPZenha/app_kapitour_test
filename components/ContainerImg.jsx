import React from "react";
import { View, StyleSheet } from "react-native";
import BrandLogo from "./BrandLogo";

export default function ContainerImg({ showTagline = true, compact = false }) {
  return (
    <View style={styles.wrapper}>
      <BrandLogo showTagline={showTagline} compact={compact} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    width: "100%",
    alignItems: "center",
  },
});
