import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import { useAuth } from "../hooks/useAuth";
import ContainerImg from "../components/ContainerImg";
import Button from "../components/Button";
import TextField from "../components/TextField";
import PressableScale from "../components/PressableScale";
import DismissKeyboardView from "../components/DismissKeyboardView";
import { useAppAlert } from "../components/AppAlert";

const { width: screenWidth } = Dimensions.get("window");

export default function LoginScreen() {
  const navigation = useNavigation();
  const { signIn } = useAuth();
  const { showAlert } = useAppAlert();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!email || !senha) {
      showAlert({
        icon: "alert-circle-outline",
        iconColor: colors.accent,
        title: "Campos obrigatórios",
        message: "Preencha o e-mail e a senha para continuar.",
        buttons: [{ text: "OK" }],
      });
      return;
    }

    setLoading(true);
    try {
      const result = await signIn(email, senha);
      if (!result.success) {
        showAlert({
          icon: "close-circle-outline",
          iconColor: colors.primary,
          title: "Erro no login",
          message: result.error || "Credenciais inválidas. Verifique e tente novamente.",
          buttons: [{ text: "Tentar novamente" }],
        });
      }
    } catch (err) {
      console.error("Erro handleLogin:", err);
      showAlert({
        icon: "warning-outline",
        iconColor: colors.accent,
        title: "Erro inesperado",
        message: "Não foi possível conectar. Verifique sua conexão e tente novamente.",
        buttons: [{ text: "OK" }],
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DismissKeyboardView>
      <LinearGradient {...gradients.appBg} style={styles.container}>
        <View style={styles.logoSection}>
          <ContainerImg compact showTagline={false} />
        </View>

        <View style={styles.formBox}>
          <TextField
            value={email}
            onChangeText={setEmail}
            placeholder="Email"
            keyboardType="email-address"
            editable={!loading}
            accessibilityLabel="Email"
          />

          <TextField
            value={senha}
            onChangeText={setSenha}
            placeholder="Senha"
            secureTextEntry={!showPassword}
            editable={!loading}
            accessibilityLabel="Senha"
            showPasswordToggle
            isPasswordVisible={showPassword}
            onTogglePassword={() => setShowPassword((prev) => !prev)}
          />

          <Button
            onPress={handleLogin}
            disabled={loading}
            loading={loading}
            fullWidth
            style={styles.loginButton}
            accessibilityLabel="Entrar na conta"
          >
            Login
          </Button>

          <PressableScale
            onPress={() => navigation.navigate("Cadastro")}
            disabled={loading}
            accessibilityLabel="Ir para cadastro"
            contentStyle={styles.registerHitArea}
          >
            <Text style={styles.cadastroText}>Cadastrar-se</Text>
          </PressableScale>
        </View>
      </LinearGradient>
    </DismissKeyboardView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxl + spacing.lg,
  },
  logoSection: {
    width: screenWidth,
    marginLeft: -spacing.lg,
    marginBottom: spacing.xs,
  },
  formBox: {
    width: "100%",
    maxWidth: layout.maxFormWidth,
    marginTop: spacing.lg,
  },
  loginButton: {
    marginTop: spacing.xs,
  },
  registerHitArea: {
    minHeight: layout.minTouchTarget,
    justifyContent: "center",
    alignItems: "center",
    marginTop: spacing.sm,
  },
  cadastroText: {
    ...typography.subtitle,
    fontSize: 18,
    textAlign: "center",
  },
});
