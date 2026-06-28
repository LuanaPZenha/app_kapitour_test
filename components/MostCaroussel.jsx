import React, { useEffect, useState, useCallback } from "react";
import { View, ScrollView, StyleSheet, Alert } from "react-native";
import { dbApi } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import RouteCarouselCard from "./RouteCarouselCard";
import { spacing } from "../theme/spacing";

const buildRoutesPayload = async () => {
  const { data: rotas, error } = await dbApi.listRotas();
  if (error) {
    console.error("Erro ao buscar rotas:", error.message);
    return [];
  }

  const rotasComPontos = await Promise.all(
    (rotas || []).map(async (rota) => {
      const { data: rotaPontos } = await dbApi.listRotaPontoByRota(rota.id);
      return { ...rota, rota_ponto: rotaPontos || [] };
    })
  );

  const allPontoIds = [
    ...new Set(
      rotasComPontos
        .flatMap((rota) => (rota.rota_ponto || []).map((p) => p.ponto_id))
        .filter(Boolean)
    ),
  ];

  const firstPointIds = rotasComPontos
    .map((rota) => {
      const pontosOrdenados = (rota.rota_ponto || []).sort((a, b) => a.ordem - b.ordem);
      return pontosOrdenados[0]?.ponto_id ?? null;
    })
    .filter(Boolean);

  const uniqueFirstPointIds = [...new Set(firstPointIds)];
  const { data: pontosData } = await dbApi.getPontosByIds(uniqueFirstPointIds);
  const pontosMap = new Map((pontosData || []).map((p) => [p.id, p.url_img]));

  const { data: pontoCategorias } = await dbApi.listPontoCategoriaByPontos(allPontoIds);
  const categoriaIds = [...new Set((pontoCategorias || []).map((pc) => pc.categoria_id))];

  let categoriasNomesMap = new Map();
  if (categoriaIds.length > 0) {
    const { data: categorias } = await dbApi.listCategorias();
    categoriasNomesMap = new Map(
      (categorias || []).filter((c) => categoriaIds.includes(c.id)).map((c) => [c.id, c.nome])
    );
  }

  const rotaCategoriasMap = new Map();
  (pontoCategorias || []).forEach((pc) => {
    const nome = categoriasNomesMap.get(pc.categoria_id);
    if (!nome) return;
    const list = rotaCategoriasMap.get(pc.ponto_id) || [];
    list.push(nome);
    rotaCategoriasMap.set(pc.ponto_id, list);
  });

  return rotasComPontos
    .map((rota) => {
      const pontosOrdenados = (rota.rota_ponto || []).sort((a, b) => a.ordem - b.ordem);
      if (pontosOrdenados.length === 0) return null;

      const firstId = pontosOrdenados[0].ponto_id;
      const names = (rota.rota_ponto || [])
        .flatMap((rp) => rotaCategoriasMap.get(rp.ponto_id) || []);
      const uniqueNames = [...new Set(names)];

      return {
        id: rota.id,
        nome: rota.nome,
        imagem: pontosMap.get(firstId) || null,
        categorias: uniqueNames,
        pontoId: firstId,
      };
    })
    .filter(Boolean);
};

export default function MostCaroussel({ onRotaPress }) {
  const [rotas, setRotas] = useState([]);
  const [favoritos, setFavoritos] = useState([]);
  const { user } = useAuth();
  const [userInfo, setUserInfo] = useState(null);

  const fetchFavoritos = useCallback(async () => {
    const { data, error } = await dbApi.listFavoritos();
    if (error) {
      console.error("Erro ao buscar favoritos:", error);
      return;
    }
    setFavoritos(data?.map((f) => f.ponto_id) || []);
  }, []);

  useEffect(() => {
    buildRoutesPayload().then(setRotas);
  }, []);

  useEffect(() => {
    if (!user?.id) return;

    dbApi.getUserByAuthId(user.id).then(({ data, error }) => {
      if (error || !data) {
        console.error("Erro ao buscar informações do usuário:", error);
        return;
      }
      setUserInfo(data);
      fetchFavoritos();
    });
  }, [user, fetchFavoritos]);

  const isFavorito = (pontoId) => favoritos.includes(pontoId);

  const toggleFavorito = async (pontoId) => {
    if (!user?.id || !userInfo) {
      Alert.alert("Atenção", "Você precisa estar logado para favoritar pontos turísticos.");
      return;
    }

    try {
      if (isFavorito(pontoId)) {
        const { error } = await dbApi.removeFavorito(pontoId);
        if (error) throw error;
        setFavoritos((prev) => prev.filter((id) => id !== pontoId));
      } else {
        const { error } = await dbApi.addFavorito(pontoId);
        if (error) throw error;
        setFavoritos((prev) => [...prev, pontoId]);
      }
    } catch (err) {
      console.error("Erro ao atualizar favorito:", err);
      Alert.alert("Erro", "Não foi possível atualizar o favorito.");
    }
  };

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.list}
    >
      {rotas.map((rota) => (
        <View key={rota.id} style={styles.item}>
          <RouteCarouselCard
            nome={rota.nome}
            imagem={rota.imagem}
            categorias={rota.categorias}
            isFavorito={isFavorito(rota.pontoId)}
            onPress={() => onRotaPress?.(rota)}
            onToggleFavorito={() => toggleFavorito(rota.pontoId)}
          />
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  list: {
    paddingVertical: spacing.sm,
    paddingRight: spacing.xs,
  },
  item: {
    marginHorizontal: spacing.xs,
  },
});
