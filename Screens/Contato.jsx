import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Linking,
  ScrollView,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { FontAwesome } from "@expo/vector-icons";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { gradients } from "../theme/gradients";
import { useNavigation } from "@react-navigation/native";
import Button from "../components/Button";

const Contato = () => {
  const navigation = useNavigation();
  const [showForm, setShowForm] = useState(false);
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(scale, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(scale, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const handleLinkPress = async (url) => {
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Linking.openURL(url);
    } else {
      alert("Não foi possível abrir o link.");
    }
  };

  return (
    <View style={{ flex: 1 }}>
      {/* Gradiente fixo no fundo */}
      <LinearGradient
        {...gradients.appBg}
        style={styles.gradient}
      />

      {/* Botão de retorno */}
      <TouchableOpacity
        style={styles.backButton}
        onPress={() => navigation.goBack()}
      >
        <Ionicons name="arrow-back" size={28} color="#fff" />
      </TouchableOpacity>

      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <Animated.Text
            style={[
              styles.title,
              {
                transform: [{ scale }],
              },
            ]}
          >
            Entre em Contato
          </Animated.Text>

          <View style={styles.btns}>
            <TouchableOpacity
              style={styles.contactItem}
              onPress={() => handleLinkPress("tel:+5521983581550")}
            >
              <View style={styles.iconCircle}>
                <FontAwesome name="phone" size={20} color="#fff" />
              </View>
              <Text style={styles.contactText}>(21) 98358-1550</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.contactItem}
              onPress={() => handleLinkPress("mailto:plataformadigitalkapitour@gmail.com")}
            >
              <View style={styles.iconCircle}>
                <FontAwesome name="envelope" size={20} color="#fff" />
              </View>
              <Text style={styles.contactText}>Nosso email</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.contactItem}
              onPress={() => handleLinkPress("https://www.instagram.com/kapi.tour")}
            >
              <View style={styles.iconCircle}>
                <FontAwesome name="instagram" size={20} color="#fff" />
              </View>
              <Text style={styles.contactText}>@kapi.tour</Text>
            </TouchableOpacity>

            {!showForm && (
              <TouchableOpacity
                style={[styles.contactItem, styles.messageButton]}
                onPress={() => setShowForm(true)}
              >
                <View style={styles.iconCircle}>
                  <FontAwesome name="comment" size={20} color="#fff" />
                </View>
                <Text style={styles.contactText}>Enviar uma mensagem</Text>
              </TouchableOpacity>
            )}
          </View>

          {showForm && (
            <View style={styles.form}>
              <Text style={styles.label}>Nome</Text>
              <TextInput
                style={styles.input}
                placeholder="Seu nome"
                placeholderTextColor="#ccc"
              />

              <Text style={styles.label}>Email</Text>
              <TextInput
                style={styles.input}
                placeholder="Seu email"
                placeholderTextColor="#ccc"
                keyboardType="email-address"
              />

              <Text style={styles.label}>Mensagem</Text>
              <TextInput
                style={styles.textArea}
                placeholder="Digite sua mensagem"
                placeholderTextColor="#ccc"
                multiline
                numberOfLines={4}
                textAlignVertical="top"
              />

              <Button icon="send-outline" fullWidth style={{ marginTop: 10 }}>
                Enviar
              </Button>
            </View>
          )}
        </KeyboardAvoidingView>
      </ScrollView>
    </View>
  );
};

export default Contato;

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    paddingBottom: 90,
  },

  gradient: {
    position: "absolute", 
    width: "100%",
    height: "100%", 
    top: 0,
    left: 0,
  },
  title: {
    fontSize: 28,
    fontWeight: "600",
    color: "#ffffff",
    marginTop: 60,
    marginBottom: 30,
    textAlign: "center",
    letterSpacing: 1,
  },
  btns: {
    width: "100%",
    marginTop: 20,
  },
  contactItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.07)",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.1)",
  },
  iconCircle: {
    width: 42,
    height: 42,
    backgroundColor: "#c93434",
    borderRadius: 21,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 15,
  },
  contactText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "500",
    letterSpacing: 0.5,
  },
  messageButton: {
    backgroundColor: "rgba(255,255,255,0.1)",
    borderColor: "#c93434",
    borderWidth: 1.5,
  },
  form: {
    width: "100%",
    marginTop: 30,
    alignItems: "center", 
  },
  label: {
    color: "#f0f0f0",
    fontWeight: "600",
    fontSize: 16,
    marginBottom: 6,
    letterSpacing: 0.5,
    textShadowColor: "rgba(0, 0, 0, 0.3)",
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  input: {
    width: "90%", 
    backgroundColor: "rgba(255,255,255,0.05)",
    color: "#fff",
    paddingVertical: 8,
    paddingHorizontal: 12, 
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#444",
    marginBottom: 12,
    fontSize: 14,
    height: 40,
  },
  textArea: {
    width: "90%",
    backgroundColor: "rgba(255,255,255,0.05)",
    color: "#fff",
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#444",
    height: 90,
    fontSize: 14,
    marginBottom: 20,
    textAlignVertical: "top",
  },
  backButton: {
    position: "absolute",
    top: 20,
    left: 20,
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(0,0,0,0.3)",
    justifyContent: "center",
    alignItems: "center",
  },
});
