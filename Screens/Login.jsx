import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableWithoutFeedback,
  Keyboard,
  Dimensions,
  ActivityIndicator,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import { GoogleSignin, statusCodes } from "@react-native-google-signin/google-signin";
import { Ionicons } from "@expo/vector-icons";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { useAuth } from "../hooks/useAuth";
import ContainerImg from "../components/ContainerImg";
import Button from "../components/Button";
import TextField from "../components/TextField";
import PressableScale from "../components/PressableScale";
import { useAppAlert } from "../components/AppAlert";
import { EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID } from "@env";

GoogleSignin.configure({
  webClientId: EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
  offlineAccess: true,
});

const { width: screenWidth } = Dimensions.get("window");

export default function LoginScreen() {
  const navigation = useNavigation();
  const { signIn, signInWithGoogle } = useAuth();
  const { showAlert } = useAppAlert();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleGoogleSignIn = async () => {
    setGoogleLoading(true);
    try {
      await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
      const response = await GoogleSignin.signIn();
      const { idToken } = await GoogleSignin.getTokens();

      if (!idToken) throw new Error("Token não recebido do Google.");

      const result = await signInWithGoogle(idToken);
      if (!result.success) {
        showAlert({
          icon: "close-circle-outline",
          iconColor: colors.primary,
          title: "Erro no login Google",
          message: result.error || "Não foi possível autenticar com o Google.",
          buttons: [{ text: "OK" }],
        });
      }
    } catch (err) {
      if (err.code === statusCodes.SIGN_IN_CANCELLED) {
        // usuário fechou sem logar — sem mensagem
      } else if (err.code === statusCodes.IN_PROGRESS) {
        // já em andamento
      } else if (err.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        showAlert({
          icon: "alert-circle-outline",
          iconColor: colors.accent,
          title: "Google Play Services",
          message: "O Google Play Services não está disponível ou está desatualizado.",
          buttons: [{ text: "OK" }],
        });
      } else {
        showAlert({
          icon: "warning-outline",
          iconColor: colors.accent,
          title: "Erro no login Google",
          message: err.message || "Não foi possível conectar com o Google.",
          buttons: [{ text: "OK" }],
        });
      }
    } finally {
      setGoogleLoading(false);
    }
  };

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
    <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
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
            disabled={loading || googleLoading}
            loading={loading}
            fullWidth
            style={styles.loginButton}
            accessibilityLabel="Entrar na conta"
          >
            Login
          </Button>

          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>ou</Text>
            <View style={styles.dividerLine} />
          </View>

          <PressableScale
            onPress={handleGoogleSignIn}
            disabled={loading || googleLoading}
            accessibilityLabel="Entrar com Google"
            contentStyle={styles.googleButton}
          >
            {googleLoading ? (
              <ActivityIndicator size="small" color={colors.primary} />
            ) : (
              <>
                <Ionicons name="logo-google" size={20} color="#DB4437" style={styles.googleIcon} />
                <Text style={styles.googleText}>Entrar com Google</Text>
              </>
            )}
          </PressableScale>

          <PressableScale
            onPress={() => navigation.navigate("Cadastro")}
            disabled={loading || googleLoading}
            accessibilityLabel="Ir para cadastro"
            contentStyle={styles.registerHitArea}
          >
            <Text style={styles.cadastroText}>Cadastrar-se</Text>
          </PressableScale>
        </View>
      </LinearGradient>
    </TouchableWithoutFeedback>
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
  dividerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.md,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: "rgba(255,255,255,0.25)",
  },
  dividerText: {
    ...typography.caption,
    color: "rgba(255,255,255,0.7)",
    marginHorizontal: spacing.sm,
    fontSize: 13,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  googleButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
    borderRadius: 12,
    height: 52,
    width: "100%",
    ...shadows.soft,
  },
  googleIcon: {
    marginRight: spacing.sm,
  },
  googleText: {
    ...typography.body,
    color: "#3c4043",
    fontWeight: "600",
    fontSize: 15,
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
