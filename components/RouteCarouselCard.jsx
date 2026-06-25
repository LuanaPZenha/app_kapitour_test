import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import PressableScale from "./PressableScale";
import IconButton from "./IconButton";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

export default function RouteCarouselCard({
  nome,
  imagem,
  categorias = [],
  isFavorito,
  onPress,
  onToggleFavorito,
}) {
  return (
    <View style={[styles.card, shadows.elevated]}>
      <PressableScale
        onPress={onPress}
        accessibilityLabel={`Rota ${nome}`}
        accessibilityHint="Abre detalhes da rota"
        contentStyle={styles.pressableFill}
      >
        {imagem ? (
          <Image source={{ uri: imagem }} style={styles.image} accessibilityIgnoresInvertColors />
        ) : (
          <View style={styles.placeholder}>
            <Ionicons name="map-outline" size={40} color={colors.accent} />
          </View>
        )}

        <LinearGradient {...gradients.overlayDark} style={styles.gradient}>
          <View style={styles.infoContainer}>
            <Text style={styles.nome} numberOfLines={2}>
              {nome}
            </Text>
            <View style={styles.categoriesContainer}>
              {categorias.slice(0, 2).map((categoria, idx) => (
                <View key={`${categoria}-${idx}`} style={styles.categoryTag}>
                  <Text style={styles.categoryText}>{categoria}</Text>
                </View>
              ))}
              {categorias.length > 2 ? (
                <Text style={styles.moreCategories}>+{categorias.length - 2}</Text>
              ) : null}
            </View>
          </View>
        </LinearGradient>
      </PressableScale>

      <IconButton
        name={isFavorito ? "heart" : "heart-outline"}
        onPress={onToggleFavorito}
        accessibilityLabel={isFavorito ? "Remover dos favoritos" : "Adicionar aos favoritos"}
        color={isFavorito ? colors.primary : colors.text}
        style={styles.favoriteButton}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 180,
    height: 240,
    borderRadius: radius.md,
    overflow: "hidden",
    position: "relative",
    backgroundColor: colors.cardBg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  pressableFill: {
    flex: 1,
    width: "100%",
    height: "100%",
  },
  image: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  placeholder: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceElevated,
  },
  gradient: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "52%",
    paddingHorizontal: spacing.sm,
    paddingBottom: spacing.sm,
    justifyContent: "flex-end",
  },
  infoContainer: {
    width: "100%",
  },
  nome: {
    ...typography.subtitle,
    fontSize: 17,
    marginBottom: spacing.xs - 2,
  },
  categoriesContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
  },
  categoryTag: {
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    paddingHorizontal: spacing.xs,
    paddingVertical: spacing.xxs,
    borderRadius: radius.pill,
    marginRight: spacing.xs - 2,
    marginBottom: spacing.xxs,
  },
  categoryText: {
    color: colors.inputText,
    fontSize: 10,
    fontWeight: "600",
  },
  moreCategories: {
    color: colors.text,
    fontSize: 10,
    marginLeft: spacing.xxs,
  },
  favoriteButton: {
    position: "absolute",
    top: spacing.xs + 2,
    right: spacing.xs + 2,
    zIndex: 10,
  },
});
