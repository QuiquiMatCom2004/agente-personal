# 🚀 Guía de Despliegue del Agente Personal

Esta guía te ayudará a desplegar tu bot de Telegram en la nube **GRATIS** para que funcione 24/7.

---

## 🌟 Opción 1: Railway.app (RECOMENDADA - Más Fácil)

### Paso 1: Preparar el Repositorio

1. **Crear repositorio en GitHub** (si no lo tienes):
   ```bash
   cd /home/kiki/Proyectos/Agente
   git init
   git add .
   git commit -m "Initial commit - Agente Personal"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/agente-personal.git
   git push -u origin main
   ```

2. **Actualizar .gitignore** para NO subir datos sensibles:
   ```bash
   # Ya está incluido en el proyecto
   cat .gitignore
   ```

### Paso 2: Crear Cuenta en Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Conecta tu cuenta de GitHub
5. Selecciona el repositorio `agente-personal`

### Paso 3: Configurar Variables de Entorno

En Railway, ve a la pestaña **"Variables"** y agrega:

```bash
# REQUERIDAS
OPENROUTER_API_KEY=sk-or-v1-tu_api_key_aqui
TELEGRAM_BOT_TOKEN=8041845392:AAFXwwThwqlLhEA6JmyI7gwvs3NSJmyVDDs
TELEGRAM_ALLOWED_USER_IDS=1243096887

# Interfaces
ENABLE_CLI=false
ENABLE_TELEGRAM=true
ENABLE_WEB=false

# Agent settings
AGENT_MODEL=deepseek/deepseek-chat
AGENT_TEMPERATURE=0.7
AGENT_MAX_CONTEXT_MESSAGES=20

# Logging
LOG_LEVEL=INFO

# Notificaciones (desactivar en producción)
ENABLE_DESKTOP_NOTIFICATIONS=false
NOTIFICATION_SOUND=false
```

### Paso 4: Deploy

1. Railway detectará automáticamente Python
2. Click en **"Deploy"**
3. Espera 2-3 minutos
4. ✅ ¡Listo! Tu bot está 24/7

### Paso 5: Verificar

1. Ve a la pestaña **"Logs"** en Railway
2. Deberías ver: `✅ Telegram bot activo y esperando mensajes`
3. Prueba enviando un mensaje a tu bot en Telegram

---

## 🎯 Opción 2: Render.com (También Fácil)

### Paso 1: Crear Cuenta

1. Ve a [render.com](https://render.com)
2. Regístrate con GitHub

### Paso 2: Crear Web Service

1. Click en **"New +"** → **"Web Service"**
2. Conecta tu repositorio GitHub
3. Configura:
   - **Name:** agente-personal
   - **Environment:** Python 3
   - **Build Command:** `pip install uv && uv sync`
   - **Start Command:** `uv run python main.py`
   - **Plan:** Free

### Paso 3: Variables de Entorno

Agrega las mismas variables que en Railway (ver arriba)

### Paso 4: Deploy

1. Click en **"Create Web Service"**
2. Espera 3-5 minutos
3. ✅ Bot activo 24/7

**Nota:** En Render gratis, el bot se "duerme" después de 15 minutos de inactividad, pero se despierta automáticamente cuando llega un mensaje.

---

## 💎 Opción 3: Oracle Cloud (VPS Gratis PARA SIEMPRE)

### Ventajas
- ✅ Gratis permanentemente (no es trial)
- ✅ 2 VMs ARM (24GB RAM total)
- ✅ Control total del servidor
- ✅ Puedes correr múltiples bots/apps

### Pasos

1. **Crear cuenta** en [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
   - Requiere tarjeta de crédito (pero NO te cobran)

2. **Crear una VM**:
   - Compute → Instances → Create Instance
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (ARM - GRATIS)
   - RAM: 6GB (puedes ajustar)

3. **Conectar por SSH**:
   ```bash
   ssh ubuntu@TU_IP_PUBLICA
   ```

4. **Instalar dependencias**:
   ```bash
   # Actualizar sistema
   sudo apt update && sudo apt upgrade -y

   # Instalar Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip -y

   # Instalar UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc

   # Instalar calcurse y dependencias
   sudo apt install calcurse libnotify-bin git -y
   ```

5. **Clonar tu proyecto**:
   ```bash
   git clone https://github.com/TU_USUARIO/agente-personal.git
   cd agente-personal
   ```

6. **Configurar .env**:
   ```bash
   nano .env
   # Pega tu configuración y guarda (Ctrl+X, Y, Enter)
   ```

7. **Instalar dependencias**:
   ```bash
   uv sync
   ```

8. **Crear servicio systemd** (para que arranque automáticamente):
   ```bash
   sudo nano /etc/systemd/system/agente-bot.service
   ```

   Pega esto:
   ```ini
   [Unit]
   Description=Agente Personal Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/agente-personal
   ExecStart=/home/ubuntu/.local/bin/uv run python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

9. **Iniciar servicio**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable agente-bot
   sudo systemctl start agente-bot
   sudo systemctl status agente-bot
   ```

10. **Ver logs**:
    ```bash
    sudo journalctl -u agente-bot -f
    ```

---

## 🐳 Opción 4: Fly.io (Usando Docker)

### Pasos

1. **Instalar Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Crear app**:
   ```bash
   fly launch
   # Selecciona región (iad - Washington DC es buena)
   # NO despliegues aún, solo crea la app
   ```

4. **Configurar secrets**:
   ```bash
   fly secrets set OPENROUTER_API_KEY="tu_key"
   fly secrets set TELEGRAM_BOT_TOKEN="tu_token"
   fly secrets set TELEGRAM_ALLOWED_USER_IDS="tu_id"
   fly secrets set ENABLE_TELEGRAM="true"
   fly secrets set ENABLE_CLI="false"
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Ver logs**:
   ```bash
   fly logs
   ```

---

## 📊 Comparación de Opciones

| Plataforma | Gratis | Fácil | 24/7 | Limitaciones |
|------------|--------|-------|------|--------------|
| **Railway** | ✅ (500h/mes) | ⭐⭐⭐⭐⭐ | ✅ | Suficiente para 1 bot |
| **Render** | ✅ | ⭐⭐⭐⭐ | ⚠️ Se duerme | Despierta automático |
| **Oracle Cloud** | ✅ PERMANENTE | ⭐⭐⭐ | ✅ | Requiere más setup |
| **Fly.io** | ✅ | ⭐⭐⭐ | ✅ | Límite de 3 apps |

---

## 🎯 Mi Recomendación

### Para empezar YA: **Railway.app**
- Más fácil y rápido (5 minutos)
- Gratis suficiente para un bot
- Deploy automático desde GitHub

### Para largo plazo: **Oracle Cloud**
- Gratis PARA SIEMPRE (no es trial)
- Control total
- Puedes agregar más proyectos después

---

## 🔧 Troubleshooting

### Bot no responde en producción

1. **Verificar logs**:
   - Railway: Pestaña "Logs"
   - Render: Pestaña "Logs"
   - Oracle: `sudo journalctl -u agente-bot -f`

2. **Verificar variables de entorno**:
   - Asegúrate de que `ENABLE_TELEGRAM=true`
   - Verifica que el token sea correcto

3. **Calcurse no disponible**:
   - En Railway/Render puede fallar la integración de calendario
   - El bot seguirá funcionando pero sin calendario
   - Solución: Usar Oracle Cloud con sistema completo

### Error de memoria

Si el bot se cae por memoria:
- Railway/Render: Plan gratis tiene 512MB RAM
- Oracle Cloud: Puedes asignar hasta 24GB gratis

---

## 📝 Próximos Pasos

1. **Elige tu plataforma** (recomiendo Railway para empezar)
2. **Sigue los pasos** de la sección correspondiente
3. **Configura las variables de entorno**
4. **Deploy** y prueba tu bot
5. **Monitorea los logs** para verificar que funciona

---

## 💡 Tips

- Mantén tu `.env` local con los mismos valores que en producción
- Usa GitHub Actions para auto-deploy cuando hagas cambios
- Monitorea los logs regularmente
- Configura alertas si el bot se cae (disponible en todas las plataformas)

---

**¿Necesitas ayuda con algún paso?** Pregúntame y te ayudo a configurarlo.
