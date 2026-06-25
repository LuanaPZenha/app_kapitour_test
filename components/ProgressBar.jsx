import React from "react";
import { View, Text } from "react-native";

export default function ProgressBar({ percent = 0, badgeText }) {
  return (
    <View style={{ width: "100%" }}>
      <Text style={{ color: "#fff", fontWeight: "bold", fontSize: 16, textAlign: "center", marginBottom: 8 }}>
        Progresso: {Math.round(percent)}%
      </Text>
      <View style={{ width: "100%", height: 10, backgroundColor: "rgba(255,255,255,0.2)", borderRadius: 6, overflow: "hidden" }}>
        <View style={{ height: "100%", width: `${percent}%`, backgroundColor: "#f7a000" }} />
      </View>
      {badgeText ? (
        <View style={{ alignSelf: "center", marginTop: 8, backgroundColor: "#2c2338", paddingVertical: 6, paddingHorizontal: 12, borderRadius: 999 }}>
          <Text style={{ color: "#fff", fontSize: 12, fontWeight: "bold" }}>{badgeText}</Text>
        </View>
      ) : null}
    </View>
  );
}