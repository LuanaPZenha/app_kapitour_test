import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
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
import PressableScale from "../components/PressableScale";
import IconButton from "../components/IconButton";
import { useAppAlert } from "../components/AppAlert";

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
    case 1:
      return "Administrador";
    case 2:
      return "Parceiro";
    case 3:
      return "Visitante";
    default:
      return "Usuário";
  }
}

function getTipoColor(tipoId) {
  switch (tipoId) {
    case 1:
      return colors.accent;
    case 2:
      return "#4a9eff";
    default:
      return colors.primary;
  }
}

function InfoRow({ icon, label, value }) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.infoIconWrap}>
        <Ionicons name={icon} size={17} color={colors.accent} />
      </View>
      <View style={styles.infoTextWrap}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value || "Não informado"}</Text>
      </View>
    </View>
  );
}

function ActionRow({ icon, label, subtitle, onPress, danger }) {
  return (
    <PressableScale
      onPress={onPress}
      accessibilityLabel={label}
      contentStyle={[styles.actionRow, danger && styles.actionRowDanger]}
    >
      <View style={[styles.actionIconWrap, danger && styles.actionIconDanger]}>
        <Ionicons name={icon} size={20} color={danger ? colors.primary : colors.accent} />
      </View>
      <View style={styles.actionTextWrap}>
        <Text style={[styles.actionLabel, danger && styles.actionLabelDanger]}>{label}</Text>
        {subtitle ? <Text style={styles.actionSubtitle}>{subtitle}</Text> : null}
      </View>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </PressableScale>
  );
}

function EmptyFav({ text, icon }) {
  return (
    <View style={styles.emptyFav}>
      <View style={styles.emptyIconWrap}>
        <Ionicons name={icon} size={28} color={colors.accent} />
      </View>
      <Text style={styles.emptyFavText}>{text}</Text>
    </View>
  );
}

const AreaUsuario = () => {
  const navigation = useNavigation();
  const { user, signOut } = useAuth();
  const { showAlert } = useAppAlert();

  const [userInfo, setUserInfo] = useState(null);
  const [tipoUsuarioId, setTipoUsuarioId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [editMode, setEditMode] = useState(false);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [cpf, setCpf] = useState("");
  const [sexo, setSexo] = useState("");

  const [favoritos, setFavoritos] = useState([]);
  const [rotasFavoritas, setRotasFavoritas] = useState([]);
  const [loadingFavoritos, setLoadingFavoritos] = useState(false);

  const [selectedPoint, setSelectedPoint] = useState(null);
  const [showPointDetail, setShowPointDetail] = useState(false);
  const [rotaSelecionada, setRotaSelecionada] = useState(null);

  useEffect(() => {
    if (!user?.id) {
      setLoading(false);
      return;
    }
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
      finally {
        setLoading(false);
      }
    })();
  }, [user]);

  const fetchFavoritos = useCallback(async () => {
    if (!userInfo) return;
    setLoadingFavoritos(true);
    try {
      const { data } = await dbApi.listFavoritos(userInfo.id);
      setFavoritos(data || []);
    } catch {}
    finally {
      setLoadingFavoritos(false);
    }
  }, [userInfo]);

  const fetchRotasFavoritas = useCallback(async () => {
    if (!userInfo) return;
    try {
      const { data: favData } = await dbApi.listFavoritos(userInfo.id);
      const pontoIds = (favData || []).map((f) => f.ponto_id);
      if (pontoIds.length === 0) {
        setRotasFavoritas([]);
        return;
      }

      const { data: rpData } = await dbApi.listRotaPontoByPontos(pontoIds);
      const rotaIds = [...new Set((rpData || []).map((r) => r.rota_id))];
      if (rotaIds.length === 0) {
        setRotasFavoritas([]);
        return;
      }

      const { data: allRotas } = await dbApi.listRotas();
      const filtradas = (allRotas || []).filter((r) => rotaIds.includes(r.id));

      const completas = await Promise.all(
        filtradas.map(async (rota) => {
          const { data: rp } = await dbApi.listRotaPontoByRota(rota.id);
          const primId = rp?.[0]?.ponto_id;
          const { data: pts } = await dbApi.getPontosByIds([primId]);
          return { ...rota, imagem: pts?.[0]?.url_img || null, pontoCount: rp?.length ?? 0 };
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
      fetchRotasFavoritas();
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

  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.center}>
          <ActivityIndicator size="large" color={colors.accent} />
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (!user) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.center}>
          <View style={styles.emptyIconWrap}>
            <Ionicons name="person-circle-outline" size={48} color={colors.accent} />
          </View>
          <Text style={styles.emptyTitle}>Não autenticado</Text>
          <Text style={styles.emptyBody}>Faça login para acessar seu perfil.</Text>
          <Button onPress={() => navigation.navigate("Perfil")} style={{ marginTop: spacing.md }}>
            Fazer login
          </Button>
        </SafeAreaView>
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
        onClose={() => {
          setShowPointDetail(false);
          setSelectedPoint(null);
        }}
        onFavoriteToggle={() => {
          fetchFavoritos();
          fetchRotasFavoritas();
        }}
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
            {/* Hero */}
            <View style={styles.hero}>
              <View style={styles.heroTitleRow}>
                <View style={styles.heroIconWrap}>
                  <Ionicons name="person" size={22} color={colors.accent} />
                </View>
                <Text style={styles.heroTitle}>Meu Perfil</Text>
              </View>
              <Text style={styles.heroSubtitle}>
                Gerencie seus dados, favoritos e preferências da conta.
              </Text>
            </View>

            {/* Avatar card */}
            <View style={styles.avatarCard}>
              <LinearGradient
                colors={[`${tipoColor}33`, "rgba(26,26,46,0.95)"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.avatarBg}
              >
                <View style={[styles.avatarCircle, { borderColor: tipoColor }]}>
                  <Text style={styles.avatarInitials}>{getInitials(userInfo?.nome)}</Text>
                </View>
                <Text style={styles.profileName}>{userInfo?.nome || "Usuário"}</Text>
                <View
                  style={[
                    styles.tipoBadge,
                    { backgroundColor: `${tipoColor}22`, borderColor: `${tipoColor}55` },
                  ]}
                >
                  <Text style={[styles.tipoText, { color: tipoColor }]}>
                    {getTipoLabel(tipoUsuarioId)}
                  </Text>
                </View>
              </LinearGradient>
            </View>

            {/* Stats */}
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Ionicons name="heart-outline" size={18} color={colors.accent} />
                <Text style={styles.statValue}>{favoritos.length}</Text>
                <Text style={styles.statLabel}>pontos</Text>
              </View>
              <View style={styles.statCard}>
                <Ionicons name="navigate-outline" size={18} color={colors.accent} />
                <Text style={styles.statValue}>{rotasFavoritas.length}</Text>
                <Text style={styles.statLabel}>rotas</Text>
              </View>
              <View style={styles.statCard}>
                <Ionicons name="ribbon-outline" size={18} color={colors.accent} />
                <Text style={styles.statValue}>KapiPass</Text>
                <Text style={styles.statLabel}>gamificação</Text>
              </View>
            </View>

            {/* Informações / edição */}
            <View style={[styles.card, shadows.card]}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardEyebrow}>DADOS PESSOAIS</Text>
                <Text style={styles.cardTitle}>
                  {editMode ? "Editar perfil" : "Informações da conta"}
                </Text>
                {!editMode ? (
                  <PressableScale
                    onPress={() => setEditMode(true)}
                    accessibilityLabel="Editar perfil"
                    contentStyle={styles.editBtn}
                  >
                    <Ionicons name="create-outline" size={16} color={colors.accent} />
                    <Text style={styles.editBtnText}>Editar</Text>
                  </PressableScale>
                ) : null}
              </View>

              {editMode ? (
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

            {/* Menu de ações */}
            <Text style={styles.sectionTitle}>Atalhos</Text>
            <View style={[styles.menuCard, shadows.card]}>
              <ActionRow
                icon="pricetags-outline"
                label="Meus Cupons"
                subtitle="Resgate e gerencie seus cupons"
                onPress={() => navigation.navigate("Cupons")}
              />
              <View style={styles.menuDivider} />
              <ActionRow
                icon="headset-outline"
                label="Contato e Suporte"
                subtitle="Fale conosco ou tire dúvidas"
                onPress={() => navigation.navigate("Contato")}
              />
              <View style={styles.menuDivider} />
              <ActionRow
                icon="log-out-outline"
                label="Sair da conta"
                subtitle="Encerrar sessão neste dispositivo"
                onPress={handleLogout}
                danger
              />
            </View>

            {/* Rotas favoritas */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Rotas Favoritas</Text>
              <Text style={styles.sectionSubtitle}>
                {loadingFavoritos
                  ? "Carregando…"
                  : rotasFavoritas.length === 0
                  ? "Nenhuma rota salva ainda"
                  : `${rotasFavoritas.length} rota${rotasFavoritas.length !== 1 ? "s" : ""} salva${rotasFavoritas.length !== 1 ? "s" : ""}`}
              </Text>

              {loadingFavoritos ? (
                <ActivityIndicator color={colors.accent} style={{ marginTop: spacing.md }} />
              ) : rotasFavoritas.length === 0 ? (
                <EmptyFav
                  text="Favorite rotas na aba Rotas para vê-las aqui."
                  icon="navigate-outline"
                />
              ) : (
                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  contentContainerStyle={styles.favRow}
                >
                  {rotasFavoritas.map((rota) => (
                    <PressableScale
                      key={rota.id}
                      onPress={() => setRotaSelecionada(rota)}
                      accessibilityLabel={`Rota ${rota.nome}`}
                      contentStyle={[styles.favCard, shadows.soft]}
                    >
                      {rota.imagem ? (
                        <Image source={{ uri: rota.imagem }} style={styles.favImg} />
                      ) : (
                        <View style={[styles.favImg, styles.favPlaceholder]}>
                          <Ionicons name="map-outline" size={24} color={colors.accent} />
                        </View>
                      )}
                      <LinearGradient
                        colors={["transparent", "rgba(0,0,0,0.82)"]}
                        style={styles.favGradient}
                      >
                        <Text style={styles.favEyebrow}>ROTEIRO</Text>
                        <Text style={styles.favName} numberOfLines={2}>
                          {rota.nome}
                        </Text>
                        {rota.pontoCount > 0 ? (
                          <Text style={styles.favMeta}>
                            {rota.pontoCount} {rota.pontoCount === 1 ? "parada" : "paradas"}
                          </Text>
                        ) : null}
                      </LinearGradient>
                    </PressableScale>
                  ))}
                </ScrollView>
              )}
            </View>

            {/* Pontos favoritos */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Pontos Favoritos</Text>
              <Text style={styles.sectionSubtitle}>
                {loadingFavoritos
                  ? "Carregando…"
                  : favoritos.length === 0
                  ? "Nenhum ponto salvo ainda"
                  : `${favoritos.length} ponto${favoritos.length !== 1 ? "s" : ""} salvo${favoritos.length !== 1 ? "s" : ""}`}
              </Text>

              {loadingFavoritos ? (
                <ActivityIndicator color={colors.accent} style={{ marginTop: spacing.md }} />
              ) : favoritos.length === 0 ? (
                <EmptyFav
                  text="Favorite pontos turísticos para vê-los aqui."
                  icon="location-outline"
                />
              ) : (
                <View style={styles.pontosList}>
                  {favoritos.map((favorito) => {
                    const pt = favorito.pontos_turisticos;
                    return (
                      <PressableScale
                        key={favorito.id}
                        onPress={() => handlePointPress(favorito)}
                        accessibilityLabel={`Ponto ${pt?.nome}`}
                        contentStyle={[styles.pontoCard, shadows.card]}
                      >
                        {pt?.url_img ? (
                          <Image
                            source={{ uri: pt.url_img }}
                            style={styles.pontoThumb}
                            resizeMode="cover"
                          />
                        ) : (
                          <View style={styles.pontoIconWrap}>
                            <Ionicons name="location" size={20} color={colors.accent} />
                          </View>
                        )}
                        <View style={styles.pontoTextWrap}>
                          <Text style={styles.pontoEyebrow}>PONTO TURÍSTICO</Text>
                          <Text style={styles.pontoName} numberOfLines={1}>
                            {pt?.nome || "Ponto turístico"}
                          </Text>
                        </View>
                        <IconButton
                          name="heart-dislike-outline"
                          onPress={() => removeFavorito(favorito.ponto_id)}
                          accessibilityLabel="Remover dos favoritos"
                          color={colors.textSecondary}
                          style={styles.removeFavBtn}
                        />
                      </PressableScale>
                    );
                  })}
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

export default AreaUsuario;

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    paddingHorizontal: layout.contentPadding,
  },
  scrollContent: {
    paddingHorizontal: layout.contentPadding,
    paddingTop: spacing.md,
    paddingBottom: spacing.xxl,
  },
  hero: {
    marginBottom: spacing.lg,
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
  avatarCard: {
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.3)",
    marginBottom: spacing.md,
    ...shadows.card,
  },
  avatarBg: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  avatarCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    backgroundColor: colors.cardBg,
    alignItems: "center",
    justifyContent: "center",
    ...shadows.accent,
  },
  avatarInitials: {
    fontSize: 28,
    fontWeight: "700",
    color: colors.text,
    letterSpacing: 1,
  },
  profileName: {
    ...typography.subtitle,
    fontSize: 20,
    textAlign: "center",
  },
  tipoBadge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xxs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
  },
  tipoText: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.6,
    textTransform: "uppercase",
  },
  statsRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  statCard: {
    flex: 1,
    alignItems: "center",
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingVertical: spacing.sm,
    gap: 2,
  },
  statValue: {
    ...typography.subtitle,
    fontSize: 16,
    color: colors.text,
    textAlign: "center",
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 10,
    textTransform: "lowercase",
  },
  card: {
    marginBottom: spacing.lg,
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    overflow: "hidden",
  },
  cardHeader: {
    paddingHorizontal: spacing.md,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSubtle,
    position: "relative",
  },
  cardEyebrow: {
    ...typography.caption,
    color: colors.accent,
    letterSpacing: 1.2,
    fontWeight: "700",
    fontSize: 9,
    marginBottom: spacing.xxs,
  },
  cardTitle: {
    ...typography.subtitle,
    fontSize: 15,
    paddingRight: 72,
  },
  editBtn: {
    position: "absolute",
    top: spacing.md,
    right: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xxs + 2,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: "rgba(247, 160, 0, 0.25)",
  },
  editBtnText: {
    color: colors.accent,
    fontSize: 12,
    fontWeight: "600",
  },
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
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  infoTextWrap: { flex: 1 },
  infoLabel: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.textSecondary,
    textTransform: "uppercase",
    letterSpacing: 0.6,
    marginBottom: 2,
  },
  infoValue: {
    ...typography.subtitle,
    fontSize: 14,
  },
  rowDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 34 + spacing.sm,
  },
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
  },
  cancelBtnText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  sectionTitle: {
    ...typography.subtitle,
    fontSize: 16,
    marginBottom: spacing.xxs,
  },
  sectionSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  menuCard: {
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    marginBottom: spacing.xl,
    overflow: "hidden",
  },
  menuDivider: {
    height: 1,
    backgroundColor: colors.borderSubtle,
    marginLeft: 56,
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  actionRowDanger: {},
  actionIconWrap: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    backgroundColor: "rgba(247, 160, 0, 0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  actionIconDanger: {
    backgroundColor: "rgba(200, 51, 73, 0.12)",
  },
  actionTextWrap: {
    flex: 1,
    gap: 2,
  },
  actionLabel: {
    ...typography.subtitle,
    fontSize: 15,
  },
  actionLabelDanger: {
    color: colors.primary,
  },
  actionSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 11,
  },
  section: {
    marginBottom: spacing.xl,
  },
  favRow: {
    gap: spacing.sm,
    paddingVertical: spacing.xxs,
  },
  favCard: {
    width: 160,
    height: 120,
    borderRadius: radius.md,
    overflow: "hidden",
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  favImg: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  favPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  favGradient: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "68%",
    justifyContent: "flex-end",
    padding: spacing.sm,
    gap: 2,
  },
  favEyebrow: {
    ...typography.caption,
    color: colors.accent,
    fontSize: 8,
    fontWeight: "700",
    letterSpacing: 1,
  },
  favName: {
    ...typography.caption,
    fontSize: 12,
    fontWeight: "700",
    color: colors.text,
  },
  favMeta: {
    ...typography.caption,
    fontSize: 10,
    color: colors.textMuted,
  },
  pontosList: {
    gap: spacing.sm,
  },
  pontoCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.cardBg,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
    padding: spacing.sm,
    gap: spacing.sm,
  },
  pontoThumb: {
    width: 52,
    height: 52,
    borderRadius: radius.md,
    flexShrink: 0,
  },
  pontoIconWrap: {
    width: 52,
    height: 52,
    borderRadius: radius.md,
    backgroundColor: "rgba(200, 51, 73, 0.12)",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  pontoTextWrap: {
    flex: 1,
    gap: 2,
  },
  pontoEyebrow: {
    ...typography.caption,
    color: colors.accent,
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 1,
  },
  pontoName: {
    ...typography.subtitle,
    fontSize: 14,
  },
  removeFavBtn: {
    padding: spacing.xxs,
  },
  emptyFav: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    gap: spacing.sm,
  },
  emptyIconWrap: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    alignItems: "center",
    justifyContent: "center",
  },
  emptyFavText: {
    ...typography.body,
    fontSize: 13,
    textAlign: "center",
    color: colors.textSecondary,
    paddingHorizontal: spacing.md,
  },
  emptyTitle: {
    ...typography.subtitle,
    textAlign: "center",
  },
  emptyBody: {
    ...typography.body,
    textAlign: "center",
  },
});
