# 🔄 Sincronización entre Deploy y PC Local

## El Problema

Cuando despliegas el bot en Railway:
- ❌ Railway NO tiene acceso a tu Calcurse local
- ❌ Railway NO puede mostrar notificaciones en tu desktop
- ❌ Railway NO puede reproducir alarmas con sonido en tu PC

Pero quieres:
- ✅ Bot disponible 24/7 desde Telegram
- ✅ Notificaciones y alarmas en tu PC cuando esté encendida
- ✅ Datos sincronizados entre ambos

---

## ✅ Solución 1: PostgreSQL Compartido (RECOMENDADA)

### Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   PostgreSQL                         │
│              (Base de datos central)                 │
│                                                      │
│  - Tareas                                           │
│  - Recordatorios                                    │
│  - Eventos del calendario                           │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
           │                           │
    ┌──────▼──────┐            ┌──────▼──────┐
    │   RAILWAY   │            │    TU PC    │
    │   (Nube)    │            │   (Local)   │
    ├─────────────┤            ├─────────────┤
    │ Bot 24/7    │            │ Listener    │
    │ Telegram    │            │ + Desktop   │
    │             │            │ + Alarmas   │
    └─────────────┘            └─────────────┘
```

### Cómo Funciona

1. **Railway** (nube):
   - Corre el bot de Telegram 24/7
   - Escribe tareas/eventos en PostgreSQL
   - NO ejecuta notificaciones ni alarmas

2. **Tu PC** (local):
   - Ejecuta un "listener" que monitorea PostgreSQL
   - Cuando hay alarma/notificación pendiente → la ejecuta localmente
   - Sincroniza con Calcurse local

### Configuración

#### Paso 1: Crear Base de Datos PostgreSQL Gratis

**Opción A: Supabase (Recomendada)**

1. Ve a https://supabase.com
2. Crea proyecto gratis
3. Copia la connection string:
   ```
   postgresql://user:pass@db.xxx.supabase.co:5432/postgres
   ```

**Opción B: Railway (Si ya estás ahí)**

1. En Railway → "New" → "Database" → "PostgreSQL"
2. Copia la connection string

#### Paso 2: Modificar el Código

Voy a crear los archivos necesarios...

---

## ✅ Solución 2: Webhook Local (Más Simple)

### Arquitectura

```
┌─────────────┐         Webhook (HTTP)        ┌─────────────┐
│   RAILWAY   │─────────────────────────────►│    TU PC    │
│   (Nube)    │  "Ejecuta alarma a las 9am"   │   (Local)   │
│             │                                │             │
│ Bot 24/7    │                                │ Recibe      │
│ Telegram    │                                │ + Notifica  │
└─────────────┘                                └─────────────┘
```

### Cómo Funciona

1. Railway envía webhooks a tu PC (usando ngrok/cloudflare tunnel)
2. Tu PC recibe el webhook y ejecuta la alarma/notificación
3. Más simple pero requiere que tu PC sea "alcanzable" por internet

### Configuración Rápida

```bash
# En tu PC - Instalar ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update && sudo apt install ngrok

# Crear túnel
ngrok http 8000
# Te dará una URL pública temporal: https://abc123.ngrok.io
```

---

## ✅ Solución 3: Solo PC + Túnel SSH Inverso (Más Control)

### Arquitectura

```
┌──────────────────────────────────────┐
│           TU PC (MAESTRO)            │
│                                      │
│  - Bot de Telegram (corre aquí)     │
│  - Base de datos local              │
│  - Notificaciones                   │
│  - Alarmas                          │
└────────────┬─────────────────────────┘
             │
             │ SSH Reverse Tunnel
             │ (Para estar "siempre conectado")
             │
      ┌──────▼──────┐
      │   RAILWAY   │
      │   (Proxy)   │
      │             │
      │  Solo hace  │
      │  forwarding │
      └─────────────┘
```

### Cómo Funciona

- El bot corre en **TU PC**
- Railway solo hace de "puente" para que esté accesible 24/7
- Requiere que tu PC esté encendida

**Ventaja:**
- ✅ Todo en un solo lugar
- ✅ Control total

**Desventaja:**
- ❌ Tu PC debe estar encendida 24/7

---

## 🎯 Mi Recomendación para TI

### Implementar **Solución 1** (PostgreSQL)

**Por qué:**
1. ✅ Bot disponible 24/7 en Railway
2. ✅ Datos centralizados
3. ✅ Tu PC ejecuta alarmas/notificaciones cuando esté encendida
4. ✅ Si tu PC está apagada, las alarmas se ejecutan cuando enciendas
5. ✅ Gratis con Supabase

### Plan de Implementación

Te voy a crear:

1. **Módulo de sincronización** (`src/integrations/postgres_sync.py`)
2. **Listener local** (`scripts/local_listener.py`)
3. **Configuración dual** (Railway usa PostgreSQL, local usa PostgreSQL + Desktop)

---

## 📦 Implementación Rápida

### Archivos que Voy a Crear

```
src/integrations/
  └── postgres_sync.py      # Reemplaza SQLite con PostgreSQL

scripts/
  └── local_listener.py     # Corre en tu PC, ejecuta alarmas/notificaciones

config/
  └── deployment.yaml       # Config para Railway vs Local
```

### Configuración

**Railway (.env en Railway):**
```env
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
ENABLE_DESKTOP_NOTIFICATIONS=false  # NO notificaciones en nube
ENABLE_ALARMS=false                 # NO alarmas en nube
ENABLE_TELEGRAM=true                # Bot de Telegram ✅
```

**Tu PC (.env local):**
```env
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
ENABLE_DESKTOP_NOTIFICATIONS=true   # Notificaciones ✅
ENABLE_ALARMS=true                  # Alarmas ✅
ENABLE_TELEGRAM=false               # NO bot (ya corre en Railway)
RUN_AS_LISTENER=true                # Modo listener
```

---

## ⚙️ Flujo Completo

### Usuario crea alarma desde Telegram:

```
1. Usuario → Telegram: "Alarma para las 9am"
   ↓
2. Bot (Railway) → PostgreSQL: INSERT alarma 9am
   ↓
3. Listener (Tu PC) → PostgreSQL: Polling cada 30 seg
   ↓
4. Listener detecta alarma pendiente
   ↓
5. A las 9am → Listener ejecuta:
   - Reproduce sonido en tu PC ✅
   - Muestra notificación desktop ✅
   - Marca alarma como ejecutada en PostgreSQL
```

### Usuario crea evento desde PC:

```
1. CLI local → PostgreSQL: INSERT evento
   ↓
2. Bot (Railway) también puede leerlo desde Telegram
   ✅ Sincronizado
```

---

## 🚀 Alternativa Ultra-Simple (Sin PostgreSQL)

Si no quieres PostgreSQL todavía, puedes:

### Opción Temporal: Solo Telegram en Railway

1. **Railway:** Solo bot de Telegram (sin alarmas ni notificaciones)
2. **Tu PC:** Corre CLI local con alarmas y notificaciones
3. **Sincronización manual:** Copias la base de datos SQLite ocasionalmente

**Comandos:**

```bash
# Descargar DB desde Railway
railway run cat data/db/tasks.db > tasks_railway.db

# Subir DB local a Railway
railway run cat tasks_local.db > data/db/tasks.db
```

---

## ❓ Siguiente Paso

¿Qué opción prefieres?

1. **PostgreSQL + Listener** - La más completa (te la implemento ya)
2. **Webhook local** - Más simple pero requiere ngrok
3. **Solo Railway sin alarmas** - Más fácil pero sin notificaciones desktop
4. **Solo PC con túnel** - Todo local pero PC debe estar encendida 24/7

Dime y te lo configuro ahora mismo.
