#!/usr/bin/env bash
# Sobe backend Docker e mostra como iniciar o Expo (modo LAN).
set -e
cd "$(dirname "$0")/.."

echo "=== Kapitour Dev ==="
echo ""

echo "[1/2] Subindo backend Docker..."
docker compose up -d redis auth content engagement commerce kapipass gateway
sleep 3

IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
OK=false
for PORTA in 8000 8080; do
  if curl -sf "http://${IP}:${PORTA}/api/health" >/dev/null 2>&1; then
    echo "API OK em http://${IP}:${PORTA}/api"
    OK=true
    break
  fi
done

if [ "$OK" = false ]; then
  echo "API nao respondeu. Verifique: docker compose ps"
fi

echo ""
echo "[2/2] Em OUTRO terminal, inicie o app:"
echo "  npm install"
echo "  npm start"
echo ""
echo "Celular fisico (Expo Go): mesma Wi-Fi, modo LAN (nao Tunnel)."
echo "O app usa a porta do Metro (ex.: 8081) — nao precisa configurar IP no .env."
echo ""
echo "Login teste: user@kapitour.com / user123"
