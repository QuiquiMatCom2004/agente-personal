# Agente Personal Inteligente

Un asistente personal potenciado por IA (DeepSeek via OpenRouter) que te ayuda a mantenerte organizado, gestionar tu calendario, planificar aprendizaje y más.

## Características

- **🤖 Sistema de Orquestación Inteligente** - El agente decide automáticamente qué herramientas usar
- **📅 Gestión de tareas y calendario** - Crea, modifica y consulta eventos
- **📚 Planificación de aprendizaje** - Planes estructurados para aprender nuevas habilidades
- **🔔 Notificaciones inteligentes** - Recordatorios proactivos basados en contexto (próximamente)
- **🖥️ Múltiples interfaces** - CLI, Telegram Bot, y Web API (en desarrollo)
- **🔧 Extensible** - Sistema de herramientas (tools) fácil de expandir

## Requisitos

- Python 3.11+
- Arch Linux (u otro sistema Unix)
- UV package manager
- API key de OpenRouter (para usar DeepSeek o cualquier otro modelo)

## Instalación

### 1. Clonar el repositorio (o ya estás en él)

```bash
cd /home/kiki/Proyectos/Agente
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
nano .env  # O tu editor favorito
```

Edita el archivo `.env` y agrega tu API key de OpenRouter:

```env
OPENROUTER_API_KEY=tu_api_key_de_openrouter_aqui
AGENT_MODEL=deepseek/deepseek-chat  # O cualquier modelo compatible con OpenRouter
```

**Nota**: Obtén tu API key gratis en [OpenRouter](https://openrouter.ai/keys)

### 3. Las dependencias ya están instaladas con UV

Si necesitas reinstalar:

```bash
uv sync
```

## Uso

### Modo CLI (Interfaz de línea de comandos)

```bash
# Asegúrate de tener ENABLE_CLI=true en .env
uv run python main.py
```

### Modo Telegram Bot

1. **Obtén un token de bot:**
   - Habla con [@BotFather](https://t.me/botfather) en Telegram
   - Usa `/newbot` y sigue las instrucciones
   - Copia el token que te da

2. **Configura el bot en `.env`:**
```env
ENABLE_CLI=false
ENABLE_TELEGRAM=true
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_ALLOWED_USER_IDS=tu_user_id_aqui
```

3. **Obtén tu User ID:**
   - Habla con [@userinfobot](https://t.me/userinfobot)
   - Te dará tu ID numérico

4. **Inicia el bot:**
```bash
uv run python main.py
```

5. **Úsalo desde Telegram:**
   - Busca tu bot en Telegram
   - Envía `/start`
   - ¡Listo! Puedes usar todos los comandos y hablar naturalmente

### Comandos disponibles

Dentro del CLI:

- `/help` - Muestra ayuda
- `/agenda [días]` - Ver tu agenda
- `/clear` - Limpiar historial de conversación
- `/exit` - Salir

### Ejemplos de uso

```
Tú: Qué tengo programado para mañana?
Tú: Agenda una reunión con el equipo el lunes a las 3pm
Tú: Recuérdame revisar el email en 2 horas
Tú: Ayúdame a aprender Rust, tengo 8 horas por semana
Tú: Cancela mi reunión de las 4pm
```

## Estructura del proyecto

```
Agente/
├── src/
│   ├── core/              # Lógica principal del agente
│   │   └── agent.py       # Clase PersonalAgent + orquestador
│   ├── tools/             # Sistema de herramientas ✨ NUEVO
│   │   ├── base.py        # Clase base Tool y ToolRegistry
│   │   ├── calendar_tool.py # Herramientas de calendario
│   │   └── task_tool.py   # Herramientas de tareas
│   ├── interfaces/        # Interfaces de usuario
│   │   ├── cli.py         # Interfaz CLI (funcional)
│   │   ├── telegram.py    # Bot de Telegram (TODO)
│   │   └── web.py         # API Web (TODO)
│   ├── integrations/      # Integraciones externas (TODO)
│   │   ├── calendar.py    # Calcurse
│   │   ├── notifications.py # Sistema de notificaciones
│   │   └── knowledge_base.py # Logseq/AppFlowy
│   └── utils/             # Utilidades
│       └── config.py      # Gestión de configuración
├── config/
│   └── agent_config.yaml  # Configuración del comportamiento
├── docs/                  # Documentación ✨ NUEVO
│   └── COMO_AGREGAR_HERRAMIENTAS.md # Guía para crear tools
├── data/
│   ├── logs/              # Logs del sistema
│   ├── db/                # Base de datos local
│   └── cache/             # Caché temporal
├── main.py                # Punto de entrada
├── pyproject.toml         # Dependencias
└── README.md              # Este archivo
```

## ✨ Cómo Funciona el Orquestador

El agente usa **Function Calling** para decidir automáticamente qué herramientas usar:

1. **Usuario envía mensaje**: "Agenda reunión mañana a las 3pm"
2. **Agente analiza** y decide que necesita usar `calendar_create_event`
3. **Orquestador ejecuta** la herramienta con los parámetros correctos
4. **Agente recibe resultado** y responde al usuario

### Herramientas Disponibles

Actualmente el agente tiene acceso a:

**Calendario (Calcurse)**
- `calendar_create_event` - Crear eventos en calcurse
- `calendar_get_agenda` - Ver agenda de próximos días desde calcurse

**Tareas (SQLite)**
- `task_create` - Crear nuevas tareas en la base de datos
- `task_list` - Listar tareas pendientes (con filtros)
- `task_complete` - Marcar tareas como completadas

**Notificaciones (Dunst)**
- `notification_send` - Enviar notificaciones de escritorio

**Recordatorios (APScheduler)**
- `reminder_create` - Programar recordatorios para el futuro
- `reminder_list` - Ver recordatorios programados
- `reminder_cancel` - Cancelar un recordatorio

**Alarmas (Sistema de Audio)**
- `alarm_create` - Crear alarmas con sonido persistente

### Agregar Nuevas Herramientas

Es muy fácil extender el agente con nuevas capacidades. Ver la guía completa en:

📖 **[docs/COMO_AGREGAR_HERRAMIENTAS.md](docs/COMO_AGREGAR_HERRAMIENTAS.md)**

Ejemplo rápido:

```python
from src.tools.base import Tool, ToolParameter

class MiNuevaHerramienta(Tool):
    @property
    def name(self) -> str:
        return "mi_herramienta"

    @property
    def description(self) -> str:
        return "Descripción de qué hace esta herramienta"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Tu lógica aquí
        return {"success": True, "message": "Hecho!"}
```

## Configuración

### Variables de entorno (.env)

Ver `.env.example` para todas las opciones disponibles. Las principales:

- `OPENROUTER_API_KEY` - Tu API key de OpenRouter (requerida)
- `AGENT_MODEL` - Modelo a usar (default: `deepseek/deepseek-chat`)
- `AGENT_TEMPERATURE` - Creatividad del modelo (0.0-1.0, default: 0.7)
- `LOG_LEVEL` - Nivel de logging (INFO, DEBUG, etc.)

### Configuración del agente (config/agent_config.yaml)

Personaliza el comportamiento del agente:

- Horarios de trabajo
- Duración de sesiones de aprendizaje
- Intervalos de notificaciones
- Integraciones habilitadas

## ✅ Integraciones Completadas

- [x] **Integración con Calcurse** - Gestión completa de calendario y tareas
- [x] **Sistema de notificaciones desktop** - Notificaciones con dunst/notify-send
- [x] **Base de datos SQLite** - Persistencia de tareas con aiosqlite
- [x] **Sistema de herramientas** - Orquestación automática con function calling
- [x] **Recordatorios programados** - Sistema completo con APScheduler
- [x] **Sistema de alarmas** - Alarmas con sonido persistente (NEW!)
- [x] **Bot de Telegram** - Interface móvil completa y funcional (NEW!)

## 🚀 Roadmap de Integraciones

Para ver el plan completo de desarrollo con todas las integraciones planificadas, consulta:
📖 **[docs/ROADMAP.md](docs/ROADMAP.md)**

### Próximas Integraciones Prioritarias

#### Fase 2: Gestión de Comunicaciones (PLANIFICADO)
1. **📧 Gmail** - Sistema inteligente de emails
   - Clasificación automática por prioridad (Urgente/Alto/Medio/Bajo)
   - Respuestas automatizadas **SOLO** para contextos de negocio
   - Creación automática de tareas desde emails importantes
   - Resúmenes diarios de emails pendientes
   - Detección de deadlines y seguimientos

2. **🐙 GitHub** - Gestión de desarrollo
   - Notificaciones priorizadas (PRs críticos, mentions, issues)
   - Sincronización bidireccional con tareas
   - Alertas de builds fallidos
   - Resumen de actividad semanal
   - Quick actions para PRs y issues

3. **💼 LinkedIn** - Networking profesional
   - Notificaciones de mensajes importantes
   - Alertas de oportunidades laborales relevantes
   - Respuestas automatizadas para networking
   - Gestión de conexiones

4. **📱 WhatsApp** - Comunicación de negocio
   - Clasificación inteligente: Negocio vs Personal
   - Auto-respuestas **SOLO** para contactos de negocio
   - **NUNCA** responder a familia/amigos automáticamente
   - Plantillas configurables por tipo de contacto
   - Auditoría completa de mensajes automáticos

#### Fase 3: Gestión Financiera Personal (NUEVO!)
- [ ] 💰 **Tracking de Gastos e Ingresos**
  - Registro manual y automático
  - Categorización inteligente con IA
  - Importación desde bancos (CSV/API)

- [ ] 📊 **Presupuestos y Metas**
  - Presupuestos por categoría
  - Metas de ahorro
  - Alertas de gastos inusuales

- [ ] 📈 **Análisis e Insights**
  - Resúmenes mensuales
  - Comparaciones mes a mes
  - Proyecciones y recomendaciones
  - Tracking de inversiones

#### Fase 4: Business Intelligence
- [ ] Resúmenes automáticos diarios/semanales
- [ ] Dashboard web con visualizaciones
- [ ] Centro de notificaciones unificado
- [ ] Análisis de productividad
- [ ] Reportes financieros automáticos

#### Otras Integraciones Futuras
- [ ] API Web con FastAPI + WebSockets
- [ ] Slack - Comunicación de equipos
- [ ] Discord - Comunidades y proyectos
- [ ] Notion/Obsidian - Knowledge base
- [ ] Trello/Jira - Project management
- [ ] Integración con Logseq/AppFlowy
- [ ] Detección inteligente de conflictos de calendario
- [ ] Sistema de planificación de aprendizaje con spaced repetition
- [ ] Launcher de aplicaciones basado en contexto
- [ ] Sincronización multi-dispositivo con Redis
- [ ] Open Banking APIs (BBVA, Santander)
- [ ] Stripe/PayPal para freelancers

## Desarrollo

### Ejecutar tests de integración

```bash
uv run python scripts/test_integrations.py
```

Este script prueba:
- Creación de eventos y tareas en Calcurse
- Obtención de agenda desde Calcurse
- Persistencia de tareas en SQLite
- Sistema de notificaciones con dunst

### Ejecutar tests unitarios (cuando estén disponibles)

```bash
uv run pytest
```

### Formatear código

```bash
uv run black src/
uv run ruff check src/
```

## Troubleshooting

### Error: "Field required" en OPENROUTER_API_KEY

Asegúrate de tener un archivo `.env` con tu API key:

```bash
cp .env.example .env
nano .env
# Agrega: OPENROUTER_API_KEY=tu_key_aqui
```

### Error: "X is not a valid model ID"

Verifica que el modelo en tu `.env` sea correcto:

```env
AGENT_MODEL=deepseek/deepseek-chat
```

Modelos populares en OpenRouter:
- `deepseek/deepseek-chat` - DeepSeek v3 (rápido y económico)
- `anthropic/claude-3.5-sonnet` - Claude Sonnet
- `openai/gpt-4` - GPT-4

### El agente no responde

Verifica que:
1. Tienes conexión a internet
2. Tu API key es válida
3. No has excedido los límites de la API

## Licencia

MIT
