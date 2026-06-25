import { Alert } from "react-native";

export const handleError = (source, error, userMessage) => {
  try {
    const message = error?.message || String(error);
    console.error(`[${source}]`, message);
    if (userMessage) Alert.alert("Atenção", userMessage);
  } catch {}
};

export const handleNetworkError = (source, error) => {
  const msg = error?.message?.toLowerCase() || "";
  const isTimeout = msg.includes("timeout");
  const isNetwork = msg.includes("network") || msg.includes("fetch") || msg.includes("failed");
  const userMessage = isTimeout
    ? "Tempo de resposta excedido. Verifique sua conexão."
    : isNetwork
      ? "Falha de rede. Tente novamente em alguns instantes."
      : "Ocorreu um erro. Tente novamente mais tarde.";
  handleError(source, error, userMessage);
};