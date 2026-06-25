import React, { memo } from "react";
import { View, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";

function RatingStars({ value = 0, onChange, size = 26, color = "#f7a000", count = 5, style }) {
  return (
    <View style={[{ flexDirection: "row", justifyContent: "center", gap: 8, marginBottom: 16 }, style]}>
      {Array.from({ length: count }, (_, i) => i + 1).map((star) => (
        <TouchableOpacity key={star} onPress={() => onChange?.(star)}>
          <Ionicons name={value >= star ? "star" : "star-outline"} size={size} color={color} />
        </TouchableOpacity>
      ))}
    </View>
  );
}

export default memo(RatingStars);