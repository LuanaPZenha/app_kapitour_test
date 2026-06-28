import { api } from "../lib/api";

export async function submitRating(pontoId, _usuarioId, nota, comentario = null) {
  try {
    const { data } = await api.post("/ponto-avaliacoes", {
      ponto_id: pontoId,
      nota,
      comentario,
    });
    return { data, error: null };
  } catch (error) {
    return { data: null, error: { message: error.message } };
  }
}

export async function getAverageRating(pontoId) {
  try {
    const { data } = await api.get("/ponto-avaliacoes/media", { params: { ponto_id: pontoId } });
    return data.media || 0;
  } catch {
    return 0;
  }
}
