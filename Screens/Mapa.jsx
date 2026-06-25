import React, { useEffect, useMemo, useRef, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Modal,
  Image,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { WebView } from "react-native-webview";
import * as Location from "expo-location";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { dbApi } from "../lib/api";
import PointDetail from "../components/PointDetail";
import PressableScale from "../components/PressableScale";
import { getIconForCategory as baseCategoryIcon } from "../utils/categoryIcons";
import { colors } from "../theme/colors";
import { gradients } from "../theme/gradients";
import { layout, radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { shadows } from "../theme/shadows";

function getIconForCategory(categoryName) {
  const name = (categoryName || "").toLowerCase();
  if (name.includes("restaurante") || name.includes("gastronom")) return "restaurant-outline";
  if (name.includes("hotel") || name.includes("pousada") || name.includes("hospedagem")) return "bed-outline";
  if (name.includes("parque") || name.includes("natureza")) return "leaf-outline";
  if (name.includes("cultura") || name.includes("museu")) return "color-palette-outline";
  if (name.includes("compras") || name.includes("loja")) return "cart-outline";
  if (name.includes("esporte")) return "football-outline";
  return baseCategoryIcon(categoryName);
}

function formatDistance(km) {
  if (km == null || Number.isNaN(km)) return "—";
  if (km < 1) return `${Math.round(km * 1000)} m`;
  return `${km.toFixed(1)} km`;
}

function getDistance(lat1, lon1, lat2, lon2) {
  const toRad = (v) => (v * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

const leafletHtml = `<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1" /><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" /><style>html,body,#map{height:100%;margin:0;padding:0;background:#0f142c}</style></head><body><div id="map"></div><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>(function(){var map=L.map('map',{zoomControl:true});var base=L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{attribution:'&copy;OpenStreetMap &copy;Carto',maxZoom:19});base.addTo(map);map.setView([0,0],2);var markersLayer=L.layerGroup().addTo(map);var routeLayer=L.polyline([], {color:'#FF0000', weight:4}).addTo(map);var userMarker=null;function clearMarkers(){markersLayer.clearLayers()}function setUserLocation(lat,lon){if(userMarker){map.removeLayer(userMarker)}if(lat!=null&&lon!=null){userMarker=L.circleMarker([lat,lon],{radius:6,color:'#2a93d5',fillColor:'#2a93d5',fillOpacity:1}).addTo(map)}}function setMarkers(pontos){clearMarkers();(pontos||[]).forEach(function(p){var m=L.marker([p.latitude,p.longitude]);m.on('click',function(){window.ReactNativeWebView&&window.ReactNativeWebView.postMessage(JSON.stringify({type:'markerClick',id:p.id}))});m.addTo(markersLayer)})}function setRoute(coords){routeLayer.setLatLngs(coords||[]);if(coords&&coords.length>1){var b=L.latLngBounds(coords);map.fitBounds(b,{padding:[40,40]})}}window.receive=function(payloadStr){try{var payload=JSON.parse(payloadStr);if(payload.userLocation){setUserLocation(payload.userLocation.latitude,payload.userLocation.longitude);if(!payload.skipCenter){map.setView([payload.userLocation.latitude,payload.userLocation.longitude],13)}}if(payload.pontos){setMarkers(payload.pontos)}if(payload.rotaCoords){setRoute(payload.rotaCoords)}}catch(e){}};setTimeout(function(){window.ReactNativeWebView&&window.ReactNativeWebView.postMessage(JSON.stringify({type:'ready'}))},0);})();</script></body></html>`;

export default function Mapa() {
  const webviewRef = useRef(null);
  const [location, setLocation] = useState(null);
  const [region, setRegion] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [categoriaId, setCategoriaId] = useState(null);
  const [pontos, setPontos] = useState([]);
  const [selectedPonto, setSelectedPonto] = useState(null);
  const [loadingScreen, setLoadingScreen] = useState(true);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [webviewReady, setWebviewReady] = useState(false);

  const categoriaNome = useMemo(() => {
    if (!categoriaId) return null;
    return categorias.find((c) => c.id === categoriaId)?.nome ?? null;
  }, [categoriaId, categorias]);

  useEffect(() => {
    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== "granted") {
          setLoadingScreen(false);
          return;
        }
        const loc = await Location.getCurrentPositionAsync({});
        setLocation(loc.coords);
        setRegion({
          latitude: loc.coords.latitude,
          longitude: loc.coords.longitude,
          latitudeDelta: 0.04,
          longitudeDelta: 0.04,
        });
      } finally {
        setLoadingScreen(false);
      }
    })();
  }, []);

  useEffect(() => {
    const fetchCategorias = async () => {
      try {
        const cached = await AsyncStorage.getItem("cache:categorias");
        if (cached) {
          const parsed = JSON.parse(cached);
          const isFresh = Date.now() - parsed.ts < 10 * 60 * 1000;
          if (isFresh) setCategorias(parsed.data);
        }
        const { data, error } = await dbApi.listCategorias();
        if (!error && data) {
          setCategorias(data);
          await AsyncStorage.setItem(
            "cache:categorias",
            JSON.stringify({ ts: Date.now(), data })
          );
        }
      } catch {
        // noop
      }
    };
    fetchCategorias();
  }, []);

  useEffect(() => {
    if (!location) return;

    (async () => {
      try {
        const cacheKey = `cache:pontos:${categoriaId ?? "all"}`;
        const cached = await AsyncStorage.getItem(cacheKey);
        if (cached) {
          const parsed = JSON.parse(cached);
          const isFresh = Date.now() - parsed.ts < 5 * 60 * 1000;
          if (isFresh) setPontos(parsed.data);
        }

        let pontosData;
        if (categoriaId) {
          const pontoCat = await dbApi.listPontoCategoriaByCategoria(categoriaId);
          const ids = (pontoCat.data || []).map((p) => p.ponto_id);
          if (ids.length === 0) {
            setPontos([]);
            return;
          }
          const allPontos = await dbApi.listPontos();
          pontosData = (allPontos.data || []).filter((p) => ids.includes(p.id));
        } else {
          const result = await dbApi.listPontos();
          pontosData = result.data;
        }

        const withDistance = (pontosData || []).map((p) => ({
          ...p,
          distance: getDistance(location.latitude, location.longitude, p.latitude, p.longitude),
        }));

        const pontosToShow = categoriaId
          ? withDistance.sort((a, b) => a.distance - b.distance)
          : withDistance.sort((a, b) => a.distance - b.distance).slice(0, 6);

        setPontos(pontosToShow);
        await AsyncStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data: pontosToShow }));
      } catch {
        // noop
      }
    })();
  }, [location, categoriaId]);

  const pushMapPayload = (skipCenter = false) => {
    const payload = {
      userLocation: location
        ? { latitude: location.latitude, longitude: location.longitude }
        : null,
      pontos,
      skipCenter,
    };
    const script = `window.receive(${JSON.stringify(JSON.stringify(payload))}); true;`;
    webviewRef.current?.injectJavaScript(script);
  };

  useEffect(() => {
    if (!webviewReady) return;
    pushMapPayload(false);
  }, [webviewReady, location, pontos]);

  const abrirDetalhe = (destino) => {
    if (!location) return;
    setSelectedPonto(destino);
    setShowDetailModal(true);
  };

  const toggleFavorite = (pontoId) => {
    setFavorites((prev) =>
      prev.includes(pontoId) ? prev.filter((id) => id !== pontoId) : [...prev, pontoId]
    );
  };

  const recenterMap = () => {
    if (!location) return;
    pushMapPayload(false);
  };

  if (loadingScreen || !region) {
    return (
      <LinearGradient {...gradients.appBg} style={styles.flex}>
        <SafeAreaView style={styles.center}>
          <ActivityIndicator size="large" color={colors.accent} />
          <Text style={styles.loadingText}>Carregando mapa…</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return (
    <View style={styles.container}>
      <WebView
        ref={webviewRef}
        style={styles.map}
        originWhitelist={["*"]}
        source={{ html: leafletHtml }}
        onMessage={(ev) => {
          try {
            const msg = JSON.parse(ev.nativeEvent.data);
            if (msg.type === "ready") {
              setWebviewReady(true);
            } else if (msg.type === "markerClick") {
              const p = pontos.find((pt) => pt.id === msg.id);
              if (p) abrirDetalhe(p);
            }
          } catch {}
        }}
      />

      {/* Overlay superior: hero + filtros */}
      <View style={styles.topOverlay} pointerEvents="box-none">
        <SafeAreaView edges={["top"]} pointerEvents="box-none">
          <View style={[styles.heroCard, shadows.elevated]}>
            <View style={styles.heroTitleRow}>
              <View style={styles.heroIconWrap}>
                <Ionicons name="map" size={20} color={colors.accent} />
              </View>
              <View style={styles.heroTextWrap}>
                <Text style={styles.heroTitle}>Mapa de Maricá</Text>
                <Text style={styles.heroSubtitle}>
                  {pontos.length}{" "}
                  {pontos.length === 1 ? "ponto próximo" : "pontos próximos"}
                  {categoriaNome ? ` · ${categoriaNome}` : ""}
                </Text>
              </View>
            </View>

            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.chipsRow}
            >
              <PressableScale
                onPress={() => setCategoriaId(null)}
                accessibilityLabel="Mostrar todos os pontos no mapa"
                accessibilityState={{ selected: categoriaId === null }}
                contentStyle={[styles.chip, categoriaId === null && styles.chipActive]}
              >
                <Ionicons
                  name="apps-outline"
                  size={16}
                  color={categoriaId === null ? colors.text : colors.accent}
                />
                <Text style={[styles.chipText, categoriaId === null && styles.chipTextActive]}>
                  Todos
                </Text>
              </PressableScale>
              {categorias.map((cat) => {
                const iconName = getIconForCategory(cat.nome);
                const ativo = categoriaId === cat.id;
                return (
                  <PressableScale
                    key={cat.id}
                    onPress={() => setCategoriaId((prev) => (prev === cat.id ? null : cat.id))}
                    accessibilityLabel={`Filtrar por ${cat.nome}`}
                    accessibilityState={{ selected: ativo }}
                    contentStyle={[styles.chip, ativo && styles.chipActive]}
                  >
                    <Ionicons
                      name={iconName}
                      size={16}
                      color={ativo ? colors.text : colors.accent}
                    />
                    <Text style={[styles.chipText, ativo && styles.chipTextActive]}>
                      {cat.nome}
                    </Text>
                  </PressableScale>
                );
              })}
            </ScrollView>
          </View>
        </SafeAreaView>
      </View>

      {/* Botão recentralizar */}
      <PressableScale
        onPress={recenterMap}
        accessibilityLabel="Centralizar no meu local"
        contentStyle={[styles.fab, shadows.card]}
      >
        <Ionicons name="locate" size={22} color={colors.accent} />
      </PressableScale>

      {/* Painel inferior: pontos próximos */}
      <View style={styles.bottomOverlay} pointerEvents="box-none">
        <View style={[styles.bottomSheet, shadows.elevated]}>
          <View style={styles.sheetHeader}>
            <Text style={styles.sheetTitle}>Próximos de você</Text>
            <Text style={styles.sheetSubtitle}>
              {categoriaId ? "Filtrado por categoria" : "Toque para ver detalhes"}
            </Text>
          </View>

          {pontos.length === 0 ? (
            <View style={styles.emptyBlock}>
              <Ionicons name="location-outline" size={28} color={colors.accent} />
              <Text style={styles.emptyText}>Nenhum ponto encontrado nesta área.</Text>
            </View>
          ) : (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.pointsRow}
            >
              {pontos.map((ponto) => (
                <PressableScale
                  key={ponto.id}
                  onPress={() => abrirDetalhe(ponto)}
                  accessibilityLabel={`Ponto ${ponto.nome}`}
                  contentStyle={styles.pointCard}
                >
                  {ponto.url_img ? (
                    <Image
                      source={{ uri: ponto.url_img }}
                      style={styles.pointThumb}
                      resizeMode="cover"
                    />
                  ) : (
                    <View style={styles.pointThumbPlaceholder}>
                      <Ionicons name="location" size={22} color={colors.accent} />
                    </View>
                  )}
                  <View style={styles.pointBody}>
                    <Text style={styles.pointName} numberOfLines={2}>
                      {ponto.nome}
                    </Text>
                    <View style={styles.distanceBadge}>
                      <Ionicons name="navigate-outline" size={11} color={colors.accent} />
                      <Text style={styles.distanceText}>{formatDistance(ponto.distance)}</Text>
                    </View>
                  </View>
                </PressableScale>
              ))}
            </ScrollView>
          )}
        </View>
      </View>

      <Modal visible={showDetailModal} animationType="slide" transparent={false}>
        {selectedPonto ? (
          <PointDetail
            point={selectedPonto}
            onClose={() => {
              setShowDetailModal(false);
              setSelectedPonto(null);
            }}
            distance={selectedPonto.distance || 3.4}
            onFavorite={() => toggleFavorite(selectedPonto.id)}
            isFavorite={favorites.includes(selectedPonto.id)}
          />
        ) : null}
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  container: {
    flex: 1,
    backgroundColor: colors.bgDark,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  loadingText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  map: {
    flex: 1,
  },
  topOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
  },
  heroCard: {
    marginHorizontal: layout.contentPadding,
    marginTop: spacing.xs,
    backgroundColor: "rgba(15, 20, 44, 0.94)",
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
    overflow: "hidden",
  },
  heroTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  heroIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(247, 160, 0, 0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  heroTextWrap: {
    flex: 1,
  },
  heroTitle: {
    ...typography.subtitle,
    fontSize: 17,
  },
  heroSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  chipsRow: {
    paddingHorizontal: spacing.md,
    gap: spacing.xs,
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xxs,
    paddingHorizontal: spacing.sm + 2,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    marginRight: spacing.xs,
  },
  chipActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipText: {
    ...typography.caption,
    color: colors.textMuted,
    fontWeight: "600",
    fontSize: 12,
  },
  chipTextActive: {
    color: colors.text,
  },
  fab: {
    position: "absolute",
    right: layout.contentPadding,
    bottom: 200,
    zIndex: 11,
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.cardBg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    alignItems: "center",
    justifyContent: "center",
  },
  bottomOverlay: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    paddingBottom: layout.minTouchTarget + spacing.lg,
  },
  bottomSheet: {
    marginHorizontal: layout.contentPadding,
    backgroundColor: "rgba(15, 20, 44, 0.96)",
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  sheetHeader: {
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  sheetTitle: {
    ...typography.subtitle,
    fontSize: 15,
  },
  sheetSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  pointsRow: {
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
    paddingBottom: spacing.xxs,
  },
  pointCard: {
    width: 148,
    backgroundColor: colors.cardBg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
    overflow: "hidden",
  },
  pointThumb: {
    width: "100%",
    height: 72,
  },
  pointThumbPlaceholder: {
    width: "100%",
    height: 72,
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  pointBody: {
    padding: spacing.sm,
    gap: spacing.xxs,
  },
  pointName: {
    ...typography.subtitle,
    fontSize: 13,
    lineHeight: 18,
  },
  distanceBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    alignSelf: "flex-start",
    backgroundColor: colors.badgeBg,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: radius.pill,
  },
  distanceText: {
    ...typography.caption,
    color: colors.accent,
    fontSize: 10,
    fontWeight: "600",
  },
  emptyBlock: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    gap: spacing.xs,
  },
  emptyText: {
    ...typography.body,
    fontSize: 13,
    color: colors.textSecondary,
    textAlign: "center",
  },
});
