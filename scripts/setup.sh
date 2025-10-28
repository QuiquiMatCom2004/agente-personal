#!/bin/bash
# Script de configuración inicial del Agente Personal

set -e

echo "========================================"
echo "   Configuración del Agente Personal   "
echo "========================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Crear .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "✓ Archivo .env creado"
    echo ""
    echo "IMPORTANTE: Edita .env y agrega tu ANTHROPIC_API_KEY"
    echo "  nano .env"
    echo ""
else
    echo "✓ Archivo .env ya existe"
fi

# Verificar que UV esté instalado
if ! command -v uv &> /dev/null; then
    echo "Error: UV no está instalado"
    echo "Instala UV con: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "✓ UV está instalado"

# Sincronizar dependencias
echo ""
echo "Sincronizando dependencias..."
uv sync
echo "✓ Dependencias instaladas"

# Crear directorios de datos si no existen
mkdir -p data/logs data/db data/cache
echo "✓ Directorios de datos creados"

# Verificar calcurse
if command -v calcurse &> /dev/null; then
    echo "✓ Calcurse está instalado"
else
    echo "⚠ Calcurse no está instalado (opcional)"
    echo "  Instala con: sudo pacman -S calcurse"
fi

# Verificar dunst
if command -v dunst &> /dev/null; then
    echo "✓ Dunst está instalado"
else
    echo "⚠ Dunst no está instalado (opcional)"
    echo "  Instala con: sudo pacman -S dunst"
fi

echo ""
echo "========================================"
echo "   Configuración completada!            "
echo "========================================"
echo ""
echo "Próximos pasos:"
echo "1. Edita .env y agrega tu ANTHROPIC_API_KEY"
echo "2. (Opcional) Personaliza config/agent_config.yaml"
echo "3. Ejecuta el agente:"
echo "   uv run python main.py"
echo ""
