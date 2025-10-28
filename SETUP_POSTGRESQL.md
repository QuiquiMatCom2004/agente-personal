# 🐘 Setup PostgreSQL + Sincronización

## ✅ Progreso Actual

- [x] Módulo PostgreSQL implementado (`src/integrations/postgres_db.py`)
- [x] Listener local creado (`scripts/local_listener.py`)
- [x] Configuración actualizada
- [ ] **→ Esperando connection string de Supabase**
- [ ] Commit y push
- [ ] Deploy en Railway
- [ ] Configurar listener local
- [ ] Probar sincronización

---

## 📋 Paso 1: Crear Base de Datos en Supabase

### Instrucciones:

1. Ve a https://supabase.com
2. Click "Start your project"
3. Login con GitHub
4. Click "New Project"
5. Configurar:
   - **Name:** `agente-personal`
   - **Database Password:** (Crea una fuerte y guárdala)
   - **Region:** US East u otra cercana
   - **Plan:** Free
6. Click "Create new project" (espera 2-3 min)
7. Una vez creado:
   - Settings ⚙️ → Database
   - **Connection string → URI**
   - Copia la cadena completa (reemplaza `[YOUR-PASSWORD]` con tu password)

### La connection string se ve así:

```
postgresql://postgres.abcdefgh:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Reemplaza `[YOUR-PASSWORD]` con tu password real**

---

## 📋 Paso 2: Configurar Variables de Entorno

### En tu PC Local (.env):

```env
# Cambiar esta línea:
DATABASE_URL=postgresql://postgres.xxxxx:TU_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Mantener estas:
OPENROUTER_API_KEY=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
TELEGRAM_BOT_TOKEN=8041845392:AAFXwwThwqlLhEA6JmyI7gwvs3NSJmyVDDs
TELEGRAM_ALLOWED_USER_IDS=1243096887

# Desktop habilitado (para listener local)
ENABLE_DESKTOP_NOTIFICATIONS=true
NOTIFICATION_SOUND=true

# Telegram desactivado (ya corre en Railway)
ENABLE_TELEGRAM=false
ENABLE_CLI=true
```

### En Railway (Variables):

```env
DATABASE_URL=postgresql://postgres.xxxxx:TU_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
OPENROUTER_API_KEY=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
TELEGRAM_BOT_TOKEN=8041845392:AAFXwwThwqlLhEA6JmyI7gwvs3NSJmyVDDs
TELEGRAM_ALLOWED_USER_IDS=1243096887

# Desktop DESACTIVADO (Railway no tiene desktop)
ENABLE_DESKTOP_NOTIFICATIONS=false
NOTIFICATION_SOUND=false

# Telegram ACTIVADO (bot 24/7)
ENABLE_TELEGRAM=true
ENABLE_CLI=false

# Agent settings
AGENT_MODEL=deepseek/deepseek-chat
AGENT_TEMPERATURE=0.7
LOG_LEVEL=INFO
```

---

## 📋 Paso 3: Ejecutar Listener Local

### En tu PC:

```bash
cd /home/kiki/Proyectos/Agente

# Asegúrate de que DATABASE_URL está configurado en .env
uv run python scripts/local_listener.py
```

**Output esperado:**

```
============================================================
🎧 LOCAL LISTENER - Agente Personal
============================================================

Este script monitorea PostgreSQL y ejecuta:
  • ⏰ Alarmas con sonido
  • 🔔 Notificaciones desktop
  • 📅 Sincronización con Calcurse

Presiona Ctrl+C para detener
============================================================

2025-10-28 01:00:00 - INFO - 🎧 Iniciando Local Listener...
2025-10-28 01:00:01 - INFO - ✅ Conectado a PostgreSQL
2025-10-28 01:00:01 - INFO - 📋 Monitoreando recordatorios cada 30 seg...
```

### Para ejecutar en background:

```bash
# Opción 1: Con nohup
nohup uv run python scripts/local_listener.py > listener.log 2>&1 &

# Opción 2: Con systemd (más profesional)
# Ver sección "Systemd Service" abajo
```

---

## 📋 Paso 4: Desplegar en Railway

1. Ve a https://railway.app
2. Login con GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecciona `agente-personal`
5. **Configurar Variables** (pestaña "Variables"):
   - Copia las variables de arriba ("En Railway")
6. Deploy automático se ejecutará
7. Espera 2-3 minutos
8. Verifica logs: debería decir `✅ Telegram bot activo`

---

## 🔄 Cómo Funciona la Sincronización

### Ejemplo: Crear Alarma desde Telegram

```
1. Usuario (desde Telegram): "Alarma para las 9am mañana"
   ↓
2. Bot (Railway):
   - Procesa mensaje
   - Guarda en PostgreSQL:
     INSERT INTO reminders (title, trigger_time, type...)
   - Responde: "✅ Alarma programada"
   ↓
3. Listener (Tu PC):
   - Cada 30 seg: SELECT * FROM reminders WHERE executed=FALSE
   - Encuentra alarma para las 9am
   - Espera hasta las 9am
   ↓
4. A las 9am (Tu PC):
   - 🔊 Reproduce sonido de alarma
   - 🔔 Muestra notificación desktop
   - UPDATE reminders SET executed=TRUE
   ↓
5. ✅ Sincronizado: Railway sabe que se ejecutó
```

### Ejemplo: Crear Tarea desde CLI Local

```
1. Usuario (CLI local): "Crea tarea: Comprar leche"
   ↓
2. CLI local:
   - INSERT INTO tasks (title, ...)
   ↓
3. Bot (Railway):
   - Puede leer la tarea desde Telegram
   - "Qué tareas tengo?" → muestra "Comprar leche"
   ↓
✅ Sincronizado en ambas direcciones
```

---

## 🔧 Systemd Service (Linux - Opcional)

Para que el listener arranque automáticamente al encender tu PC:

```bash
# Crear service file
sudo nano /etc/systemd/system/agente-listener.service
```

Contenido:

```ini
[Unit]
Description=Agente Personal - Local Listener
After=network.target

[Service]
Type=simple
User=kiki
WorkingDirectory=/home/kiki/Proyectos/Agente
ExecStart=/home/kiki/.local/bin/uv run python scripts/local_listener.py
Restart=always
RestartSec=10
Environment="PATH=/home/kiki/.local/bin:/usr/bin"

[Install]
WantedBy=multi-user.target
```

Habilitar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agente-listener
sudo systemctl start agente-listener

# Ver logs
sudo journalctl -u agente-listener -f
```

---

## 🧪 Testing de Sincronización

### Prueba 1: Crear Alarma desde Telegram

```bash
# En Telegram, envía:
"Ponme una alarma en 2 minutos para probar"

# Espera 2 minutos
# Tu PC debería:
# - Reproducir sonido ✅
# - Mostrar notificación ✅
```

### Prueba 2: Crear Tarea desde CLI Local

```bash
# En tu PC:
uv run python main.py

# En el CLI, escribe:
"Crea una tarea de prueba"

# Luego en Telegram:
"/tareas"

# Debería mostrar la tarea creada desde tu PC ✅
```

### Prueba 3: Completar Tarea desde Telegram

```bash
# En Telegram:
"Completa la tarea de prueba"

# En tu PC (CLI):
"Muestra mis tareas"

# La tarea debería aparecer como completada ✅
```

---

## ⚠️ Troubleshooting

### Listener no conecta a PostgreSQL

**Error:** `Error conectando a PostgreSQL`

**Solución:**
1. Verifica que `DATABASE_URL` esté en `.env`
2. Verifica que reemplazaste `[YOUR-PASSWORD]`
3. Prueba conexión manual:
   ```bash
   uv run python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('tu_connection_string'))"
   ```

### Railway no encuentra DATABASE_URL

**Solución:**
1. Ve a Railway → Tu proyecto → Variables
2. Verifica que `DATABASE_URL` esté configurado
3. Redeploy: Settings → Redeploy

### Alarmas no suenan en PC

**Solución:**
1. Verifica que el listener esté corriendo
2. Verifica logs: `uv run python scripts/local_listener.py`
3. Verifica que `ENABLE_DESKTOP_NOTIFICATIONS=true` en .env local

---

## 📊 Estado Actual

- ✅ Código listo para PostgreSQL
- ✅ Listener implementado
- ⏳ Esperando connection string de Supabase
- ⏳ Deploy pendiente

---

## 🎯 Siguiente Paso

**Dame la connection string de Supabase** cuando la tengas y continuamos con:
1. Commit de cambios
2. Push a GitHub
3. Deploy en Railway
4. Test de sincronización

¿Ya tienes la connection string?
