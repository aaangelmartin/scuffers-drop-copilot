#!/bin/bash
# Scuffers Drop Co-Pilot — arranque completo
# Uso: ./start.sh                  # solo local (puerto 8080)
#      ./start.sh tunnel           # local + ngrok
#      ./start.sh full              # local + ngrok + lanza demo en Telegram

set -e
cd "$(dirname "$0")"

source venv/bin/activate 2>/dev/null || { echo "❌ venv no encontrado. Ejecuta: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"; exit 1; }

# Mata procesos previos
pkill -f "python3 webapp.py" 2>/dev/null || true
pkill -f "ngrok http" 2>/dev/null || true
sleep 1

echo "▶️  Lanzando Scuffers Drop Co-Pilot web app en :8080..."
PORT=8080 python3 webapp.py > /tmp/scuffers-webapp.log 2>&1 &
WEBAPP_PID=$!
sleep 3

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/healthz | grep -q 200; then
    echo "❌ La web app no responde. Revisa /tmp/scuffers-webapp.log"
    exit 1
fi

echo "✅ Web app: http://localhost:8080"

if [ "$1" = "tunnel" ] || [ "$1" = "full" ]; then
    if ! command -v ngrok >/dev/null; then
        echo "❌ ngrok no instalado. brew install ngrok"
        exit 1
    fi
    echo "🌐 Lanzando ngrok..."
    ngrok http 8080 --log=stdout > /tmp/scuffers-ngrok.log 2>&1 &
    sleep 4
    PUBLIC=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import json,sys;d=json.load(sys.stdin);print([t['public_url'] for t in d.get('tunnels',[]) if t.get('proto')=='https'][0])" 2>/dev/null || echo "")
    if [ -z "$PUBLIC" ]; then
        echo "⚠️  ngrok arrancó pero no pude leer la URL. Revisa http://localhost:4040"
    else
        echo "✅ Público: $PUBLIC"
        # Actualiza .env temporalmente
        if grep -q "^PUBLIC_URL=" .env 2>/dev/null; then
            sed -i.bak "s|^PUBLIC_URL=.*|PUBLIC_URL=$PUBLIC|" .env
        else
            echo "PUBLIC_URL=$PUBLIC" >> .env
        fi
        echo "✅ .env actualizado con PUBLIC_URL=$PUBLIC"
        echo "🔄 Reiniciando web app con nueva PUBLIC_URL..."
        kill $WEBAPP_PID 2>/dev/null || true
        sleep 1
        PORT=8080 python3 webapp.py > /tmp/scuffers-webapp.log 2>&1 &
        sleep 2
        echo ""
        echo "📲 Comparte con tu equipo:"
        echo "   Dashboard: $PUBLIC"
        echo "   Health:    $PUBLIC/healthz"
    fi
fi

if [ "$1" = "full" ]; then
    echo ""
    echo "🚀 Lanzando motor + demo a Telegram..."
    python3 demo_run.py
fi

echo ""
echo "📁 Logs: /tmp/scuffers-webapp.log /tmp/scuffers-ngrok.log"
echo "🛑 Para parar: pkill -f 'python3 webapp.py'  &&  pkill -f 'ngrok http'"
echo ""
echo "Web corriendo en background. Pulsa Ctrl+C aquí para terminar el script (la web sigue viva)."
wait $WEBAPP_PID
