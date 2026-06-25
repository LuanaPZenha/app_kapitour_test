import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
  ActivityIndicator,
  Image,
  ImageBackground,
  Alert,
  Dimensions,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { dbApi } from "../lib/api";
import { LinearGradient } from "expo-linear-gradient";
import { salvarProgressoRota, carregarProgressoRota } from "../utils/progressManager";
import ProgressBar from "../components/ProgressBar";
import RatingStars from "../components/RatingStars";
import Card from "../components/Card";
import Button from "../components/Button";
import { submitRating, getAverageRating } from "../services/ratings";
import { colors } from "../theme/colors";
import { prefetchImages } from "../utils/images";
import { gradients } from "../theme/gradients";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useAuth } from "../hooks/useAuth";

export default function DetalhesRota({ rota, voltar }) {
  const [pontos, setPontos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isStarted, setIsStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentRating, setCurrentRating] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [avgRating, setAvgRating] = useState(null);
  const windowHeight = Dimensions.get("window").height;
  const insets = useSafeAreaInsets();
  const { userInfo } = useAuth();
  const GAP_FROM_TAB = 10;
  const HEADER_OFFSET = 150;
  const cardMinHeight = Math.max(300, windowHeight - (insets.top || 55) - HEADER_OFFSET - (insets.bottom || 90) - GAP_FROM_TAB);

  useEffect(() => {
    const fetchPontosDaRota = async () => {
      const { data: relData, error: errorRel } = await dbApi.listRotaPontoByRota(rota.id);
      const relacionamentos = relData || [];

      if (errorRel) {
        console.error("Erro rota_ponto:", errorRel);
        setLoading(false);
        return;
      }

      const pontoIds = relacionamentos.map((rel) => rel.ponto_id);

      const { data: pontosData, error: errorPontos } = await dbApi.getPontosByIds(pontoIds);

      if (errorPontos) {
        console.error("Erro pontos_turisticos:", errorPontos);
      } else {
        // Carregar progresso salvo
        const progressoSalvo = await carregarProgressoRota(rota.id);
        // Ordena pontos pela ordem da relação
        const orderedIds = relacionamentos.sort((a,b)=>a.ordem-b.ordem).map(r=>r.ponto_id);
        const orderedPontos = orderedIds
          .map(id => pontosData.find(p => p.id === id))
          .filter(Boolean);

        const pontosComProgresso = orderedPontos.map((p) => {
          const pontoSalvo = progressoSalvo?.find(ps => ps.id === p.id);
          return {
            ...p,
            completed: pontoSalvo ? pontoSalvo.completed : false,
            rating: pontoSalvo && typeof pontoSalvo.rating === 'number' ? pontoSalvo.rating : null,
          };
        });
        
        setPontos(pontosComProgresso);
      }

      setLoading(false);
    };

    fetchPontosDaRota();
  }, [rota.id]);

  useEffect(() => {
    setImageLoaded(false);
    if (isStarted) {
      prefetchImages([
        pontos[currentIndex]?.url_img,
        pontos[currentIndex + 1]?.url_img,
      ]);
    }
  }, [isStarted, currentIndex, pontos]);

  useEffect(() => {
    const loadAvg = async () => {
      const id = pontos[currentIndex]?.id;
      if (isStarted && id) {
        try {
          const avg = await getAverageRating(id);
          setAvgRating(avg);
        } catch {
          setAvgRating(null);
        }
      } else {
        setAvgRating(null);
      }
    };
    loadAvg();
  }, [isStarted, currentIndex, pontos]);

  

  const progresso = pontos.length
    ? (pontos.filter((p) => p.completed).length / pontos.length) * 100
    : 0;

  if (loading) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.containerPrincipal}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Carregando detalhes da rota...</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient {...gradients.appBg} style={styles.containerPrincipal}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[styles.contentContainer, { paddingTop: (insets.top || 55), paddingBottom: (insets.bottom || 90) + GAP_FROM_TAB }]}
      >
        <View style={styles.progressContainer}>
          <ProgressBar percent={progresso} badgeText={isStarted && pontos.length > 0 ? `Ponto ${currentIndex + 1} de ${pontos.length}` : null} />
        </View>

        {!isStarted ? (
          <>
            <TouchableOpacity onPress={voltar} style={styles.voltar}>
              <Text style={styles.voltarText}>← Voltar</Text>
            </TouchableOpacity>

            <Text style={styles.titulo}>{rota.nome}</Text>
            <Text style={styles.descricao}>{rota.descricao}</Text>

            <Button
              icon="play"
              onPress={() => {
                const firstIncompleteIndex = pontos.findIndex(p => !p.completed);
                setCurrentIndex(firstIncompleteIndex >= 0 ? firstIncompleteIndex : 0);
                setCurrentRating(0);
                setIsStarted(true);
              }}
              fullWidth
            >
              Iniciar rota
            </Button>
          </>
        ) : (
          <Card
            imageUrl={pontos[currentIndex]?.url_img}
            title={pontos[currentIndex]?.nome}
            description={pontos[currentIndex]?.descricao}
            showBack={currentIndex > 0}
            onBack={() => {
              const prev = currentIndex - 1;
              setCurrentIndex(prev);
              setCurrentRating(pontos[prev]?.rating || 0);
            }}
            style={{ minHeight: cardMinHeight, marginBottom: 10 }}
          >
            {avgRating !== null ? (
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <Ionicons name="star" size={16} color={colors.accent} />
                <Text style={{ color: colors.textMuted }}>Média: {avgRating}</Text>
              </View>
            ) : null}
            <RatingStars value={currentRating} onChange={setCurrentRating} />
            <View style={styles.fullButtons}>
              <Button icon="navigate" onPress={() => Linking.openURL(`https://www.google.com/maps/dir/?api=1&destination=${pontos[currentIndex]?.latitude},${pontos[currentIndex]?.longitude}`)} fullWidth style={{ marginBottom: 8 }}>
                Abrir no GPS
              </Button>
              <Button icon="arrow-forward" onPress={async () => {
                if (currentRating === 0) {
                  Alert.alert("Avaliação necessária", "Avalie este ponto antes de prosseguir.");
                  return;
                }
                const updated = [...pontos];
                updated[currentIndex] = { ...updated[currentIndex], completed: true, rating: currentRating };
                setPontos(updated);
                await salvarProgressoRota(rota.id, updated);
                try { await submitRating(updated[currentIndex].id, userInfo?.id ?? null, currentRating); } catch {}
                const nextIndex = currentIndex + 1;
                if (nextIndex >= updated.length) {
                  setIsStarted(false);
                } else {
                  setCurrentIndex(nextIndex);
                  setCurrentRating(0);
                }
              }} fullWidth>
                Próximo
              </Button>
            </View>
          </Card>
        )}

        

      </ScrollView>

    </LinearGradient>
  );
}
const styles = StyleSheet.create({
  // Estilos principais seguindo o padrão do Rotas.jsx
  containerPrincipal: {
    flex: 1,
  },
  scroll: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  contentContainer: {
    padding: 20,
    paddingTop: 55,
    alignItems: "center",
  },
  
  // Loading
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingTop: 55,
  },
  loadingText: {
    color: "#fff",
    marginTop: 10,
    fontSize: 16,
  },

  // Botão voltar melhorado
  voltar: {
    backgroundColor: "#c3073f",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    marginBottom: 20,
    alignSelf: "flex-start",
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  voltarText: { 
    color: "#fff", 
    fontSize: 16,
    fontWeight: "bold",
  },

  // Títulos seguindo o padrão
  titulo: { 
    fontSize: 24, 
    fontWeight: "bold", 
    color: "#fff",
    textAlign: "center",
    marginBottom: 10,
  },
  descricao: { 
    color: "#eee", 
    marginBottom: 20,
    textAlign: "center",
    fontSize: 16,
    lineHeight: 22,
  },

  // Progresso
  progressContainer: {
    width: "100%",
    marginBottom: 25,
  },
  progressText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 8,
    textAlign: "center",
  },
  progressBar: {
    height: 12,
    backgroundColor: "rgba(255, 255, 255, 0.2)",
    borderRadius: 6,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#f7a000",
    borderRadius: 6,
  },
  stepBadge: {
    alignSelf: "center",
    marginTop: 8,
    backgroundColor: "#2c2338",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  stepBadgeText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  buttonInline: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },

  // Cards dos pontos seguindo o padrão do Rotas.jsx
  gpsButton: {
    backgroundColor: "#f7a000",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: "center",
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  gpsText: { 
    color: "#fff", 
    fontWeight: "bold",
    fontSize: 16,
  },
  startButton: {
    backgroundColor: "#f7a000",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
    alignItems: "center",
    alignSelf: "center",
    marginBottom: 20,
  },
  startText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  fullCard: {
    backgroundColor: "#1a1a2e",
    borderRadius: 16,
    padding: 16,
  },
  fullCardBg: {
    width: "100%",
    minHeight: 420,
    borderRadius: 16,
    overflow: "hidden",
    position: "relative",
  },
  fullCardBgImage: {
    resizeMode: "cover",
  },
  imagePlaceholder: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.2)",
    justifyContent: "center",
    alignItems: "center",
  },
  fullOverlayContent: {
    padding: 16,
    backgroundColor: "rgba(0,0,0,0.45)",
    flex: 1,
    justifyContent: "flex-end",
  },
  backOverlayButton: {
    position: "absolute",
    top: 12,
    left: 12,
    backgroundColor: "rgba(0,0,0,0.4)",
    padding: 10,
    borderRadius: 24,
    zIndex: 2,
  },
  fullTitle: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 6,
  },
  fullDesc: {
    color: "#ddd",
    marginBottom: 12,
  },
  ratingRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 8,
    marginBottom: 16,
  },
  fullButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "center",
  },
  nextButton: {
    backgroundColor: "#c3073f",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: "center",
  },
  nextText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
});
