import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { gradients } from "../theme/gradients";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useAuth } from "../hooks/useAuth";
import Button from "../components/Button";
import { dbApi } from "../lib/api";
import { buscarCuponsDisponiveis, verificarCupomResgatado, verificarResgatePorCampanha, resgatarCupom } from "../utils/cupomManager";
import { handleError, handleNetworkError } from "../utils/errors";

const LeitorQR = () => {
  const navigation = useNavigation();
  const { userInfo } = useAuth();
  const [showCuponsModal, setShowCuponsModal] = useState(false);
  const [cuponsDisponiveis, setCuponsDisponiveis] = useState([]);
  const [usuarioEscaneado, setUsuarioEscaneado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [redeemingId, setRedeemingId] = useState(null);
  const [cupomSelecionado, setCupomSelecionado] = useState(null);

  // 👇 trava de leitura
  const [scanned, setScanned] = useState(false);

  const [facing, setFacing] = useState("back");
  const [permission, requestPermission] = useCameraPermissions();

  useEffect(() => {
    if (userInfo?.tipo_usuario_id === 2) {
      fetchCuponsDisponiveis();
    }
  }, [userInfo]);

  const fetchCuponsDisponiveis = async () => {
    try {
      setLoading(true);
      const result = await buscarCuponsDisponiveis(userInfo.id);

      if (result.success) {
        setCuponsDisponiveis(result.data);
      } else {
        Alert.alert("Erro", result.error);
      }
    } catch (error) {
      console.error("Erro ao buscar cupons:", error);
      Alert.alert("Erro", "Não foi possível carregar os cupons");
    } finally {
      setLoading(false);
    }
  };

  const handleQRCodeScanned = async ({ data }) => {
    if (scanned) return; // 👈 impede leitura múltipla
    setScanned(true); // trava até o usuário fechar modal ou alerta

    try {
      setLoading(true);

      const { data: usuario, error: usuarioError } = await dbApi.getUserByAuthId(data);

      if (usuarioError || !usuario) throw new Error(usuarioError?.message || "Usuário não encontrado");

      setUsuarioEscaneado(usuario);
      setShowCuponsModal(true);
    } catch (error) {
      handleNetworkError("LeitorQR.handleQRCodeScanned", error);
      setScanned(false);
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (cupom) => {
    if (!usuarioEscaneado) return;
    try {
      setRedeemingId(cupom.id);

      // 1) Impedir resgate repetido do mesmo cupom
      const checkCupom = await verificarCupomResgatado(cupom.id, usuarioEscaneado.id);
      if (!checkCupom.success) throw new Error(checkCupom.error);
      if (checkCupom.jaResgatado) {
        Alert.alert('Atenção', 'Este usuário já resgatou este cupom.');
        return;
      }

      // 2) Impedir resgate repetido na mesma campanha
      if (cupom.campanha_id) {
        const checkCampanha = await verificarResgatePorCampanha(cupom.campanha_id, usuarioEscaneado.id);
        if (!checkCampanha.success) throw new Error(checkCampanha.error);
        if (checkCampanha.jaResgatouCampanha) {
          Alert.alert('Atenção', 'Este usuário já resgatou um cupom desta campanha.');
          return;
        }
      }

      // 3) Resgatar
      const result = await resgatarCupom(cupom.id, usuarioEscaneado.id, userInfo.id);
      if (!result.success) throw new Error(result.error);

      Alert.alert('Sucesso', 'Cupom resgatado com sucesso!', [
        {
          text: 'OK',
          onPress: () => {
            setShowCuponsModal(false);
            setScanned(false);
            setUsuarioEscaneado(null);
            // Voltar para área do usuário
            navigation.goBack();
          }
        }
      ]);
    } catch (error) {
      handleError("LeitorQR.handleRedeem", error, error.message || "Não foi possível resgatar o cupom.");
    } finally {
      setRedeemingId(null);
    }
  };

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>
          Precisamos da sua permissão para acessar a câmera
        </Text>
        <Button onPress={requestPermission} fullWidth style={{ marginTop: 16, alignSelf: "center", width: 260 }}>
          Conceder permissão
        </Button>
      </View>
    );
  }

  return (
    <LinearGradient
      {...gradients.appBg}
      style={styles.container}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <MaterialCommunityIcons name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Leitor de QR Code</Text>
      </View>

      {/* Câmera */}
      <View style={styles.content}>
        <CameraView
          style={styles.camera}
          facing={facing}
          onBarcodeScanned={scanned ? undefined : handleQRCodeScanned} // 👈 só chama se não estiver travado
          barcodeScannerSettings={{ barCodeTypes: ["qr"] }}
        />

        <TouchableOpacity
          style={styles.flipButton}
          onPress={() =>
            setFacing((current) => (current === "back" ? "front" : "back"))
          }
        >
          <MaterialCommunityIcons name="camera-switch" size={32} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Modal de Cupons */}
      <Modal
        visible={showCuponsModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => {
          setShowCuponsModal(false);
          setScanned(false); // 👈 libera nova leitura quando fecha modal
        }}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={{ fontSize: 18, marginBottom: 10 }}>
              Usuário Escaneado:
            </Text>
            {usuarioEscaneado ? (
              <>
                <Text style={{ marginBottom: 12 }}>{usuarioEscaneado.nome}</Text>
                <Text style={{ fontWeight: 'bold', marginBottom: 8 }}>Selecione um cupom para resgatar:</Text>
                {cuponsDisponiveis.length === 0 ? (
                  <Text>Não há cupons disponíveis.</Text>
                ) : (
                  cuponsDisponiveis.map((c) => (
                    <TouchableOpacity
                      key={c.id}
                      style={[
                        styles.couponItem,
                        (cupomSelecionado?.id === c.id) && styles.couponItemSelected,
                        redeemingId === c.id && { opacity: 0.6 }
                      ]}
                      disabled={!!redeemingId}
                      onPress={() => setCupomSelecionado(c)}
                    >
                      <Text style={{ fontWeight: 'bold' }}>{c.codigo}</Text>
                      <Text>{c.descricao}</Text>
                      <Text>Disponíveis: {c.quantidade_disponivel}</Text>
                      {c.campanha?.nome ? (
                        <Text>Campanha: {c.campanha.nome}</Text>
                      ) : null}
                      {c.campanha ? (
                        <Text>
                          {c.campanha.data_inicio ? `Início: ${c.campanha.data_inicio}` : ''}
                          {c.campanha.data_fim ? `  Fim: ${c.campanha.data_fim}` : ''}
                        </Text>
                      ) : null}
                    </TouchableOpacity>
                  ))
                )}
              </>
            ) : (
              <Text>Nenhum usuário encontrado</Text>
            )}

            <Button
              onPress={() => {
                setShowCuponsModal(false);
                setScanned(false);
              }}
              fullWidth
              style={{ marginTop: 20 }}
            >
              Fechar
            </Button>

            {cupomSelecionado && (
              <Button
                icon="checkmark-outline"
                disabled={!!redeemingId}
                onPress={() => handleRedeem(cupomSelecionado)}
                fullWidth
                style={{ marginTop: 10 }}
              >
                Confirmar
              </Button>
            )}
          </View>
        </View>
      </Modal>
    </LinearGradient>
  );
};

export default LeitorQR;

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: "row",
    alignItems: "center",
    padding: 40,
  },
  headerTitle: { color: "#fff", fontSize: 18, marginLeft: 8 },
  content: { flex: 1 },
  camera: { flex: 1 },
  flipButton: {
    position: "absolute",
    bottom: 32,
    alignSelf: "center",
    backgroundColor: "rgba(0,0,0,0.5)",
    padding: 20,
    borderRadius: 50,
  },
  message: { textAlign: "center", marginTop: 50, color: "#fff" },
  scanButton: {
    alignSelf: "center",
    backgroundColor: "#c83349",
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  scanButtonText: { color: "#fff", fontWeight: "bold" },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderRadius: 12,
    margin: 20,
    padding: 20,
  },
  closeButton: {
    marginTop: 20,
    backgroundColor: "#c83349",
    padding: 12,
    borderRadius: 8,
  },
  closeButtonText: { color: "#fff", textAlign: "center" },
  couponItem: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#f2f2f2',
    marginBottom: 10,
  },
  couponItemSelected: {
    backgroundColor: '#ffe6ea',
    borderColor: '#c83349',
    borderWidth: 2,
  },
});
