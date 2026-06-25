import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Animated,
  FlatList,
  Dimensions,
  Linking,
  StatusBar,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import Button from "../components/Button";
import Card from "../components/Card";
import SectionHeader from "../components/SectionHeader";
import { gradients } from "../theme/gradients";
import { spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import ContainerImg from "../components/ContainerImg";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import { useNavigation } from "@react-navigation/native";

const { width } = Dimensions.get("window");
const CARD_WIDTH = width * 0.6;
const CARD_NARROW = Math.min(width * 0.9, 360);
const PARTNER_CARD_HEIGHT = 280;
const PARTNER_LOGO_HEIGHT = 115;

const PATROCINADORES = [
  {
    id: "1",
    title: "AGM Maricá",
    description: "Parceria com a AGM Associação dos Guias de Turismo de Maricá.",
    imageUri: "https://github.com/Kapitour/Imgs-Padr-o/blob/main/home/agm.png?raw=true",
    buttonText: "Guias de Turismo",
    onPress: () =>
      Linking.openURL(
        "https://wa.me/5521971292030?text=Olá%20vim%20pela%20Kapitour%20e%20gostaria%20de%20contratar%20um%20guia%20de%20turismo!"
      ),
    style: "circle",
  },
  {
    id: "2",
    title: "Vassouras Tec",
    description: "Incubadora tecnológica da Univassouras.",
    imageUri: "https://github.com/Kapitour/Imgs-Padr-o/blob/main/VassourasT%C3%A9c.png?raw=true",
    buttonText: "Conheça Vassouras Tec",
    onPress: () => Linking.openURL("https://univassouras.edu.br/vassourastec/"),
    style: "incubadora",
  },
];

export default function Home() {
  const navigation = useNavigation();
  const [currentIndex, setCurrentIndex] = useState(0);

  const flatListRef = useRef(null);
  const scrollX = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const interval = setInterval(() => {
      const nextIndex = (currentIndex + 1) % PATROCINADORES.length;
      flatListRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      setCurrentIndex(nextIndex);
    }, 4000);

    return () => clearInterval(interval);
  }, [currentIndex]);

  const renderPatrocinador = ({ item, index }) => {
    const inputRange = [
      (index - 1) * CARD_WIDTH,
      index * CARD_WIDTH,
      (index + 1) * CARD_WIDTH,
    ];
    const scale = scrollX.interpolate({
      inputRange,
      outputRange: [0.92, 1, 0.92],
      extrapolate: "clamp",
    });

    return (
      <Animated.View
        style={{
          width: CARD_WIDTH,
          height: PARTNER_CARD_HEIGHT,
          marginHorizontal: spacing.xs,
          transform: [{ scale }],
        }}
      >
        <Card
          imageUrl={item.imageUri}
          imageFit="logo"
          logoShape={item.style === "circle" ? "circle" : "rounded"}
          imageHeight={PARTNER_LOGO_HEIGHT}
          title={item.title}
          description={item.description}
          style={{ height: "100%" }}
        >
          {item.buttonText ? (
            <Button icon="arrow-forward" onPress={item.onPress} fullWidth>
              {item.buttonText}
            </Button>
          ) : null}
        </Card>
      </Animated.View>
    );
  };

  return (
    <LinearGradient {...gradients.appBg} style={styles.safeArea}>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" backgroundColor="#c83349" />
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.topImageWrapper}>
            <ContainerImg />
          </View>

          <View style={styles.heroGreeting}>
            <View style={styles.heroTitleRow}>
              <View style={styles.heroIconWrap}>
                <Ionicons name="compass" size={22} color={colors.accent} />
              </View>
              <Text style={styles.heroTitle}>Bem-vindo a Maricá</Text>
            </View>
            <Text style={styles.heroSubtitle}>
              Explore praias, trilhas, gastronomia e muito mais pela cidade.
            </Text>
          </View>

          <View style={styles.content}>
            <View style={styles.section}>
              <SectionHeader
                title="Descubra no Mapa"
                subtitle="Pontos turísticos próximos de você, por categoria."
              />
              <Card
                title="Pontos turísticos próximos"
                description="Abra o mapa e explore por categoria"
                style={styles.narrowCard}
              >
                <Button icon="map" onPress={() => navigation.navigate("Mapa")} fullWidth>
                  Abrir Mapa
                </Button>
              </Card>
            </View>

            <View style={styles.section}>
              <SectionHeader
                title="Previsão do Tempo"
                subtitle="Planeje seu passeio com o clima atualizado de Maricá."
              />
              <Card
                imageUrl="https://github.com/Kapitour/Imgs-Padr-o/blob/main/KapiTempo/MASCULINO/AMENO%20-%20ENSOLARADO.png?raw=true"
                imageFit="overlay"
                imageHeight={240}
                imageOpacity={0.52}
                title="Clima em Maricá"
                description="Consulte a previsão do tempo e dicas para seu passeio!"
                style={[styles.narrowCard, styles.weatherCard]}
              >
                <Button icon="sunny-outline" onPress={() => navigation.navigate("Clima")} fullWidth>
                  Ver clima
                </Button>
              </Card>
            </View>

            <View style={styles.section}>
              <SectionHeader
                title="Nossos Parceiros"
                subtitle="Quem acredita e apoia o turismo em Maricá."
              />
              <View style={styles.carouselContainer}>
                <Animated.FlatList
                  ref={flatListRef}
                  data={PATROCINADORES}
                  keyExtractor={(item) => item.id}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  pagingEnabled
                  snapToInterval={CARD_WIDTH + spacing.md}
                  decelerationRate="fast"
                  contentContainerStyle={{ paddingHorizontal: spacing.xs }}
                  renderItem={renderPatrocinador}
                  initialNumToRender={PATROCINADORES.length}
                  getItemLayout={(_, index) => ({
                    length: CARD_WIDTH + spacing.md,
                    offset: (CARD_WIDTH + spacing.md) * index,
                    index,
                  })}
                  onScrollToIndexFailed={(info) => {
                    const offset = (CARD_WIDTH + spacing.md) * info.index;
                    flatListRef.current?.scrollToOffset({ offset, animated: true });
                  }}
                  onScroll={Animated.event(
                    [{ nativeEvent: { contentOffset: { x: scrollX } } }],
                    { useNativeDriver: true }
                  )}
                />
              </View>
            </View>
          </View>

          <LinearGradient {...gradients.appBg} style={styles.footer}>
            <Text style={styles.footerText}>© 2026 Kapitour · Maricá, RJ</Text>
          </LinearGradient>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingTop: spacing.lg,
    paddingHorizontal: layout.contentPadding,
    paddingBottom: spacing.xxl + spacing.lg,
  },
  topImageWrapper: {
    alignItems: "center",
    marginHorizontal: -layout.contentPadding,
  },
  heroGreeting: {
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  heroTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  heroIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(247, 160, 0, 0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  heroTitle: {
    ...typography.hero,
    fontSize: 22,
  },
  heroSubtitle: {
    ...typography.body,
    marginTop: spacing.xs,
    lineHeight: 20,
    marginLeft: 36 + spacing.xs,
  },
  content: {
    marginTop: spacing.md,
  },
  section: {
    marginBottom: spacing.xl,
  },
  narrowCard: {
    alignSelf: "center",
    width: CARD_NARROW,
    marginTop: spacing.sm,
  },
  weatherCard: {
    minHeight: 240,
  },
  carouselContainer: {
    height: PARTNER_CARD_HEIGHT + spacing.md,
    marginTop: spacing.sm,
  },
  footer: {
    padding: layout.contentPadding,
    alignItems: "center",
    justifyContent: "center",
  },
  footerText: {
    ...typography.caption,
    color: "#fff",
  },
});
