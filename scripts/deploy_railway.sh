#!/bin/bash
# Script para preparar el proyecto para Railway.app

echo "🚀 Preparando proyecto para Railway.app..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar git
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositorio Git..."
    git init
    git branch -M main
else
    echo "✅ Repositorio Git ya existe"
fi

# Verificar archivos necesarios
echo ""
echo "📋 Verificando archivos de despliegue..."

files=("Procfile" "railway.json" "runtime.txt" "Dockerfile" ".dockerignore")
all_present=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - FALTA"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "❌ Faltan archivos. Ejecuta primero los comandos de Claude para crearlos."
    exit 1
fi

# Verificar .env.example
if [ ! -f ".env.example" ]; then
    echo "⚠️  Creando .env.example..."
    cp .env .env.example
    # Limpiar valores sensibles del example
    sed -i 's/sk-or-v1-[a-zA-Z0-9]*/your_openrouter_api_key_here/g' .env.example
    sed -i 's/[0-9]\+:AAF[a-zA-Z0-9_-]*/your_telegram_bot_token_here/g' .env.example
    sed -i 's/TELEGRAM_ALLOWED_USER_IDS=[0-9]\+/TELEGRAM_ALLOWED_USER_IDS=123456789/g' .env.example
fi

# Crear commit si hay cambios
echo ""
echo "📝 Verificando cambios en Git..."
git add .

if git diff --staged --quiet; then
    echo "  ℹ️  No hay cambios nuevos"
else
    echo "  📦 Creando commit..."
    git commit -m "Preparar para despliegue en Railway.app

- Agregar Procfile para Railway
- Agregar railway.json con configuración
- Agregar Dockerfile para despliegue
- Agregar runtime.txt con Python 3.11
- Configurar .dockerignore
"
fi

echo ""
echo "✅ Proyecto preparado para Railway!"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Crear repositorio en GitHub:"
echo "   gh repo create agente-personal --public --source=. --push"
echo "   # O manualmente:"
echo "   git remote add origin https://github.com/TU_USUARIO/agente-personal.git"
echo "   git push -u origin main"
echo ""
echo "2. Ve a https://railway.app"
echo "3. Click 'Start a New Project' → 'Deploy from GitHub repo'"
echo "4. Selecciona tu repositorio 'agente-personal'"
echo "5. Agrega las variables de entorno (ver DEPLOY.md)"
echo "6. ¡Deploy automático!"
echo ""
echo "📖 Para más detalles, lee: DEPLOY.md"
echo ""
