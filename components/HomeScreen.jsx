import React, { useState } from "react";
import { View, StyleSheet } from "react-native";
import Categories from "./Categories";
import MapaHome from "./MapaHome";

export default function Home() {
  const [categoriaId, setCategoriaId] = useState(null);

  return (
    <View style={styles.container}>
      <Categories onSelectCategoria={setCategoriaId} />
      <MapaHome categoriaId={categoriaId} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
