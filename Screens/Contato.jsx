import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Linking,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import PressableScale from "../components/PressableScale";
import TextField from "../components/TextField";
import Button from "../components/Button";
import SectionHeader from "../components/SectionHeader";
import { useAppAlert } from "../components/AppAlert";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

const EMAIL_CONTATO = "plataformadigitalkapitour@gmail.com";

const CANAIS = [
  {
    id: "phone",
    icon: "call-outline",
    eyebrow: "LIGAR AGORA",
    title: "(21) 98358-1550",
    subtitle: "Atendimento por telefone",
    url: "tel:+5521983581550",
    tint: colors.primary,
  },
  {
    id: "whatsapp",
    icon: "logo-whatsapp",
    eyebrow: "WHATSAPP",
    title: "Fale conosco",
    subtitle: "Resposta mais rápida pelo app",
    url: "https://wa.me/5521983581550?text=Ol%C3%A1!%20Vim%20pelo%20app%20Kapitour%20e%20gostaria%20de%20falar%20com%20a%20equipe.",
    tint: "#25D366",
  },
  {
    id: "email",
    icon: "mail-outline",
    eyebrow: "E-MAIL",
    title: EMAIL_CONTATO,
    subtitle: "Suporte e parcerias",
    url: `mailto:${EMAIL_CONTATO}`,
    tint: colors.accent,
  },
  {
    id: "instagram",
    icon: "logo-instagram",
    eyebrow: "REDES SOCIAIS",
    title: "@kapi.tour",
    subtitle: "Novidades e dicas de Maricá",
    url: "https://www.instagram.com/kapi.tour",
    tint: "#E1306C",
  },
];

function CanalCard({ icon, eyebrow, title, subtitle, tint, onPress }) {
  return (
    <PressableScale
      onPress={onPress}
      contentStyle={[styles.card, shadows.card]}
      accessibilityLabel={`${title}. ${subtitle}`}
    >
      <View style={[styles.cardStripe, { backgroundColor: tint }]} />
      <View style={[styles.cardIconWrap, { backgroundColor: `${tint}22` }]}>
        <Ionicons name={icon} size={22} color={tint} />
      </View>
      <View style={styles.cardBody}>
        <Text style={styles.cardEyebrow}>{eyebrow}</Text>
        <Text style={styles.cardTitle} numberOfLines={2}>
          {title}
        </Text>
        <Text style={styles.cardSubtitle}>{subtitle}</Text>
      </View>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </PressableScale>
  );
}

export default function Contato() {
  const navigation = useNavigation();
  const { showAlert } = useAppAlert();
  const [showForm, setShowForm] = useState(false);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [mensagem, setMensagem] = useState("");

  const abrirLink = async (url) => {
    try {
      const ok = await Linking.canOpenURL(url);
      if (!ok) {
        showAlert({
          icon: "alert-circle-outline",
          iconColor: colors.primary,
          title: "Link indisponível",
          message: "Não foi possível abrir este contato no seu dispositivo.",
          buttons: [{ text: "OK" }],
        });
        return;
      }
      await Linking.openURL(url);
    } catch {
      showAlert({
        icon: "alert-circle-outline",
        iconColor: colors.primary,
        title: "Erro ao abrir",
        message: "Tente novamente ou use outro canal de contato.",
        buttons: [{ text: "OK" }],
      });
    }
  };

  const enviarMensagem = () => {
    if (!nome.trim() || !email.trim() || !mensagem.trim()) {
      showAlert({
        icon: "create-outline",
        iconColor: colors.accent,
        title: "Preencha o formulário",
        message: "Informe nome, e-mail e mensagem antes de enviar.",
        buttons: [{ text: "Entendi" }],
      });
      return;
    }

    const corpo = encodeURIComponent(
      `Nome: ${nome.trim()}\nE-mail: ${email.trim()}\n\n${mensagem.trim()}`
    );
    abrirLink(`mailto:${EMAIL_CONTATO}?subject=${encodeURIComponent("Contato pelo app Kapitour")}&body=${corpo}`);
  };

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <ScrollView
            contentContainerStyle={styles.scroll}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {navigation.canGoBack?.() ? (
              <PressableScale
                onPress={() => navigation.goBack()}
                contentStyle={styles.backBtn}
                accessibilityLabel="Voltar"
              >
                <Ionicons name="chevron-back" size={22} color={colors.text} />
                <Text style={styles.backLabel}>Voltar</Text>
              </PressableScale>
            ) : null}

            <View style={styles.hero}>
              <View style={styles.heroTitleRow}>
                <View style={styles.heroIconWrap}>
                  <Ionicons name="mail" size={22} color={colors.accent} />
                </View>
                <Text style={styles.heroTitle}>Contato</Text>
              </View>
              <Text style={styles.heroSubtitle}>
                Fale com a equipe Kapitour. Estamos prontos para ajudar turistas, parceiros e
                guias em Maricá.
              </Text>
            </View>

            <View style={styles.infoBanner}>
              <Ionicons name="time-outline" size={18} color={colors.accent} />
              <Text style={styles.infoBannerText}>
                Horário de atendimento: seg a sex, 9h às 18h
              </Text>
            </View>

            <SectionHeader title="Canais de atendimento" />
            <View style={styles.cards}>
              {CANAIS.map((canal) => (
                <CanalCard
                  key={canal.id}
                  {...canal}
                  onPress={() => abrirLink(canal.url)}
                />
              ))}
            </View>

            <SectionHeader
              title="Enviar mensagem"
              subtitle="Preferimos o formulário para dúvidas detalhadas"
              style={styles.formSectionHeader}
            />

            {!showForm ? (
              <Button
                icon="chatbubble-ellipses-outline"
                variant="ghost"
                fullWidth
                onPress={() => setShowForm(true)}
              >
                Escrever mensagem
              </Button>
            ) : (
              <View style={[styles.formCard, shadows.card]}>
                <TextField
                  value={nome}
                  onChangeText={setNome}
                  placeholder="Seu nome"
                  autoCapitalize="words"
                  accessibilityLabel="Nome"
                />
                <TextField
                  value={email}
                  onChangeText={setEmail}
                  placeholder="Seu e-mail"
                  keyboardType="email-address"
                  accessibilityLabel="E-mail"
                />
                <Text style={styles.fieldLabel}>Mensagem</Text>
                <TextInput
                  style={styles.textArea}
                  value={mensagem}
                  onChangeText={setMensagem}
                  placeholder="Como podemos ajudar?"
                  placeholderTextColor={colors.inputPlaceholder}
                  multiline
                  numberOfLines={5}
                  textAlignVertical="top"
                  accessibilityLabel="Mensagem"
                />
                <Button icon="send-outline" fullWidth onPress={enviarMensagem}>
                  Enviar por e-mail
                </Button>
                <Button variant="ghost" fullWidth onPress={() => setShowForm(false)}>
                  Cancelar
                </Button>
              </View>
            )}
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  backBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
    alignSelf: "flex-start",
    marginTop: spacing.xs,
    marginBottom: spacing.xs,
    paddingVertical: spacing.xxs,
  },
  backLabel: {
    ...typography.body,
    color: colors.text,
    fontWeight: "600",
  },
  hero: {
    paddingTop: spacing.sm,
    paddingBottom: spacing.md,
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
  infoBanner: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.lg,
  },
  infoBannerText: {
    ...typography.caption,
    color: colors.textMuted,
    fontWeight: "600",
    flex: 1,
  },
  cards: {
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.sm,
    gap: spacing.sm,
    overflow: "hidden",
  },
  cardStripe: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    width: 3,
  },
  cardIconWrap: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
    marginLeft: spacing.xxs,
  },
  cardBody: {
    flex: 1,
    gap: 2,
  },
  cardEyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 1,
    fontWeight: "700",
    fontSize: 9,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 15,
    lineHeight: 20,
  },
  cardSubtitle: {
    ...typography.body,
    fontSize: 12,
    lineHeight: 16,
  },
  formSectionHeader: {
    marginTop: spacing.xs,
  },
  formCard: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    padding: spacing.md,
    gap: spacing.xxs,
  },
  fieldLabel: {
    ...typography.caption,
    color: colors.textMuted,
    fontWeight: "600",
    marginBottom: spacing.xxs,
    marginTop: spacing.xxs,
  },
  textArea: {
    backgroundColor: colors.inputBg,
    color: colors.inputText,
    minHeight: 120,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    ...typography.body,
    fontSize: 16,
    marginBottom: spacing.sm,
  },
});
