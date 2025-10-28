# 🚀 Inicio Rápido - Agente Personal

Guía de 5 minutos para empezar a usar tu agente personal.

---

## ✅ Prerrequisitos

```bash
# Verificar que todo está instalado
which python3  # Python 3.11+
which uv       # UV package manager
which calcurse # Calcurse
which notify-send # Sistema de notificaciones
```

Si falta algo:
```bash
# Instalar calcurse (Arch Linux)
sudo pacman -S calcurse

# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🔧 Configuración (2 minutos)

### 1. Clonar/navegar al proyecto

```bash
cd /home/kiki/Proyectos/Agente
```

### 2. Crear archivo `.env`

```bash
cp .env.example .env
nano .env
```

**Mínimo requerido:**
```env
OPENROUTER_API_KEY=tu_key_aqui
AGENT_MODEL=deepseek/deepseek-chat
ENABLE_CLI=true
ENABLE_TELEGRAM=false
```

**Obtener API key gratis:**
1. Ve a https://openrouter.ai/keys
2. Crea una cuenta
3. Genera una API key
4. Pégala en `.env`

### 3. Sincronizar dependencias

```bash
uv sync
```

---

## 🎮 Uso - Modo CLI

### Iniciar el agente

```bash
uv run python main.py
```

### Ejemplos de uso

```
Tú: Hola
Agente: ¡Hola! ¿En qué puedo ayudarte?

Tú: Recuérdame llamar al dentista en 2 horas
Agente: ✅ Recordatorio 'Llamar al dentista' programado...

Tú: Crea una tarea urgente: revisar PR #123
Agente: ✅ Tarea 'Revisar PR #123' creada con prioridad urgent

Tú: Ponme una alarma para las 9am mañana
Agente: 🚨 Alarma programada para 28/10/2025 a las 09:00

Tú: Qué tengo programado para mañana?
Agente: 📅 Agenda para mañana...

Tú: /exit
Agente: ¡Hasta luego!
```

### Comandos especiales

- `/help` - Ver ayuda
- `/agenda [días]` - Ver tu agenda
- `/clear` - Limpiar historial
- `/exit` - Salir

---

## 📱 Uso - Modo Telegram

### 1. Crear bot en Telegram

1. Habla con [@BotFather](https://t.me/botfather)
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el **token**

### 2. Obtener tu User ID

1. Habla con [@userinfobot](https://t.me/userinfobot)
2. Te dará tu **ID numérico**

### 3. Configurar `.env`

```env
ENABLE_CLI=false
ENABLE_TELEGRAM=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_ALLOWED_USER_IDS=123456789
```

### 4. Iniciar el bot

```bash
uv run python main.py
```

### 5. Usar desde Telegram

1. Busca tu bot en Telegram
2. Envía `/start`
3. Usa comandos o habla naturalmente

**Comandos disponibles:**
- `/start` - Iniciar
- `/help` - Ayuda
- `/agenda` - Ver agenda
- `/tareas` - Ver tareas
- `/clear` - Limpiar historial
- `/stats` - Estadísticas

---

## 🎯 ¿Qué Puede Hacer?

### 📅 Calendario
```
"Agenda reunión con el equipo mañana a las 3pm"
"Qué tengo programado el lunes?"
"Crea un evento: Cumpleaños de mamá, 15 de noviembre"
```

### ✅ Tareas
```
"Crea una tarea: Comprar leche"
"Muéstrame mis tareas pendientes"
"Marca como completada la tarea de enviar el reporte"
"Crea una tarea urgente para revisar el código"
```

### ⏰ Recordatorios
```
"Recuérdame llamar a Juan en 30 minutos"
"Recuérdame la reunión 15 minutos antes"
"Muéstrame mis recordatorios"
"Cancela el recordatorio reminder_123"
```

### 🚨 Alarmas
```
"Ponme una alarma para despertar a las 7am"
"Alarma en 30 minutos"
"Crea una alarma con sonido de campana para las 9am mañana"
```

### 🔔 Notificaciones
```
"Envíame una notificación cuando termine"
"Notifícame si algo sale mal"
```

---

## 🧪 Verificar que Todo Funciona

### Test rápido (30 segundos)

```bash
uv run python scripts/test_integrations.py
```

**Resultado esperado:**
```
✓ Todas las pruebas completadas exitosamente
```

---

## 🐛 Solución de Problemas

### Error: "Field required" en OPENROUTER_API_KEY

**Causa:** No hay API key en `.env`

**Solución:**
```bash
# Crear .env con tu API key
echo "OPENROUTER_API_KEY=tu_key_aqui" > .env
echo "AGENT_MODEL=deepseek/deepseek-chat" >> .env
echo "ENABLE_CLI=true" >> .env
```

### Error: "calcurse not found"

**Causa:** Calcurse no está instalado

**Solución:**
```bash
sudo pacman -S calcurse  # Arch Linux
sudo apt install calcurse # Ubuntu/Debian
```

### Error: "notify-send not found"

**Causa:** Sistema de notificaciones no instalado

**Solución:**
```bash
sudo pacman -S libnotify dunst  # Arch Linux
sudo apt install libnotify-bin  # Ubuntu/Debian
```

### Bot de Telegram no responde

**Causa:** Token o user_id incorrecto

**Verificar:**
1. Token es correcto en `.env`
2. User ID es tu ID numérico (no username)
3. Bot está corriendo (`uv run python main.py`)

---

## 📖 Más Información

- **README.md** - Documentación completa
- **docs/ESTADO_ACTUAL.md** - Estado del proyecto
- **docs/ROADMAP.md** - Plan futuro
- **docs/INTEGRACIONES.md** - Detalles técnicos

---

## 🎉 ¡Listo!

Ya puedes usar tu Agente Personal. Algunas ideas para probar:

1. **Planifica tu día:**
   ```
   "Qué tengo hoy?"
   "Agenda tiempo para estudiar mañana de 4 a 6pm"
   ```

2. **Gestiona tareas:**
   ```
   "Crea una tarea para cada email importante"
   "Muéstrame solo las tareas urgentes"
   ```

3. **No olvides nada:**
   ```
   "Recuérdame tomar agua cada 2 horas"
   "Alarma para ir al gym a las 6pm"
   ```

4. **Desde cualquier lado con Telegram:**
   - Úsalo desde el móvil
   - Todas las funciones disponibles
   - Respuestas instantáneas

**¡Disfruta tu nuevo asistente inteligente!** 🚀
