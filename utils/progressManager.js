import AsyncStorage from "@react-native-async-storage/async-storage";

// Chave para armazenar o progresso de todas as rotas
const PROGRESS_KEY = "kapitour_progresso_rotas";

// Salvar progresso de uma rota específica
export const salvarProgressoRota = async (rotaId, pontos) => {
  try {
    const progressoData = {
      rotaId,
      pontos: pontos.map(p => ({
        id: p.id,
        completed: p.completed,
        rating: typeof p.rating === 'number' ? p.rating : null,
      })),
      timestamp: new Date().toISOString()
    };
    
    await AsyncStorage.setItem(
      `progresso_rota_${rotaId}`,
      JSON.stringify(progressoData)
    );
    
    // Também salvar no registro geral
    await salvarNoRegistroGeral(rotaId, progressoData);
    
    return true;
  } catch (error) {
    console.error("Erro ao salvar progresso da rota:", error);
    return false;
  }
};

// Carregar progresso de uma rota específica
export const carregarProgressoRota = async (rotaId) => {
  try {
    const progressoSalvo = await AsyncStorage.getItem(`progresso_rota_${rotaId}`);
    if (progressoSalvo) {
      const progressoData = JSON.parse(progressoSalvo);
      return progressoData.pontos;
    }
  } catch (error) {
    console.error("Erro ao carregar progresso da rota:", error);
  }
  return null;
};

// Limpar progresso de uma rota específica
export const limparProgressoRota = async (rotaId) => {
  try {
    await AsyncStorage.removeItem(`progresso_rota_${rotaId}`);
    await removerDoRegistroGeral(rotaId);
    return true;
  } catch (error) {
    console.error("Erro ao limpar progresso da rota:", error);
    return false;
  }
};

// Obter estatísticas de progresso de todas as rotas
export const obterEstatisticasProgresso = async () => {
  try {
    const registroGeral = await AsyncStorage.getItem(PROGRESS_KEY);
    if (registroGeral) {
      return JSON.parse(registroGeral);
    }
  } catch (error) {
    console.error("Erro ao obter estatísticas de progresso:", error);
  }
  return {};
};

// Funções auxiliares
const salvarNoRegistroGeral = async (rotaId, progressoData) => {
  try {
    const registroGeral = await AsyncStorage.getItem(PROGRESS_KEY);
    const registro = registroGeral ? JSON.parse(registroGeral) : {};
    
    registro[rotaId] = {
      ultimaAtualizacao: progressoData.timestamp,
      pontosCompletados: progressoData.pontos.filter(p => p.completed).length,
      totalPontos: progressoData.pontos.length
    };
    
    await AsyncStorage.setItem(PROGRESS_KEY, JSON.stringify(registro));
  } catch (error) {
    console.error("Erro ao salvar no registro geral:", error);
  }
};

const removerDoRegistroGeral = async (rotaId) => {
  try {
    const registroGeral = await AsyncStorage.getItem(PROGRESS_KEY);
    if (registroGeral) {
      const registro = JSON.parse(registroGeral);
      delete registro[rotaId];
      await AsyncStorage.setItem(PROGRESS_KEY, JSON.stringify(registro));
    }
  } catch (error) {
    console.error("Erro ao remover do registro geral:", error);
  }
};
