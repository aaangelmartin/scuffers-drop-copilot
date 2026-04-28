#!/usr/bin/env python3
"""Verifica que todo el setup del hackathon está listo. Run: python3 scripts/verify_setup.py"""
import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

def load_env():
    if not ENV_FILE.exists():
        return {}
    env = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env

def check(label, cond, hint=""):
    icon = "✅" if cond else "❌"
    print(f"{icon} {label}" + (f"  → {hint}" if not cond and hint else ""))
    return cond

def cmd_exists(cmd):
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0

def http_ok(url, timeout=2):
    try:
        import urllib.request
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False

def main():
    print("\n🔍 VERIFICACIÓN DE SETUP — HACKATHON SCUFFERS\n" + "="*50)
    env = load_env()
    results = []

    print("\n📁 Archivos del proyecto:")
    results.append(check(".env existe", ENV_FILE.exists(), "crea el archivo .env"))
    results.append(check("data/ existe", (ROOT/"data").exists()))
    results.append(check("scripts/ existe", (ROOT/"scripts").exists()))

    print("\n🛠️ Herramientas CLI:")
    results.append(check("docker instalado", cmd_exists("docker"), "instala Docker Desktop"))
    results.append(check("ngrok instalado", cmd_exists("ngrok"), "brew install ngrok"))
    results.append(check("python3", cmd_exists("python3")))
    results.append(check("node", cmd_exists("node"), "opcional, fallback de n8n"))

    print("\n🌐 Servicios locales:")
    results.append(check("n8n en localhost:5678", http_ok("http://localhost:5678"), "docker run -d -p 5678:5678 n8nio/n8n"))

    print("\n🔑 API Keys (mínimas):")
    results.append(check("ANTHROPIC_API_KEY", bool(env.get("ANTHROPIC_API_KEY")), "console.anthropic.com"))
    results.append(check("TELEGRAM_BOT_TOKEN", bool(env.get("TELEGRAM_BOT_TOKEN")), "@BotFather"))
    results.append(check("TELEGRAM_CHAT_ID", bool(env.get("TELEGRAM_CHAT_ID"))))

    print("\n🔑 API Keys (probables):")
    check("SHOPIFY_ACCESS_TOKEN", bool(env.get("SHOPIFY_ACCESS_TOKEN")), "opcional pero probable")
    check("AIRTABLE_TOKEN", bool(env.get("AIRTABLE_TOKEN")), "opcional pero probable")
    check("OPENAI_API_KEY", bool(env.get("OPENAI_API_KEY")), "opcional, backup")

    print("\n" + "="*50)
    if all(results):
        print("🚀 TODO LISTO. Estás preparado para el reto.")
        sys.exit(0)
    else:
        print("⚠️  Faltan elementos críticos. Revisa TUS_TAREAS.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
