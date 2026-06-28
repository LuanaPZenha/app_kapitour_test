import React, { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  Modal,
  TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import QRCode from "react-native-qrcode-svg";
import { useNavigation } from "@react-navigation/native";
import { dbApi } from "../lib/api";
import {
  buscarCuponsDisponiveis,
  buscarCuponsResgatados,
  buscarCampanhasDoParceiro,
  buscarContagemCuponsPorCampanha,
} from "../utils/cupomManager";
import { useAuth } from "../hooks/useAuth";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { radius, spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import SectionHeader from "../components/SectionHeader";
import Button from "../components/Button";
import { useAppAlert } from "../components/AppAlert";

// ─────────────────────────────────────────
// Cabeçalho com botão de voltar
// ─────────────────────────────────────────
function HeaderBack({ children }) {
  const navigation = useNavigation();
  return (
    <View style={styles.header}>
      <View style={styles.headerRow}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}
          accessibilityLabel="Voltar"
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <Ionicons name="chevron-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <View style={styles.flex}>{children}</View>
      </View>
    </View>
  );
}

// ─────────────────────────────────────────
// Card de cupom individual
// ─────────────────────────────────────────
function CupomCard({ nome, validade, resgatado = false, disponivel = false }) {
  return (
    <View style={[styles.card, shadows.card]}>
      <View style={[styles.cardStripe, resgatado ? styles.stripeUsed : styles.stripeAvailable]} />
      <View style={styles.cardBody}>
        <View style={styles.cardIconWrap}>
          <Ionicons
            name={resgatado ? "checkmark-circle" : "pricetag"}
            size={22}
            color={resgatado ? colors.textSecondary : colors.accent}
          />
        </View>
        <View style={styles.cardContent}>
          <Text style={styles.cardTitle} numberOfLines={2}>{nome}</Text>
          {validade ? (
            <Text style={styles.cardSub}>
              <Ionicons name="time-outline" size={12} /> Validade: {validade}
            </Text>
          ) : null}
        </View>
        <View style={[styles.badge, resgatado ? styles.badgeUsed : styles.badgeAvailable]}>
          <Text style={styles.badgeText}>{resgatado ? "Usado" : "Ativo"}</Text>
        </View>
      </View>
    </View>
  );
}

// Card de campanha (para parceiros)
function CampanhaCard({ nome, descricao, dataInicio, dataFim, ativa, disponiveis }) {
  return (
    <View style={[styles.card, shadows.card]}>
      <View style={[styles.cardStripe, ativa ? styles.stripeAvailable : styles.stripeUsed]} />
      <View style={styles.cardBody}>
        <View style={styles.cardIconWrap}>
          <Ionicons name="megaphone" size={22} color={ativa ? colors.accent : colors.textSecondary} />
        </View>
        <View style={styles.cardContent}>
          <Text style={styles.cardTitle} numberOfLines={2}>{nome}</Text>
          {descricao ? <Text style={styles.cardSub} numberOfLines={2}>{descricao}</Text> : null}
          {(dataInicio || dataFim) ? (
            <Text style={styles.cardSub}>
              {dataInicio ? `Início: ${dataInicio}` : ""}
              {dataInicio && dataFim ? "  ·  " : ""}
              {dataFim ? `Fim: ${dataFim}` : ""}
            </Text>
          ) : null}
          <Text style={styles.cardSub}>
            {disponiveis ?? 0} cupons disponíveis
          </Text>
        </View>
        <View style={[styles.badge, ativa ? styles.badgeAvailable : styles.badgeUsed]}>
          <Text style={styles.badgeText}>{ativa ? "Ativa" : "Inativa"}</Text>
        </View>
      </View>
    </View>
  );
}

// ─────────────────────────────────────────
// Tela principal
// ─────────────────────────────────────────
export default function Cupons() {
  const { user, isLogged } = useAuth();
  const navigation = useNavigation();
  const { showAlert } = useAppAlert();
  const [userInfo, setUserInfo] = useState(null);
  const [tipoUsuarioId, setTipoUsuarioId] = useState(null);
  const [cuponsDisponiveis, setCuponsDisponiveis] = useState([]);
  const [cuponsResgatados, setCuponsResgatados] = useState([]);
  const [campanhas, setCampanhas] = useState([]);
  const [contagemCampanhas, setContagemCampanhas] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);

  const fetchData = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }
    try {
      const { data } = await dbApi.getUserByAuthId(user.id);
      if (!data) return;
      setUserInfo(data);
      setTipoUsuarioId(data.tipo_usuario_id);

      if (data.tipo_usuario_id === 2) {
        const [campResult, contagemResult, histResult] = await Promise.all([
          buscarCampanhasDoParceiro(data.id),
          buscarContagemCuponsPorCampanha(data.id),
          buscarCuponsResgatados(),
        ]);
        if (campResult.success) setCampanhas(campResult.data || []);
        if (contagemResult.success) setContagemCampanhas(contagemResult.data || {});
        if (histResult.success) setCuponsResgatados(histResult.data || []);
      } else {
        const [dispResult, resgatadosResult] = await Promise.all([
          buscarCuponsDisponiveis(),
          buscarCuponsResgatados(),
        ]);
        if (dispResult.success) setCuponsDisponiveis(dispResult.data || []);
        if (resgatadosResult.success) setCuponsResgatados(resgatadosResult.data || []);
      }
    } catch (err) {
      showAlert({
        icon: "warning-outline",
        iconColor: colors.accent,
        title: "Erro ao carregar",
        message: "Não foi possível buscar seus cupons. Tente novamente.",
        buttons: [{ text: "OK" }],
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  // ── Não logado ──
  if (!isLogged) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.flex} edges={["top"]}>
          <HeaderBack>
            <SectionHeader title="Cupons" subtitle="Promoções e benefícios exclusivos." />
          </HeaderBack>
          <View style={styles.guestWrap}>
            <View style={styles.guestIconWrap}>
              <Ionicons name="pricetags-outline" size={52} color={colors.accent} />
            </View>
            <Text style={styles.guestTitle}>Faça login para ver seus cupons</Text>
            <Text style={styles.guestBody}>
              Entre na sua conta para acessar promoções e resgatar benefícios exclusivos em Maricá.
            </Text>
            <Button
              icon="log-in-outline"
              onPress={() => navigation.navigate("Login")}
              fullWidth
              style={styles.loginBtn}
            >
              Entrar
            </Button>
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ── Carregando ──
  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.flex} edges={["top"]}>
          <HeaderBack>
            <SectionHeader title="Cupons" />
          </HeaderBack>
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ── Modal QR Code ──
  const qrModal = (
    <Modal
      visible={showQRModal}
      animationType="fade"
      transparent
      onRequestClose={() => setShowQRModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.qrBox}>
          <Text style={styles.qrTitle}>Seu QR Code</Text>
          <Text style={styles.qrSub}>Apresente para parceiros resgatarem seu benefício</Text>
          <View style={styles.qrCodeWrap}>
            <QRCode value={userInfo?.auth_id || "kapitour"} size={200} />
          </View>
          <TouchableOpacity style={styles.qrClose} onPress={() => setShowQRModal(false)}>
            <MaterialCommunityIcons name="close" size={22} color="#333" />
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  // ── Parceiro: leitor QR + campanhas ──
  if (tipoUsuarioId === 2) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.flex} edges={["top"]}>
          <HeaderBack>
            <SectionHeader
              title="Cupons"
              subtitle={`${campanhas.length} campanha${campanhas.length !== 1 ? "s" : ""} cadastrada${campanhas.length !== 1 ? "s" : ""}`}
            />
          </HeaderBack>
          <FlatList
            data={campanhas}
            keyExtractor={(item) => String(item.id)}
            contentContainerStyle={styles.list}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
            }
            ListHeaderComponent={
              <View style={[styles.card, styles.qrCard, shadows.card]}>
                <View style={styles.qrCardStripe} />
                <View style={styles.cardBody}>
                  <View style={[styles.cardIconWrap, styles.qrIconWrap]}>
                    <MaterialCommunityIcons name="qrcode-scan" size={24} color={colors.primary} />
                  </View>
                  <View style={styles.cardContent}>
                    <Text style={styles.cardTitle}>Leitor de QR Code</Text>
                    <Text style={styles.cardSub}>Escaneie o QR Code dos clientes</Text>
                  </View>
                  <Button
                    icon="qr-code-outline"
                    onPress={() => navigation.navigate("LeitorQR")}
                    style={styles.qrBtn}
                  >
                    Abrir
                  </Button>
                </View>
              </View>
            }
            ListEmptyComponent={<EmptyState icon="megaphone-outline" text="Nenhuma campanha encontrada." />}
            renderItem={({ item }) => (
              <CampanhaCard
                nome={item.nome}
                descricao={item.descricao}
                dataInicio={item.data_inicio}
                dataFim={item.data_fim}
                ativa={item.ativa}
                disponiveis={contagemCampanhas[item.id]}
              />
            )}
          />
        </SafeAreaView>
      </LinearGradient>
    );
  }

  // ── Usuário / admin: QR Code + cupons disponíveis + resgatados ──
  const qrSection = {
    key: "qr-card",
    type: "qr",
  };

  const sections = [
    qrSection,

    {
      key: "header-disp",
      type: "header",
      title: "Disponíveis",
      subtitle: `${cuponsDisponiveis.length} cupom${cuponsDisponiveis.length !== 1 ? "ns" : ""} ativo${cuponsDisponiveis.length !== 1 ? "s" : ""}`,
    },
    ...cuponsDisponiveis.map((c) => ({ key: `disp-${c.id}`, type: "disp", data: c })),
    ...(cuponsDisponiveis.length === 0
      ? [{ key: "empty-disp", type: "empty", text: "Nenhum cupom disponível no momento." }]
      : []),
    {
      key: "header-resq",
      type: "header",
      title: "Resgatados",
      subtitle: `${cuponsResgatados.length} resgate${cuponsResgatados.length !== 1 ? "s" : ""}`,
    },
    ...cuponsResgatados.map((r) => ({ key: `resq-${r.id}`, type: "resq", data: r })),
    ...(cuponsResgatados.length === 0
      ? [{ key: "empty-resq", type: "empty", text: "Você ainda não resgatou nenhum cupom." }]
      : []),
  ];

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <HeaderBack>
          <SectionHeader
            title="Meus Cupons"
            subtitle="Promoções e benefícios exclusivos para você."
          />
        </HeaderBack>
        <FlatList
          data={sections}
          keyExtractor={(item) => item.key}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
          }
          renderItem={({ item }) => {
            if (item.type === "qr") {
              return (
                <View style={[styles.card, styles.qrCard, shadows.card]}>
                  <View style={[styles.cardStripe, styles.stripeAvailable]} />
                  <View style={styles.cardBody}>
                    <View style={[styles.cardIconWrap, styles.qrIconWrap]}>
                      <MaterialCommunityIcons name="qrcode" size={24} color={colors.primary} />
                    </View>
                    <View style={styles.cardContent}>
                      <Text style={styles.cardTitle}>Seu QR Code</Text>
                      <Text style={styles.cardSub}>Apresente para parceiros</Text>
                    </View>
                    <Button
                      icon="qr-code-outline"
                      onPress={() => setShowQRModal(true)}
                      style={styles.qrBtn}
                    >
                      Ver
                    </Button>
                  </View>
                </View>
              );
            }
            if (item.type === "header") {
              return (
                <SectionHeader
                  title={item.title}
                  subtitle={item.subtitle}
                  style={styles.subHeader}
                />
              );
            }
            if (item.type === "empty") {
              return <EmptyState icon="pricetag-outline" text={item.text} small />;
            }
            if (item.type === "disp") {
              const c = item.data;
              return (
                <CupomCard
                  nome={c.campanha?.nome || c.codigo || `Cupom ${c.id}`}
                  validade={c.data_validade}
                  resgatado={false}
                />
              );
            }
            if (item.type === "resq") {
              const r = item.data;
              return (
                <CupomCard
                  nome={r.cupom?.campanha?.nome || r.cupom?.codigo || `Cupom ${r.id}`}
                  validade={r.cupom?.data_validade}
                  resgatado
                />
              );
            }
            return null;
          }}
        />
        {qrModal}
      </SafeAreaView>
    </LinearGradient>
  );
}

function EmptyState({ icon, text, small = false }) {
  return (
    <View style={[styles.emptyWrap, small && styles.emptySmall]}>
      <Ionicons name={icon} size={small ? 28 : 44} color={colors.textSecondary} />
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  header: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  backBtn: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.06)",
  },
  subHeader: {
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  list: {
    paddingHorizontal: layout.contentPadding,
    paddingBottom: layout.minTouchTarget + spacing.xxl,
  },
  // ── Card ──
  card: {
    flexDirection: "row",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    marginBottom: spacing.sm,
    overflow: "hidden",
  },
  cardStripe: {
    width: 4,
  },
  stripeAvailable: {
    backgroundColor: colors.accent,
  },
  stripeUsed: {
    backgroundColor: colors.textSecondary,
  },
  cardBody: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.sm,
    gap: spacing.sm,
  },
  cardIconWrap: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  cardContent: {
    flex: 1,
    gap: spacing.xxs,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 15,
  },
  cardSub: {
    ...typography.caption,
    fontSize: 12,
  },
  badge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xxs + 1,
    borderRadius: radius.pill,
    alignSelf: "flex-start",
  },
  badgeAvailable: {
    backgroundColor: "rgba(247, 160, 0, 0.18)",
  },
  badgeUsed: {
    backgroundColor: "rgba(184, 184, 200, 0.15)",
  },
  badgeText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.text,
  },
  // ── Guest / empty ──
  guestWrap: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.xl,
    gap: spacing.md,
  },
  guestIconWrap: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xs,
  },
  guestTitle: {
    ...typography.subtitle,
    textAlign: "center",
  },
  guestBody: {
    ...typography.body,
    textAlign: "center",
    lineHeight: 22,
  },
  loginBtn: {
    marginTop: spacing.sm,
  },
  emptyWrap: {
    alignItems: "center",
    paddingVertical: spacing.xxl,
    gap: spacing.sm,
  },
  emptySmall: {
    paddingVertical: spacing.md,
  },
  emptyText: {
    ...typography.body,
    textAlign: "center",
  },
  // ── QR card inline ──
  qrCard: {
    marginBottom: spacing.md,
  },
  qrIconWrap: {
    backgroundColor: "rgba(200, 51, 73, 0.15)",
  },
  qrBtn: {
    paddingHorizontal: spacing.sm,
    minWidth: 64,
  },
  // ── QR Modal ──
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    alignItems: "center",
    justifyContent: "center",
  },
  qrBox: {
    backgroundColor: "#fff",
    borderRadius: radius.lg,
    padding: spacing.xl,
    alignItems: "center",
    width: "80%",
    gap: spacing.sm,
    position: "relative",
  },
  qrTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1a1a1a",
  },
  qrSub: {
    fontSize: 13,
    color: "#555",
    textAlign: "center",
    marginBottom: spacing.xs,
  },
  qrCodeWrap: {
    padding: spacing.md,
    backgroundColor: "#fff",
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: "#eee",
  },
  qrClose: {
    marginTop: spacing.xs,
    padding: spacing.xs,
  },
});
