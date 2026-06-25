/**
 * Alertas de segurança de acordo com as condições climáticas.
 * Cada alerta tem: icon (Ionicons), message e level ("warning" | "danger" | "tip").
 */
export function getWeatherAlerts(info) {
  if (!info) return [];

  const { weatherCondition, tempCategory, isWindy } = info;
  const alerts = [];

  // ── Chuva ──────────────────────────────────────────────────────────
  if (weatherCondition === "chuvoso") {
    alerts.push({
      icon: "thunderstorm-outline",
      level: "danger",
      message: "Evite cachoeiras e trilhas — risco de deslizamentos e enxurradas.",
    });
    alerts.push({
      icon: "car-outline",
      level: "warning",
      message: "Dirija com cautela: pistas molhadas e possíveis alagamentos nas vias.",
    });
    alerts.push({
      icon: "umbrella-outline",
      level: "tip",
      message: "Leve guarda-chuva e roupa impermeável antes de sair.",
    });
  }

  // ── Vento forte ────────────────────────────────────────────────────
  if (isWindy) {
    alerts.push({
      icon: "boat-outline",
      level: "danger",
      message: "Evite atividades náuticas — vento forte pode ser perigoso no mar.",
    });
    alerts.push({
      icon: "walk-outline",
      level: "warning",
      message: "Cuidado em mirantes e trilhas abertas com vento forte.",
    });
  }

  // ── Calor ──────────────────────────────────────────────────────────
  if (tempCategory === "calor") {
    alerts.push({
      icon: "sunny-outline",
      level: "warning",
      message: "Evite o sol entre 10h e 16h — risco de insolação e queimaduras.",
    });
    alerts.push({
      icon: "water-outline",
      level: "tip",
      message: "Hidrate-se bastante e use protetor solar FPS 50+ ao sair.",
    });
  }

  // ── Frio ────────────────────────────────────────────────────────────
  if (tempCategory === "frio") {
    alerts.push({
      icon: "snow-outline",
      level: "tip",
      message: "Vista roupas em camadas — em trilhas longas o frio pode ser mais intenso.",
    });
  }

  // ── Sol + ameno (sem outros alertas) → dica positiva ───────────────
  if (alerts.length === 0) {
    alerts.push({
      icon: "checkmark-circle-outline",
      level: "tip",
      message: "Clima favorável para passeios ao ar livre. Aproveite Maricá!",
    });
  }

  return alerts;
}
