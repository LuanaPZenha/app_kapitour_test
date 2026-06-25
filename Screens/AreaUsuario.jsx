import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Image,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { gradients } from "../theme/gradients";
import { colors } from "../theme/colors";
import { radius, spacing, layout } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";
import { useAuth } from "../hooks/useAuth";
import { dbApi } from "../lib/api";
import { atualizarUsuario } from "../utils/cupomManager";
import PointDetail from "../components/PointDetail";
import DetalhesRota from "./DetalhesRotas";
import Button from "../components/Button";
import TextField from "../components/TextField";
import SectionHeader from "../components/SectionHeader";
import PressableScale from "../components/PressableScale";
import { useAppAlert } from "../components/AppAlert";

// ─────────────────────────────────────
// Helpers
// ─────────────────────────────────────
function getInitials(nome) {
  if (!nome) return "?";
  return nome
    .trim()
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

function getTipoLabel(tipoId) {
  switch (tipoId) {
    case 1: return "Administrador";
    case 2: return "Parceiro";
    case 3: return "Visitante";
    default: return "Usuário";
  }
}

function getTipoColor(tipoId) {
  switch (tipoId) {
    case 1: return "#f7a000";
    case 2: return "#4a9eff";
    default: return colors.primary;
  }
}

// ─────────────────────────────────────
// InfoRow — linha de dado do perfil
// ─────────────────────────────────────
function InfoRow({ icon, label, value }) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.infoIconWrap}>
        <Ionicons name={icon} size={18} color={colors.primary} />
      </View>
      <View style={styles.infoTextWrap}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value || "Não informado"}</Text>
      </View>
    </View>
  );
}

// ─────────────────────────────────────
// StatBadge — número destacado
// ─────────────────────────────────────
function StatBadge({ count, label, icon }) {
  return (
    <View style={styles.statBadge}>
      <Ionicons name={icon} size={20} color={colors.accent} />
      <Text style={styles.statCount}>{count}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ─────────────────────────────────────
// Tela principal
// ─────────────────────────────────────
const AreaUsuario = () => {
  const navigation = useNavigation();
  const { user, signOut } = useAuth();
  const { showAlert } = useAppAlert();

  const [userInfo, setUserInfo] = useState(null);
  const [tipoUsuarioId, setTipoUsuarioId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Campos de edição
  const [editMode, setEditMode] = useState(false);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [cpf, setCpf] = useState("");
  const [sexo, setSexo] = useState("");

  // Favoritos
  const [favoritos, setFavoritos] = useState([]);
  const [rotasFavoritas, setRotasFavoritas] = useState([]);
  const [loadingFavoritos, setLoadingFavoritos] = useState(false);

  // Detalhe de ponto / rota
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [showPointDetail, setShowPointDetail] = useState(false);
  const [rotaSelecionada, setRotaSelecionada] = useState(null);

  // ── Carregar perfil ──
  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    (async () => {
      try {
        const { data, error } = await dbApi.getUserByAuthId(user.id);
        if (error || !data) return;
        setUserInfo(data);
        setNome(data.nome || "");
        setEmail(data.email || "");
        setCpf(data.cpf || "");
        setSexo(data.sexo || "");
        setTipoUsuarioId(data.tipo_usuario_id);
      } catch {}
      finally { setLoading(false); }
    })();
  }, [user]);

  // ── Carregar favoritos ──
  const fetchFavoritos = useCallback(async () => {
    if (!userInfo) return;
    setLoadingFavoritos(true);
    try {
      const { data } = await dbApi.listFavoritos(userInfo.id);
      setFavoritos(data || []);
    } catch {}
    finally { setLoadingFavoritos(false); }
  }, [userInfo]);

  const fetchRotasFavoritas = useCallback(async () => {
    if (!userInfo) return;
    try {
      const { data: favData } = await dbApi.listFavoritos(userInfo.id);
      const pontoIds = (favData || []).map((f) => f.ponto_id);
      if (pontoIds.length === 0) { setRotasFavoritas([]); return; }

      const { data: rpData } = await dbApi.listRotaPontoByPontos(pontoIds);
      const rotaIds = [...new Set((rpData || []).map((r) => r.rota_id))];
      if (rotaIds.length === 0) { setRotasFavoritas([]); return; }

      const { data: allRotas } = await dbApi.listRotas();
      const filtradas = (allRotas || []).filter((r) => rotaIds.includes(r.id));

      const completas = await Promise.all(
        filtradas.map(async (rota) => {
          const { data: rp } = await dbApi.listRotaPontoByRota(rota.id);
          const primId = rp?.[0]?.ponto_id;
          const { data: pts } = await dbApi.getPontosByIds([primId]);
          return { ...rota, imagem: pts?.[0]?.url_img || null };
        })
      );
      setRotasFavoritas(completas);
    } catch {}
  }, [userInfo]);

  useEffect(() => {
    fetchFavoritos();
    fetchRotasFavoritas();
  }, [fetchFavoritos, fetchRotasFavoritas]);

  useFocusEffect(
    React.useCallback(() => {
      fetchFavoritos();
      fetchRotasFavoritas();
    }, [fetchFavoritos, fetchRotasFavoritas])
  );

  // ── Salvar perfil ──
  const handleSave = async () => {
    if (!nome.trim()) {
      showAlert({
        icon: "alert-circle-outline",
        iconColor: colors.accent,
        title: "Campo obrigatório",
        message: "O nome não pode ficar vazio.",
        buttons: [{ text: "OK" }],
      });
      return;
    }
    setSaving(true);
    try {
      const result = await atualizarUsuario(userInfo?.auth_id, { nome, email, cpf, sexo });
      if (!result.success) throw new Error(result.error);
      setUserInfo((prev) => ({ ...prev, nome, email, cpf, sexo }));
      setEditMode(false);
      showAlert({
        icon: "checkmark-circle-outline",
        iconColor: "#4caf50",
        title: "Perfil atualizado",
        message: "Suas informações foram salvas com sucesso.",
        buttons: [{ text: "Ótimo!" }],
      });
    } catch (err) {
      showAlert({
        icon: "close-circle-outline",
        iconColor: colors.primary,
        title: "Erro ao salvar",
        message: err.message || "Tente novamente.",
        buttons: [{ text: "OK" }],
      });
    } finally {
      setSaving(false);
    }
  };

  const cancelEdit = () => {
    setNome(userInfo?.nome || "");
    setEmail(userInfo?.email || "");
    setCpf(userInfo?.cpf || "");
    setSexo(userInfo?.sexo || "");
    setEditMode(false);
  };

  const handleLogout = () => {
    showAlert({
      icon: "log-out-outline",
      iconColor: colors.primary,
      title: "Sair da conta",
      message: "Tem certeza que deseja encerrar sua sessão?",
      buttons: [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Sair",
          style: "destructive",
          onPress: async () => {
            const result = await signOut();
            if (!result.success) {
              showAlert({
                icon: "close-circle-outline",
                iconColor: colors.primary,
                title: "Erro ao sair",
                message: result.error,
                buttons: [{ text: "OK" }],
              });
            }
          },
        },
      ],
    });
  };

  const handlePointPress = (favorito) => {
    setSelectedPoint({
      id: favorito.pontos_turisticos?.id,
      nome: favorito.pontos_turisticos?.nome,
      descricao: favorito.pontos_turisticos?.descricao,
      url_img: favorito.pontos_turisticos?.url_img,
      latitude: favorito.pontos_turisticos?.latitude,
      longitude: favorito.pontos_turisticos?.longitude,
    });
    setShowPointDetail(true);
  };

  const removeFavorito = async (pontoId) => {
    try {
      await dbApi.removeFavorito(userInfo.id, pontoId);
      fetchFavoritos();
    } catch {
      showAlert({
        icon: "heart-dislike-outline",
        iconColor: colors.primary,
        title: "Erro",
        message: "Não foi possível remover o favorito.",
        buttons: [{ text: "OK" }],
      });
    }
  };

  // ── Guards ──
  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.accent} />
        </View>
      </LinearGradient>
    );
  }

  if (!user) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <View style={styles.center}>
          <Ionicons name="person-circle-outline" size={64} color={colors.textSecondary} />
          <Text style={[styles.sectionTitle, { marginTop: spacing.md }]}>
            Não autenticado
          </Text>
          <Button onPress={() => navigation.navigate("Perfil")} style={{ marginTop: spacing.md }}>
            Fazer login
          </Button>
        </View>
      </LinearGradient>
    );
  }

  if (rotaSelecionada) {
    return <DetalhesRota rota={rotaSelecionada} voltar={() => setRotaSelecionada(null)} />;
  }

  if (showPointDetail && selectedPoint) {
    return (
      <PointDetail
        point={selectedPoint}
        onClose={() => { setShowPointDetail(false); setSelectedPoint(null); }}
        onFavoriteToggle={() => { fetchFavoritos(); fetchRotasFavoritas(); }}
      />
    );
  }

  const tipoColor = getTipoColor(tipoUsuarioId);

  return (
    <LinearGradient {...gradients.appBg} style={styles.flex}>
      <SafeAreaView style={styles.flex} edges={["top"]}>
        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* ── Avatar + nome ── */}
            <View style={styles.profileHeader}>
              <View style={[styles.avatarCircle, { borderColor: tipoColor }]}>
                <Text style={styles.avatarInitials}>{getInitials(userInfo?.nome)}</Text>
              </View>
              <Text style={styles.profileName}>{userInfo?.nome || "Usuário"}</Text>
              <View style={[styles.tipoBadge, { backgroundColor: `${tipoColor}22`, borderColor: `${tipoColor}55` }]}>
                <Text style={[styles.tipoText, { color: tipoColor }]}>
                  {getTipoLabel(tipoUsuarioId)}
                </Text>
              </View>

              {/* Stats */}
              <View style={styles.statsRow}>
                <StatBadge count={favoritos.length} label="Pontos" icon="location" />
                <View style={styles.statDivider} />
                <StatBadge count={rotasFavoritas.length} label="Rotas" icon="navigate" />
              </View>
            </View>

            {/* ── Card de informações / edição ── */}
            <View style={[styles.card, shadows.card]}>
              <View style={styles.cardTitleRow}>
                <Text style={styles.cardTitle}>
                  {editMode ? "Editar perfil" : "Informações"}
                </Text>
                {!editMode ? (
                  <PressableScale
                    onPress={() => setEditMode(true)}
                    accessibilityLabel="Editar perfil"
                    contentStyle={styles.editBtn}
                  >
                    <Ionicons name="create-outline" size={18} color={colors.primary} />
                    <Text style={styles.editBtnText}>Editar</Text>
                  </PressableScale>
                ) : null}
              </View>

              {editMode ? (
                // ── Modo edição ──
                <View style={styles.editForm}>
                  <TextField
                    value={nome}
                    onChangeText={setNome}
                    placeholder="Nome completo"
                    accessibilityLabel="Nome"
                    editable={!saving}
                  />
                  <TextField
                    value={email}
                    onChangeText={setEmail}
                    placeholder="E-mail"
                    keyboardType="email-address"
                    accessibilityLabel="E-mail"
                    editable={!saving}
                  />
                  <TextField
                    value={cpf}
                    onChangeText={setCpf}
                    placeholder="CPF"
                    keyboardType="numeric"
                    accessibilityLabel="CPF"
                    editable={!saving}
                  />
                  <TextField
                    value={sexo}
                    onChangeText={setSexo}
                    placeholder="Gênero (ex: Masculino, Feminino...)"
                    accessibilityLabel="Gênero"
                    editable={!saving}
                  />
                  <View style={styles.editActions}>
                    <Button
                      icon="save-outline"
                      onPress={handleSave}
                      loading={saving}
                      disabled={saving}
                      fullWidth
                    >
                      Salvar alterações
                    </Button>
                    <PressableScale
                      onPress={cancelEdit}
                      disabled={saving}
                      accessibilityLabel="Cancelar edição"
                      contentStyle={styles.cancelBtn}
                    >
                      <Text style={styles.cancelBtnText}>Cancelar</Text>
                    </PressableScale>
                  </View>
                </View>
              ) : (
                // ── Modo visualização ──
                <View style={styles.infoList}>
                  <InfoRow icon="person-outline" label="Nome" value={userInfo?.nome} />
                  <View style={styles.rowDivider} />
                  <InfoRow icon="mail-outline" label="E-mail" value={userInfo?.email} />
                  <View style={styles.rowDivider} />
                  <InfoRow icon="card-outline" label="CPF" value={userInfo?.cpf} />
                  <View style={styles.rowDivider} />
                  <InfoRow icon="male-female-outline" label="Gênero" value={userInfo?.sexo} />
                </View>
              )}
            </View>

            {/* ── Ações ── */}
            <View style={styles.actions}>
              <Button
                icon="pricetags-outline"
                onPress={() => navigation.navigate("Cupons")}
                fullWidth
              >
                Meus Cupons
              </Button>
              <Button
                icon="headset-outline"
                onPress={() => navigation.navigate("Contato")}
                fullWidth
              >
                Contato e Suporte
              </Button>
              <Button
                icon="log-out-outline"
                onPress={handleLogout}
                fullWidth
                style={styles.logoutBtn}
              >
                Sair da conta
              </Button>
            </View>

            {/* ── Rotas favoritas ── */}
            <View style={styles.section}>
              <SectionHeader
                title="Rotas Favoritas"
                subtitle={
                  loadingFavoritos
                    ? "Carregando…"
                    : rotasFavoritas.length === 0
                    ? "Nenhuma rota salva ainda"
                    : `${rotasFavoritas.length} rota${rotasFavoritas.length !== 1 ? "s" : ""} salva${rotasFavoritas.length !== 1 ? "s" : ""}`
                }
              />
              {loadingFavoritos ? (
                <ActivityIndicator color={colors.accent} style={{ marginTop: spacing.md }} />
              ) : rotasFavoritas.length === 0 ? (
                <EmptyFav text="Favorita rotas na aba Rotas para vê-las aqui." icon="navigate-outline" />
              ) : (
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.favRow}>
                  {rotasFavoritas.map((rota) => (
                    <PressableScale
                      key={rota.id}
                      onPress={() => setRotaSelecionada(rota)}
                      accessibilityLabel={`Rota ${rota.nome}`}
                      contentStyle={styles.favCard}
                    >
                      {rota.imagem ? (
                        <Image source={{ uri: rota.imagem }} style={styles.favImg} />
                      ) : (
                        <View style={[styles.favImg, styles.favPlaceholder]}>
                          <Ionicons name="map-outline" size={28} color={colors.accent} />
                        </View>
                      )}
                      <LinearGradient colors={["transparent", "rgba(0,0,0,0.75)"]} style={styles.favGradient}>
                        <Text style={styles.favName} numberOfLines={2}>{rota.nome}</Text>
                      </LinearGradient>
                    </PressableScale>
                  ))}
                </ScrollView>
              )}
            </View>

            {/* ── Pontos favoritos ── */}
            <View style={styles.section}>
              <SectionHeader
                title="Pontos Favoritos"
                subtitle={
                  loadingFavoritos
                    ? "Carregando…"
                    : favoritos.length === 0
                    ? "Nenhum ponto salvo ainda"
                    : `${favoritos.length} ponto${favoritos.length !== 1 ? "s" : ""} salvo${favoritos.length !== 1 ? "s" : ""}`
                }
              />
              {loadingFavoritos ? (
                <ActivityIndicator color={colors.accent} style={{ marginTop: spacing.md }} />
              ) : favoritos.length === 0 ? (
                <EmptyFav text="Favorita pontos turísticos para vê-los aqui." icon="location-outline" />
              ) : (
                <View style={styles.pontosList}>
                  {favoritos.map((favorito) => (
                    <PressableScale
                      key={favorito.id}
                      onPress={() => handlePointPress(favorito)}
                      accessibilityLabel={`Ponto ${favorito.pontos_turisticos?.nome}`}
                      contentStyle={[styles.pontoCard, shadows.soft]}
                    >
                      <View style={styles.pontoIconWrap}>
                        <Ionicons name="location" size={20} color={colors.primary} />
                      </View>
                      <Text style={styles.pontoName} numberOfLines={1}>
                        {favorito.pontos_turisticos?.nome || "Ponto turístico"}
                      </Text>
                      <TouchableOpacity
                        onPress={() => removeFavorito(favorito.ponto_id)}
                        style={styles.removeFavBtn}
                        accessibilityLabel="Remover dos favoritos"
                        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                      >
                        <Ionicons name="heart-dislike-outline" size={18} color={colors.textSecondary} />
                      </TouchableOpacity>
                    </PressableScale>
                  ))}
                </View>
              )}
            </View>

            <View style={{ height: spacing.xxl }} />
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
};

function EmptyFav({ text, icon }) {
  return (
    <View style={styles.emptyFav}>
      <Ionicons name={icon} size={32} color={colors.textSecondary} />
      <Text style={styles.emptyFavText}>{text}</Text>
    </View>
  );
}

export default AreaUsuario;

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: spacing.md },
  scrollContent: {
    paddingTop: spacing.lg,
    paddingBottom: spacing.xxl,
  },

  // ── Cabeçalho do perfil ──
  profileHeader: {
    alignItems: "center",
    paddingHorizontal: layout.contentPadding,
    paddingBottom: spacing.xl,
    gap: spacing.sm,
  },
  avatarCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    borderWidth: 3,
    backgroundColor: "rgba(200,51,73,0.18)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xs,
  },
  avatarInitials: {
    fontSize: 32,
    fontWeight: "700",
    color: colors.text,
    letterSpacing: 1,
  },
  profileName: {
    ...typography.hero,
    textAlign: "center",
  },
  tipoBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xxs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
  },
  tipoText: {
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.xs,
    backgroundColor: "rgba(255,255,255,0.07)",
    borderRadius: radius.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    gap: spacing.xl,
  },
  statBadge: {
    alignItems: "center",
    gap: spacing.xxs,
  },
  statCount: {
    ...typography.subtitle,
    fontSize: 20,
  },
  statLabel: {
    ...typography.caption,
    fontSize: 11,
  },
  statDivider: {
    width: 1,
    height: 36,
    backgroundColor: "rgba(255,255,255,0.15)",
  },

  // ── Card de informações ──
  card: {
    marginHorizontal: layout.contentPadding,
    marginBottom: spacing.md,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    overflow: "hidden",
  },
  cardTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.md,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSubtle,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 15,
  },
  editBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs + 2,
    backgroundColor: "rgba(200,51,73,0.12)",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xxs + 2,
    borderRadius: radius.pill,
  },
  editBtnText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "600",
  },

  // ── Linhas de info (view mode) ──
  infoList: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    gap: spacing.sm,
  },
  infoIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(200,51,73,0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  infoTextWrap: { flex: 1 },
  infoLabel: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.textSecondary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  infoValue: {
    ...typography.subtitle,
    fontSize: 15,
  },
  rowDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 36 + spacing.sm,
  },

  // ── Formulário de edição ──
  editForm: {
    padding: spacing.md,
    gap: spacing.xs,
  },
  editActions: {
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  cancelBtn: {
    alignItems: "center",
    paddingVertical: spacing.sm,
    marginTop: spacing.xxs,
  },
  cancelBtnText: {
    ...typography.body,
    color: colors.textSecondary,
  },

  // ── Ações ──
  actions: {
    marginHorizontal: layout.contentPadding,
    marginBottom: spacing.lg,
    gap: spacing.sm,
  },
  logoutBtn: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: "rgba(200,51,73,0.4)",
  },

  // ── Seções favoritos ──
  section: {
    marginBottom: spacing.xl,
    paddingHorizontal: layout.contentPadding,
  },
  sectionTitle: {
    ...typography.subtitle,
  },

  // Rotas favoritas (horizontal scroll)
  favRow: {
    gap: spacing.sm,
    paddingVertical: spacing.xs,
  },
  favCard: {
    width: 150,
    height: 110,
    borderRadius: radius.md,
    overflow: "hidden",
    backgroundColor: colors.surfaceElevated,
  },
  favImg: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  favPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceElevated,
  },
  favGradient: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "55%",
    justifyContent: "flex-end",
    padding: spacing.xs,
  },
  favName: {
    ...typography.caption,
    fontSize: 12,
    fontWeight: "700",
  },

  // Pontos favoritos (lista vertical)
  pontosList: {
    gap: spacing.xs,
  },
  pontoCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  pontoIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(200,51,73,0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  pontoName: {
    ...typography.subtitle,
    fontSize: 14,
    flex: 1,
  },
  removeFavBtn: {
    padding: spacing.xxs,
  },

  // Empty state
  emptyFav: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    backgroundColor: "rgba(255,255,255,0.04)",
    borderRadius: radius.md,
    marginTop: spacing.xs,
  },
  emptyFavText: {
    ...typography.body,
    flex: 1,
    fontSize: 13,
  },
});
