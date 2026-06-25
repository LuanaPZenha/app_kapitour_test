import { Image } from "react-native";

export function prefetchImages(urls = []) {
  urls.forEach((u) => {
    if (u) {
      try { Image.prefetch(u); } catch {}
    }
  });
}