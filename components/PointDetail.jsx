import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Linking,
  ScrollView,
  Dimensions,
  Modal,
  TextInput,
  Alert,
} from "react-native";
import { handleError } from "../utils/errors";
import Button from "./Button";
import Animated, { FadeIn, FadeOut } from "react-native-reanimated";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { dbApi } from "../lib/api";
import { useAuth } from "../hooks/useAuth";

const { height } = Dimensions.get("window");

const PointDetail = ({
  point,
  onClose,
  distance,
  onFavorite,
  isFavorite: propIsFavorite,
}) => {
  const { user } = useAuth();
  const [userInfo, setUserInfo] = useState(null);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [pointRating, setPointRating] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isFavorite, setIsFavorite] = useState(propIsFavorite);

  useEffect(() => {
    if (user?.id) {
      fetchUserInfo();
      fetchPointRating();
      checkFavoriteStatus();
    }
  }, [user, point]);

  useEffect(() => {
    setIsFavorite(propIsFavorite);
  }, [propIsFavorite]);

  // Buscar informações do usuário
  const fetchUserInfo = async () => {
    try {
      const { data, error } = await dbApi.getUserByAuthId(user.id);

      if (error || !data) {
        console.error("Erro ao buscar informações do usuário:", error);
        return;
      }

      setUserInfo(data);
    } catch (err) {
      console.error("Erro inesperado:", err);
    }
  };

  // Verificar status de favorito
  const checkFavoriteStatus = async () => {
    if (!user?.id || !userInfo) return;

    try {
      const { data, error } = await dbApi.getFavorito(userInfo.id, point.id);

      if (error && error.code !== "PGRST116") {
        console.error("Erro ao verificar favorito:", error);
        return;
      }

      setIsFavorite(!!data);
    } catch (err) {
      console.error("Erro inesperado:", err);
    }
  };

  // Alternar favorito
  const toggleFavorito = async () => {
    if (!user?.id) {
      handleError("PointDetail.toggleFavorito", new Error("Not logged in"), "Você precisa estar logado para favoritar pontos turísticos.");
      return;
    }

    if (!userInfo) {
      handleError("PointDetail.toggleFavorito", new Error("User info missing"), "Não foi possível obter suas informações. Tente novamente.");
      return;
    }

    try {
      if (isFavorite) {
        // Remover dos favoritos
        const { error } = await dbApi.removeFavorito(point.id);

        if (error) throw error;
        setIsFavorite(false);
      } else {
        // Adicionar aos favoritos
        const { error } = await dbApi.addFavorito(point.id);

        if (error) throw error;
        setIsFavorite(true);
      }

      // Notificar o componente pai sobre a mudança
      if (onFavorite) {
        onFavorite(point.id, !isFavorite);
      }
    } catch (err) {
      handleError("PointDetail.toggleFavorito", err, "Não foi possível atualizar seus favoritos.");
    }
  };

  // Buscar avaliação média do ponto
  const fetchPointRating = async () => {
    try {
      const { data, error } = await dbApi.listAvaliacoes(point.id);

      if (error) {
        console.error("Erro ao buscar avaliações:", error);
        return;
      }

      if (data && data.length > 0) {
        const average =
          data.reduce((sum, item) => sum + item.nota, 0) / data.length;
        setPointRating(Math.round(average));
      }
    } catch (err) {
      console.error("Erro inesperado:", err);
    }
  };

  // Salvar avaliação
  const saveRating = async () => {
    if (!user?.id || !userInfo) {
      handleError("PointDetail.saveRating", new Error("Not logged in"), "Você precisa estar logado para avaliar pontos turísticos.");
      setShowRatingModal(false);
      return;
    }

    if (rating === 0) {
      handleError("PointDetail.saveRating", new Error("Invalid rating"), "Por favor, selecione uma avaliação de 1 a 5 estrelas.");
      return;
    }

    setLoading(true);

    try {
      // Verificar se o usuário já avaliou este ponto
      const result = await dbApi.saveAvaliacao({
        ponto_id: point.id,
        nota: rating,
        comentario: comment,
      });

      if (result.error) throw result.error;

      Alert.alert("Sucesso", "Sua avaliação foi salva com sucesso!");
      setShowRatingModal(false);
      fetchPointRating(); // Atualizar a avaliação média
    } catch (err) {
      handleError("PointDetail.saveRating", err, "Não foi possível salvar sua avaliação.");
    } finally {
      setLoading(false);
    }
  };

  // Função para abrir o Google Maps com as coordenadas do ponto
  const openInMaps = () => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${point.latitude},${point.longitude}`;
    Linking.openURL(url);
  };

  // Calcula o tempo estimado (5 min por km, aproximadamente)
  const safeDistance = distance || 0;
  const estimatedTime = Math.round(safeDistance * 5);
  const hours = Math.floor(estimatedTime / 60);
  const minutes = estimatedTime % 60;
  const timeText = hours > 0 ? `${hours} h ${minutes} min` : `${minutes} min`;

  return (
    <SafeAreaView style={styles.container}>
      {/* Imagem de fundo */}
      {point.url_img ? (
        <Animated.Image
          sharedTransitionTag={`point-image-${point.id}`}
          source={{ uri: point.url_img }}
          style={styles.backgroundImage}
          resizeMode="cover"
        />
      ) : null}

      {/* Botões superiores */}
      <View style={styles.topButtons}>
        <TouchableOpacity style={styles.backButton} onPress={onClose}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.favoriteButton}
          onPress={toggleFavorito}
        >
          <Ionicons
            name={isFavorite ? "star" : "star-outline"}
            size={24}
            color={isFavorite ? "#f7a000" : "#fff"}
          />
        </TouchableOpacity>
      </View>

      {/* Card de informações */}
      <Animated.View style={styles.infoCard} entering={FadeIn.duration(200)}>
        <View style={styles.contentContainer}>
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={true}
          >
            <Animated.Text
              sharedTransitionTag={`point-title-${point.id}`}
              style={styles.title}
            >
              {point.nome}
            </Animated.Text>
            <View style={styles.ratingContainer}>
              <View style={styles.starsRow}>
                <View style={styles.starsContainer}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Ionicons
                      key={star}
                      name={
                        star <= (pointRating || point.rating || 0)
                          ? "star"
                          : "star-outline"
                      }
                      size={18}
                      color="#f7a000"
                      style={styles.starIcon}
                    />
                  ))}
                </View>

                {pointRating > 0 && (
                  <Text style={styles.ratingNumber}>
                    {pointRating.toFixed(1)}
                  </Text>
                )}
              </View>
            </View>

            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>
                  {safeDistance.toFixed(1)} km
                </Text>
                <Text style={styles.statLabel}>Distância</Text>
              </View>

              <View style={styles.statDivider} />

              <View style={styles.statItem}>
                <Text style={styles.statValue}>{timeText}</Text>
                <Text style={styles.statLabel}>Tempo estimado</Text>
              </View>
            </View>

            <Text style={styles.description}>
              {point.descricao ||
                `${point.nome} é um local favorito entre moradores e visitantes! Este ponto turístico oferece vistas deslumbrantes e experiências únicas. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.`}
            </Text>

            {/* Espaço adicional para garantir que o conteúdo role acima dos botões fixos */}
            <View style={styles.bottomPadding} />
          </ScrollView>
        </View>

        <View style={styles.fixedActionButtons}>
          <Button
            icon="star-outline"
            onPress={() => {
              if (!user) {
                Alert.alert(
                  "Atenção",
                  "Você precisa estar logado para avaliar pontos turísticos."
                );
                return;
              }
              setShowRatingModal(true);
            }}
            style={styles.actionButton}
          >
            Avaliar
          </Button>

          <Button icon="navigate-outline" onPress={openInMaps} style={styles.actionButton}>
            Visitar
          </Button>
        </View>
      </Animated.View>

      {/* Modal de Avaliação */}
      <Modal
        visible={showRatingModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowRatingModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Avaliar {point.nome}</Text>

            <View style={styles.ratingStarsContainer}>
              {[1, 2, 3, 4, 5].map((star) => (
                <TouchableOpacity key={star} onPress={() => setRating(star)}>
                  <Ionicons
                    name={star <= rating ? "star" : "star-outline"}
                    size={32}
                    color="#f7a000"
                    style={styles.ratingStarIcon}
                  />
                </TouchableOpacity>
              ))}
            </View>

            <TextInput
              style={styles.commentInput}
              placeholder="Deixe um comentário (opcional)"
              multiline={true}
              numberOfLines={4}
              value={comment}
              onChangeText={setComment}
            />

            <View style={styles.modalButtons}>
              <Button
                onPress={() => {
                  setShowRatingModal(false);
                  setRating(0);
                  setComment("");
                }}
                style={styles.modalActionButton}
              >
                Cancelar
              </Button>

              <Button
                icon="checkmark-outline"
                onPress={saveRating}
                disabled={loading}
                style={styles.modalActionButton}
              >
                {loading ? "Salvando..." : "Enviar Avaliação"}
              </Button>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  backgroundImage: {
    width: "100%",
    height: "45%",
  },
  topButtons: {
    position: "absolute",
    top: 20,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    zIndex: 10,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  favoriteButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  infoCard: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "60%",
    backgroundColor: "#fff",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  contentContainer: {
    flex: 1,
    paddingBottom: 80, // Espaço para os botões fixos
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#000",
    marginBottom: 8,
  },
  ratingContainer: {
    marginBottom: 20,
  },
  starsContainer: {
    flexDirection: "row",
    marginBottom: 4,
  },
  starIcon: {
    marginRight: 2,
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: "#eee",
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#000",
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: "#666",
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: "#eee",
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
    color: "#333",
    marginBottom: 20,
  },
  bottomPadding: {
    height: 20,
  },
  fixedActionButtons: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "#fff",
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: "#eee",
    gap: 12,
  },
  actionButton: {
    flex: 1,
    height: 44,
  },
  // Estilos para o modal de avaliação
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  modalContent: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 24,
    width: "100%",
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#000",
    marginBottom: 20,
    textAlign: "center",
  },
  ratingStarsContainer: {
    flexDirection: "row",
    justifyContent: "center",
    marginBottom: 24,
  },
  ratingStarIcon: {
    marginHorizontal: 8,
  },
  commentInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    height: 100,
    textAlignVertical: "top",
    marginBottom: 24,
  },
  modalButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 8,
  },
  modalActionButton: {
    flex: 1,
    height: 44,
  },
  starsRow: {
  flexDirection: 'row',
  alignItems: 'center',
},
ratingNumber: {
  marginLeft: 8,
  fontSize: 16,
  fontWeight: 'bold',
  color: '#f7a000',
},
});

export default PointDetail;
