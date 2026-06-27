import React, { useRef, useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Animated,
  StyleSheet,
  Pressable,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Keyboard,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { gradients } from "../theme/gradients";
import { authApi, dbApi } from "./../lib/api";
import Button from "../components/Button";
import DismissKeyboardView from "../components/DismissKeyboardView";
import { useAppAlert } from "../components/AppAlert";
import { colors } from "../theme/colors";

export default function Cadastro() {
  const navigation = useNavigation();
  const { showAlert } = useAppAlert();
  const [registered, setRegistered] = useState(false);
  const [keyboardOpen, setKeyboardOpen] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [cpf, setCpf] = useState("");
  const [sexo, setSexo] = useState("");
  const [password, setPassword] = useState("");
  const [nascimento, setNascimento] = useState("");

  const formOpacity = useRef(new Animated.Value(0)).current;
  const formScale = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(formOpacity, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.spring(formScale, {
        toValue: 1,
        friction: 5,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  useEffect(() => {
    const showSubscription = Keyboard.addListener("keyboardDidShow", () =>
      setKeyboardOpen(true)
    );
    const hideSubscription = Keyboard.addListener("keyboardDidHide", () =>
      setKeyboardOpen(false)
    );

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  const formatCpf = (text) => {
    const cleaned = text.replace(/\D/g, "").slice(0, 11);
    const formatted = cleaned
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    return formatted;
  };

  const formatDataNascimento = (text) => {
    // Remove tudo que não é número
    const cleaned = text.replace(/\D/g, "").slice(0, 8);
    
    // Aplica a máscara DD/MM/AAAA automaticamente
    if (cleaned.length === 0) {
      return "";
    } else if (cleaned.length <= 2) {
      return cleaned;
    } else if (cleaned.length <= 4) {
      return cleaned.replace(/(\d{2})(\d{1,2})/, "$1/$2");
    } else {
      return cleaned.replace(/(\d{2})(\d{2})(\d{1,4})/, "$1/$2/$3");
    }
  };

  const convertToDate = (dateString) => {
    // Converte DD/MM/AAAA para AAAA-MM-DD
    const parts = dateString.split('/');
    if (parts.length === 3) {
      const [day, month, year] = parts;
      
      // Validar se os valores são válidos
      const dayNum = parseInt(day, 10);
      const monthNum = parseInt(month, 10);
      const yearNum = parseInt(year, 10);
      
      // Validações básicas
      if (dayNum < 1 || dayNum > 31) {
        throw new Error("Dia inválido");
      }
      if (monthNum < 1 || monthNum > 12) {
        throw new Error("Mês inválido");
      }
      if (yearNum < 1900 || yearNum > new Date().getFullYear()) {
        throw new Error("Ano inválido");
      }
      
      // Verificar se a data existe (ex: 29/02/2023)
      const date = new Date(yearNum, monthNum - 1, dayNum);
      if (date.getDate() !== dayNum || date.getMonth() !== monthNum - 1 || date.getFullYear() !== yearNum) {
        throw new Error("Data inválida");
      }
      
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    throw new Error("Formato de data inválido");
  };

  const handleSexoChange = (value) => {
    setSexo(value === sexo ? "" : value);
    console.log("Sexo selecionado:", value);
  };

  const handleRegister = async () => {
    if (!name || !email || !cpf || !sexo || !password || !nascimento) {
      alert("Preencha todos os campos.");
      return;
    }

    // Validar formato da data de nascimento
    if (nascimento.length !== 10 || !nascimento.includes('/')) {
      alert("Data de nascimento deve estar no formato DD/MM/AAAA");
      return;
    }

    // Validar e converter a data
    let dataNascimentoFormatada;
    try {
      dataNascimentoFormatada = convertToDate(nascimento);
      console.log("Data convertida:", dataNascimentoFormatada);
    } catch (error) {
      alert(`Erro na data de nascimento: ${error.message}`);
      return;
    }
    try {
      // Primeiro, verifica se o email já existe
      const { data: existingUsers, error: checkError } = await dbApi.emailExists(email);

      if (checkError) {
        alert("Erro ao verificar email: " + checkError.message);
        return;
      }

      if (existingUsers && existingUsers.length > 0) {
        alert("Este email já está cadastrado.");
        return;
      }

      const { data, error } = await authApi.register({
        nome: name,
        email: email,
        password: password,
        cpf: cpf,
        sexo: sexo,
        data_nascimento: dataNascimentoFormatada,
      });

      if (error) {
        alert("Erro: " + error.message);
        return;
      }

      const user = data.user;

      if (user) {
        console.log("Usuário criado:", user.auth_id);

        showAlert({
          icon: "checkmark-circle-outline",
          iconColor: "#4caf50",
          title: "Cadastro realizado!",
          message: "Sua conta foi criada com sucesso. Faça login para continuar.",
          buttons: [
            {
              text: "Fazer login",
              onPress: () => {
                navigation.reset({
                  index: 0,
                  routes: [{ name: "Login" }],
                });
              },
            },
          ],
        });

        setRegistered(true);
      }
    } catch (err) {
      alert("Erro inesperado: " + err.message);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1 }}
    >
      <LinearGradient {...gradients.appBg} style={styles.containerPrincipal}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Ionicons name="arrow-back" size={28} color="white" />
        </TouchableOpacity>

        <DismissKeyboardView>
          <ScrollView
            contentContainerStyle={[styles.container, { paddingTop: 55 }]}
            keyboardShouldPersistTaps="handled"
          >
            {!registered ? (
              <Animated.View
                style={[
                  styles.formBox,
                  {
                    opacity: formOpacity,
                    transform: [{ scale: formScale }],
                  },
                ]}
              >
              <Text style={styles.label}>Nome:</Text>
              <TextInput
                placeholder="Digite seu nome"
                style={styles.input}
                value={name}
                onChangeText={setName}
              />

              <Text style={styles.label}>Email:</Text>
              <TextInput
                placeholder="Digite seu email"
                style={styles.input}
                keyboardType="email-address"
                autoCapitalize="none"
                value={email}
                onChangeText={setEmail}
              />

              <Text style={styles.label}>CPF:</Text>
              <View style={{ flexDirection: "row", alignItems: "center" }}>
                <TextInput
                  placeholder="Digite seu CPF"
                  style={[styles.input, { flex: 1 }]}
                  value={cpf}
                  onChangeText={(text) => setCpf(formatCpf(text))}
                  keyboardType="numeric"
                  maxLength={14}
                />
                {keyboardOpen && (
                  <TouchableOpacity
                    onPress={Keyboard.dismiss}
                    style={{ marginLeft: 10 }}
                  >
                    <Text style={{ color: "white", fontSize: 16 }}>Fechar</Text>
                  </TouchableOpacity>
                )}
              </View>

              <Text style={styles.label}>Sexo:</Text>
              <View style={styles.checkboxGroup}>
                <Pressable
                  style={[
                    styles.checkbox,
                    sexo === "Masculino" && styles.checkboxSelected,
                  ]}
                  onPress={() => handleSexoChange("Masculino")}
                >
                  <Text style={styles.checkboxText}>Masculino</Text>
                </Pressable>
                <Pressable
                  style={[
                    styles.checkbox,
                    sexo === "Feminino" && styles.checkboxSelected,
                  ]}
                  onPress={() => handleSexoChange("Feminino")}
                >
                  <Text style={styles.checkboxText}>Feminino</Text>
                </Pressable>
              </View>

              <Text style={styles.label}>Senha:</Text>
              <TextInput
                placeholder="Digite sua senha"
                style={styles.input}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
              />

              <Text style={styles.label}>Data de Nascimento:</Text>
              <TextInput
                placeholder="DD/MM/AAAA"
                style={styles.input}
                value={nascimento}
                onChangeText={(text) => setNascimento(formatDataNascimento(text))}
                keyboardType="numeric"
                maxLength={10}
                autoComplete="birthdate-full"
              />

              <Button onPress={handleRegister} fullWidth style={{ marginTop: 10 }}>
                Cadastrar
              </Button>
            </Animated.View>
          ) : (
              <Animated.View
                style={[
                  styles.formBox,
                  {
                    opacity: formOpacity,
                    transform: [{ scale: formScale }],
                  },
                ]}
              >
              <Text style={styles.success}>
                Cadastro realizado com sucesso!
              </Text>
              <Button onPress={() => navigation.navigate("Login")} fullWidth>
                Fazer Login
              </Button>
            </Animated.View>
          )}
          </ScrollView>
        </DismissKeyboardView>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  containerPrincipal: {
    flex: 1,
  },
  container: {
    flexGrow: 1,
    backgroundColor: "transparent",
    justifyContent: "center",
    alignItems: "center",
    paddingBottom: 100,
    paddingHorizontal: 20,
  },
  formBox: {
    marginTop: 10,
    padding: 10,
    borderRadius: 10,
    width: "100%",
    alignItems: "center",
  },
  label: {
    color: "white",
    alignSelf: "flex-start",
    marginTop: 10,
    marginBottom: 5,
  },
  input: {
    backgroundColor: "#fff",
    color: "black",
    padding: 15,
    borderRadius: 5,
    width: "100%",
    marginBottom: 15,
  },
  success: {
    color: "#0f0",
    fontSize: 18,
    textAlign: "center",
    marginBottom: 20,
  },
  checkboxGroup: {
    flexDirection: "row",
    marginTop: 10,
    justifyContent: "space-around",
    width: "100%",
    marginBottom: 15,
  },
  checkbox: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 5,
    backgroundColor: "#444",
  },
  checkboxSelected: {
    backgroundColor: "#c83349",
  },
  checkboxText: {
    color: "white",
  },
  backButton: {
    position: "absolute",
    top: 50,
    left: 20,
    zIndex: 10,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 20,
    padding: 5,
  },
});
