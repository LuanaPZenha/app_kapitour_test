import React, { useState } from "react";
import {
  View,
  Text,
  Image,
  ImageBackground,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import IconButton from "./IconButton";
import { colors } from "../theme/colors";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

function CardBackButton({ onBack }) {
  return (
    <IconButton
      name="arrow-back"
      onPress={onBack}
      accessibilityLabel="Voltar"
      style={styles.backButton}
    />
  );
}

function CardLoader({ variant = "default" }) {
  return (
    <View style={[styles.loaderBase, variant === "logo" && styles.loaderLogo]}>
      <ActivityIndicator size="large" color={colors.accent} />
    </View>
  );
}

export default function Card({
  imageUrl,
  imageSource,
  title,
  description,
  children,
  showBack,
  onBack,
  style,
  imageFit = "cover",
  imageHeight = 200,
  imageOpacity = 0.28,
  logoShape = "rounded",
}) {
  const resolvedSource = imageSource ? imageSource : imageUrl ? { uri: imageUrl } : null;
  const hasImage = !!resolvedSource;
  const [loaded, setLoaded] = useState(!hasImage);
  const isCircleLogo = logoShape === "circle";
  const cardStyle = [styles.card, shadows.card, style];

  if (hasImage && imageFit === "logo") {
    return (
      <View style={[cardStyle, styles.logoCard]}>
        {showBack ? <CardBackButton onBack={onBack} /> : null}

        <View style={[styles.logoArea, { height: imageHeight }]}>
          {!loaded ? <CardLoader variant="logo" /> : null}
          <View style={isCircleLogo ? styles.logoCircleFrame : styles.logoFrame}>
            <Image
              source={resolvedSource}
              style={isCircleLogo ? styles.logoCircleImage : styles.logoImage}
              resizeMode="contain"
              onLoadEnd={() => setLoaded(true)}
              accessibilityIgnoresInvertColors
            />
          </View>
        </View>

        <View style={styles.logoContent}>
          <View style={styles.logoTextBlock}>
            {title ? (
              <Text style={[styles.title, styles.logoTitle]} numberOfLines={1}>
                {title}
              </Text>
            ) : null}
            {description ? (
              <Text style={[styles.description, styles.logoDescription]} numberOfLines={3}>
                {description}
              </Text>
            ) : null}
          </View>
          <View style={styles.logoActions}>{children}</View>
        </View>
      </View>
    );
  }

  if (hasImage && imageFit === "overlay") {
    return (
      <View style={[cardStyle, styles.logoCard, { minHeight: imageHeight }]}>
        {showBack ? <CardBackButton onBack={onBack} /> : null}
        {!loaded ? <CardLoader variant="logo" /> : null}

        <Image
          source={resolvedSource}
          style={[styles.overlayImage, { opacity: imageOpacity }]}
          resizeMode="contain"
          onLoadEnd={() => setLoaded(true)}
          accessibilityIgnoresInvertColors
        />

        <View style={styles.overlayContent}>
          {title ? <Text style={[styles.title, styles.overlayTitle]}>{title}</Text> : null}
          {description ? (
            <Text style={[styles.description, styles.overlayDescription]}>{description}</Text>
          ) : null}
          {children ? <View style={styles.overlayActions}>{children}</View> : null}
        </View>
      </View>
    );
  }

  if (hasImage && imageFit === "contain") {
    return (
      <View style={cardStyle}>
        {showBack ? <CardBackButton onBack={onBack} /> : null}

        <View style={[styles.imageArea, { height: imageHeight }]}>
          {!loaded ? <CardLoader /> : null}
          <Image
            source={resolvedSource}
            style={styles.containImage}
            resizeMode="contain"
            onLoadEnd={() => setLoaded(true)}
            accessibilityIgnoresInvertColors
          />
        </View>

        <View style={styles.content}>
          {title ? <Text style={styles.title}>{title}</Text> : null}
          {description ? <Text style={styles.description}>{description}</Text> : null}
          {children}
        </View>
      </View>
    );
  }

  return (
    <View style={cardStyle}>
      {showBack ? <CardBackButton onBack={onBack} /> : null}
      {hasImage ? (
        <ImageBackground
          source={resolvedSource}
          style={styles.coverImage}
          imageStyle={{ resizeMode: imageFit }}
          onLoadEnd={() => setLoaded(true)}
        >
          {!loaded ? <CardLoader /> : null}
          <View style={[styles.content, styles.contentOverlay]}>
            {title ? <Text style={styles.title}>{title}</Text> : null}
            {description ? <Text style={styles.description}>{description}</Text> : null}
            {children}
          </View>
        </ImageBackground>
      ) : (
        <View style={styles.plainContent}>
          {title ? <Text style={styles.title}>{title}</Text> : null}
          {description ? <Text style={styles.description}>{description}</Text> : null}
          {children}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: "100%",
    borderRadius: radius.lg,
    overflow: "hidden",
    position: "relative",
    backgroundColor: colors.cardBg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  backButton: {
    position: "absolute",
    top: spacing.sm,
    left: spacing.sm,
    zIndex: 3,
  },
  overlayImage: {
    ...StyleSheet.absoluteFillObject,
    width: "100%",
    height: "100%",
    zIndex: 1,
  },
  overlayContent: {
    ...StyleSheet.absoluteFillObject,
    padding: spacing.lg,
    zIndex: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  overlayTitle: {
    textAlign: "center",
    color: colors.accent,
    textShadowColor: "rgba(0, 0, 0, 0.75)",
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 5,
  },
  overlayDescription: {
    textAlign: "center",
    color: colors.textSecondary,
    textShadowColor: "rgba(0, 0, 0, 0.75)",
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 5,
    marginBottom: spacing.sm,
  },
  overlayActions: {
    width: "100%",
    alignItems: "center",
    marginTop: spacing.xxs,
  },
  logoCard: {
    flexDirection: "column",
  },
  logoArea: {
    width: "100%",
    backgroundColor: colors.cardBg,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSubtle,
  },
  logoFrame: {
    width: "100%",
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
    borderRadius: radius.md,
    overflow: "hidden",
  },
  logoImage: {
    width: "100%",
    height: "100%",
    maxHeight: 88,
  },
  logoCircleFrame: {
    width: 88,
    height: 88,
    borderRadius: 44,
    borderWidth: 3,
    borderColor: colors.partnerAccent,
    backgroundColor: colors.badgeBg,
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden",
  },
  logoCircleImage: {
    width: "88%",
    height: "88%",
  },
  logoContent: {
    flex: 1,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.sm + 2,
    paddingBottom: spacing.md,
    backgroundColor: colors.cardBg,
  },
  logoTextBlock: {
    flex: 1,
    justifyContent: "flex-start",
  },
  logoActions: {
    width: "100%",
    minHeight: 44,
    justifyContent: "center",
  },
  logoTitle: {
    color: colors.accent,
    textAlign: "center",
    fontSize: 18,
    lineHeight: 24,
    marginBottom: spacing.xs - 2,
  },
  logoDescription: {
    textAlign: "center",
    fontSize: 13,
    lineHeight: 19,
    minHeight: 57,
  },
  imageArea: {
    width: "100%",
    backgroundColor: colors.bgDark,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  containImage: {
    width: "100%",
    height: "100%",
  },
  coverImage: {
    width: "100%",
    minHeight: 160,
  },
  loaderBase: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.overlay,
    zIndex: 2,
  },
  loaderLogo: {
    backgroundColor: colors.cardBg,
    zIndex: 3,
  },
  content: {
    padding: spacing.md,
    backgroundColor: colors.overlay,
  },
  plainContent: {
    padding: spacing.md,
    backgroundColor: colors.cardBg,
  },
  contentOverlay: {
    flex: 1,
    justifyContent: "flex-end",
  },
  title: {
    ...typography.subtitle,
    fontSize: 20,
    marginBottom: spacing.xs - 2,
  },
  description: {
    ...typography.body,
    marginBottom: spacing.sm,
  },
});
