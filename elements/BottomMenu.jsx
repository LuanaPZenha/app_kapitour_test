import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

export default function BottomMenu() {
  const navigation = useNavigation();
  const { width } = Dimensions.get("window"); // Obtendo a largura da tela para responsividade

  return (
    <View style={[styles.menuContainer, { width: width - 60 }]}>
      {" "}
      {/* Responsividade   */}
      <TouchableOpacity
        onPress={() => navigation.navigate("Início")}
        accessibilityLabel="Ir para Home"
      >
        <Ionicons name="home-outline" size={28} color="#ffffff" />
      </TouchableOpacity>
      <TouchableOpacity
        onPress={() => navigation.navigate("Conta")}
        accessibilityLabel="Ir para Login"
      >
        <Ionicons name="person-outline" size={28} color="#ffffff" />
      </TouchableOpacity>
      <View style={styles.centerButtonWrapper}>
        <TouchableOpacity
          style={styles.centerButton}
          onPress={() => navigation.navigate("Rotas")}
          accessibilityLabel="Ver Rotas"
        >
          <Ionicons name="navigate-circle-outline" size={32} color="#ce1919" />
        </TouchableOpacity>
      </View>
      <TouchableOpacity
        onPress={() => navigation.navigate("Pontos")}
        accessibilityLabel="Ir para Pontos Turísticos"
      >
        <Ionicons name="location-outline" size={28} color="#ffffff" />
      </TouchableOpacity>
      <TouchableOpacity
        onPress={() => navigation.navigate("Mapa")}
        accessibilityLabel="Ir para Mapa"
      >
        <Ionicons name="map-outline" size={28} color="#ffffff" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  menuContainer: {
    position: "absolute",
    bottom: 20,
    left: 30,
    right: 30,
    backgroundColor: "#ce1919",
    borderRadius: 40,
    height: 70,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    elevation: 10,
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.3)",
  },
  centerButtonWrapper: {
    position: "relative",
    top: -25,
  },
  centerButton: {
    backgroundColor: "#ffffff",
    width: 65,
    height: 65,
    borderRadius: 32.5,
    alignItems: "center",
    justifyContent: "center",
    elevation: 8,
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.3)",
  },
});
