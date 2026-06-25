/*import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  Linking,
  Animated,
  FlatList,
  Dimensions,
  StyleSheet,
} from "react-native";

const { width } = Dimensions.get("window");

const data = [
  {
    id: "1",
    title: "AGM Maricá",
    description:
      "Parceria com a AGM Associação dos Guias de Turismo de Maricá. Conheça os melhores guias para sua experiência!",
    imageUri:
      "https://github.com/Kapitour/Imgs-Padr-o/blob/main/home/agm.png?raw=true",
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
    description:
      "Vassouras Tec, incubadora tecnológica da Univassouras. Inovação e tecnologia para o turismo!",
    imageUri:
      "https://github.com/Kapitour/Imgs-Padr-o/blob/main/VassourasT%C3%A9c.png?raw=true",
    style: "incubadora",
  },
];

const CARD_WIDTH = width * 0.6;
const SPACING = 15;

const Partiners = () => {
  const flatListRef = useRef(null);
  const scrollX = useRef(new Animated.Value(0)).current;
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      let nextIndex = (currentIndex + 1) % data.length;
      flatListRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      setCurrentIndex(nextIndex);
    }, 4000);

    return () => clearInterval(interval);
  }, [currentIndex]);

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <Image
        source={{ uri: item.imageUri }}
        style={item.style === "circle" ? styles.imageCircle : styles.imageIncubadora}
        resizeMode={item.style === "circle" ? "cover" : "contain"}
      />
      <Text style={styles.cardTitle}>{item.title}</Text>
      <Text style={styles.cardText}>{item.description}</Text>
      {item.buttonText && (
        <TouchableOpacity onPress={item.onPress} style={styles.button}>
          <Text style={styles.buttonText}>{item.buttonText}</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Parceiros</Text>
      <View style={{ flex: 1 }}>
        {/* Conteúdo principal da página */
    /*  </View>

      <View style={styles.carouselContainer}>
        <Animated.FlatList
          ref={flatListRef}
          data={data}
          keyExtractor={(item) => item.id}
          horizontal
          showsHorizontalScrollIndicator={false}
          pagingEnabled
          snapToInterval={CARD_WIDTH + SPACING}
          decelerationRate="fast"
          contentContainerStyle={{ paddingHorizontal: SPACING / 2 }}
          renderItem={renderItem}
          onScroll={Animated.event(
            [{ nativeEvent: { contentOffset: { x: scrollX } } }],
            { useNativeDriver: false }
          )}
          onMomentumScrollEnd={(ev) => {
            const index = Math.round(
              ev.nativeEvent.contentOffset.x / (CARD_WIDTH + SPACING)
            );
            setCurrentIndex(index);
          }}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f13f3f15",
    paddingTop: 40,
    paddingBottom: 30,
  },
  title: {
    color: "#fff",
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 20,
    letterSpacing: 1,
    borderBottomWidth: 3,
    borderBottomColor: "#f7a000",
    alignSelf: "center",
    paddingBottom: 6,
    width: "auto",
  },
  carouselContainer: {
    height: 320,
  },
  card: {
    backgroundColor: "rgba(59, 57, 57, 0.53)",
    borderRadius: 24,
    padding: 20,
    width: CARD_WIDTH,
    marginHorizontal: SPACING / 2,
    minHeight: 280,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#c83349",
    shadowColor: "#c83349",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  },
  imageCircle: {
    width: 70,
    height: 70,
    borderRadius: 35,
    marginBottom: 12,
    borderWidth: 3,
    borderColor: "#f7a000",
    backgroundColor: "#fff",
  },
  imageIncubadora: {
    width: 100,
    height: 100,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 3,
    borderColor: "#f7a000",
    backgroundColor: "#fff",
  },
  cardTitle: {
    color: "#f7a000",
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 6,
    textAlign: "center",
    letterSpacing: 1,
  },
  cardText: {
    color: "#fff",
    fontSize: 14,
    lineHeight: 20,
    textAlign: "center",
    marginBottom: 14,
  },
  button: {
    backgroundColor: "#c83349",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    elevation: 4,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 14,
    letterSpacing: 1,
  },
});

export default Partiners; */
