// Screens/weatherApi.js
import axios from "axios";

const API_KEY = process.env.EXPO_PUBLIC_OPENWEATHER_API_KEY;
const BASE_URL = "https://api.openweathermap.org/data/2.5/";

export const getWeatherByCity = async (city) => {
  if (!API_KEY) {
    console.error("Chave da API não encontrada. Verifique seu arquivo .env");
    return null;
  }
  try {
    const response = await axios.get(`${BASE_URL}weather`, {
      params: {
        q: city,
        appid: API_KEY,
        units: "metric",
        lang: "pt_br",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar clima:", error.response?.data || error.message);
    return null;
  }
};