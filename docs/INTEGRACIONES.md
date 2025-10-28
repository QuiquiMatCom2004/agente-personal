# Integraciones Implementadas

Este documento describe las integraciones completadas y cómo funcionan.

## 📅 Calcurse - Gestión de Calendario

**Ubicación:** `src/integrations/calcurse.py`

### Funcionalidades

La integración con Calcurse permite al agente:

1. **Crear eventos** - Guardar eventos en el calendario usando formato iCal
2. **Crear tareas** - Agregar tareas TODO a calcurse
3. **Obtener agenda** - Consultar eventos y tareas de los próximos N días

### Implementación

Calcurse acepta datos en formato iCalendar (RFC 5545). Los eventos y tareas se crean generando archivos iCal temporales e importándolos con:

```bash
calcurse -i - -q
```

Para consultar la agenda:

```bash
calcurse -r7  # Próximos 7 días
```

### Ejemplo de uso desde Python

```python
from src.integrations.calcurse import Calcurse

c = Calcurse()

# Crear evento
result = c.saveEvent(
    title="Reunión de equipo",
    date="10/28/2025",  # MM/DD/YYYY
    start_time="10:00",
    end_time="11:00"
)

# Crear tarea
result = c.saveTask(
    title="Revisar PR",
    priority=5  # 0-9
)

# Obtener agenda
agenda = c.getAgenda(days=7)
print(agenda["events"])
print(agenda["tasks"])
```

### Formato de datos

**Eventos en iCal:**
```ical
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:unique-id
DTSTART:20251028T100000
DTEND:20251028T110000
SUMMARY:Título del evento
END:VEVENT
END:VCALENDAR
```

**Tareas en iCal:**
```ical
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VTODO
UID:unique-id
SUMMARY:Título de la tarea
PRIORITY:5
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR
```

---

## 💾 SQLite - Persistencia de Tareas

**Ubicación:** `src/integrations/database.py`

### Funcionalidades

Sistema de base de datos asíncrono para tareas con:

1. **Crear tareas** - Con título, descripción, prioridad, fecha límite, tags
2. **Listar tareas** - Con filtros (pending, completed, urgent, all)
3. **Completar tareas** - Marcar como completadas con timestamp
4. **Eliminar tareas** - Borrar tareas de la BD
5. **Obtener tarea específica** - Por ID

### Esquema de base de datos

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',
    due_date TEXT,
    tags TEXT,  -- Separado por comas
    completed BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    UNIQUE(id)
)
```

### Ejemplo de uso

```python
from src.integrations.database import TaskDatabase

db = TaskDatabase(db_path="data/tasks.db")
await db.initialize()

# Crear tarea
task = await db.create_task(
    task_id="task_001",
    user_id="default",
    title="Implementar feature X",
    description="Detalles de la tarea",
    priority="high",
    tags=["desarrollo", "backend"]
)

# Listar tareas pendientes
tasks = await db.list_tasks(
    user_id="default",
    filter_type="pending",
    limit=10
)

# Completar tarea
success = await db.complete_task(
    task_id="task_001",
    user_id="default"
)
```

### Multi-usuario

El sistema soporta múltiples usuarios mediante el campo `user_id`. Esto permite:
- Uso desde diferentes interfaces (CLI, Telegram, Web)
- Diferentes usuarios con sus propias tareas
- Sincronización futura con Redis

---

## 🔔 Dunst - Notificaciones de Escritorio

**Ubicación:** `src/integrations/notifications.py`

### Funcionalidades

Sistema de notificaciones usando `notify-send` (dunst/libnotify):

1. **Enviar notificación básica** - Con título, mensaje, prioridad
2. **Recordatorio de tarea** - Formato específico para tareas
3. **Recordatorio de evento** - Avisos de eventos próximos
4. **Notificación de éxito** - Confirmaciones de acciones
5. **Notificación de error** - Alertas de problemas
6. **Resumen diario** - Estadísticas del día

### Prioridades

- `LOW` - Notificaciones no urgentes
- `NORMAL` - Notificaciones regulares
- `CRITICAL` - Notificaciones urgentes (no expiran automáticamente)

### Ejemplo de uso

```python
from src.integrations.notifications import NotificationManager

nm = NotificationManager(
    app_name="Agente Personal",
    enable_sound=True
)

# Notificación básica
nm.send(
    title="Tarea completada",
    message="Has completado 'Revisar PR'",
    priority=NotificationPriority.NORMAL,
    timeout=5000  # 5 segundos
)

# Recordatorio de tarea
nm.send_task_reminder(
    task_title="Llamar al dentista",
    priority="high"
)

# Recordatorio de evento
nm.send_event_reminder(
    event_title="Reunión de equipo",
    start_time="10:00",
    minutes_before=15
)

# Notificación de éxito
nm.send_success("Evento creado exitosamente")

# Notificación de error
nm.send_error("No se pudo conectar al servidor")

# Resumen diario
nm.send_daily_summary(
    tasks_count=5,
    events_count=3
)
```

### Iconos disponibles

El sistema usa iconos estándar de freedesktop:
- `dialog-information` - Información general
- `dialog-warning` - Advertencias
- `dialog-error` - Errores
- `dialog-positive` - Éxito
- `appointment-soon` - Eventos próximos

---

## 🔧 Sistema de Herramientas (Tools)

**Ubicación:** `src/tools/`

### Arquitectura

El sistema de herramientas permite al agente ejecutar acciones mediante function calling:

```
Usuario → Agente → ToolRegistry → Tool.execute() → Integración → Resultado
```

### Herramientas implementadas

#### Calendario
- **CalendarTool** (`calendar_create_event`) - `src/tools/calendar_tool.py`
- **CalendarGetAgendaTool** (`calendar_get_agenda`) - `src/tools/calendar_tool.py`

#### Tareas
- **TaskCreateTool** (`task_create`) - `src/tools/task_tool.py`
- **TaskListTool** (`task_list`) - `src/tools/task_tool.py`
- **TaskCompleteTool** (`task_complete`) - `src/tools/task_tool.py`

#### Notificaciones
- **NotificationSendTool** (`notification_send`) - `src/tools/notification_tool.py`

### Registro de herramientas

En `src/core/agent.py`:

```python
def _register_tools(self):
    """Registra todas las herramientas disponibles."""
    # Calendario
    self.tool_registry.register(CalendarTool())
    self.tool_registry.register(CalendarGetAgendaTool())

    # Tareas
    self.tool_registry.register(TaskCreateTool())
    self.tool_registry.register(TaskListTool())
    self.tool_registry.register(TaskCompleteTool())

    # Notificaciones
    self.tool_registry.register(NotificationSendTool())
```

### Flujo de ejecución

1. **Usuario envía mensaje**: "Crea una tarea para revisar el código"
2. **Agente recibe mensaje** y lo procesa con el LLM
3. **LLM decide usar tool**: `task_create` con parámetros
4. **ToolRegistry ejecuta**: Llama a `TaskCreateTool.execute()`
5. **Tool interactúa con BD**: Crea la tarea en SQLite
6. **Resultado vuelve al LLM**: {"success": true, "task": {...}}
7. **LLM responde al usuario**: "He creado la tarea 'Revisar código'"

---

## 🧪 Tests de Integración

**Ubicación:** `scripts/test_integrations.py`

Script que prueba todas las integraciones:

```bash
uv run python scripts/test_integrations.py
```

### Pruebas incluidas

1. **Calcurse**
   - Crear evento
   - Crear tarea
   - Obtener agenda

2. **Base de datos**
   - Crear tarea
   - Listar tareas
   - Completar tarea
   - Verificar estado

3. **Notificaciones**
   - Enviar notificación básica
   - Enviar recordatorio de tarea

### Salida esperada

```
=== Probando integración con Calcurse ===
Crear evento: {'success': True, ...}
Crear tarea: {'success': True, ...}
Obtener agenda: {'success': True, ...}

=== Probando base de datos de tareas ===
Tarea creada: {...}
Tareas pendientes: 1
Tarea completada: True
Tareas completadas: 1

=== Probando sistema de notificaciones ===
Notificación enviada: True
Recordatorio de tarea enviado: True

✓ Todas las pruebas completadas exitosamente
```

---

## 📝 Notas de Implementación

### Decisiones de diseño

1. **Calcurse con iCal**: Se eligió importar eventos en formato iCal en lugar de usar la sintaxis nativa de calcurse porque es más estándar y robusto.

2. **SQLite para tareas**: Se usa una base de datos separada para tareas (en lugar de solo calcurse) para permitir:
   - Búsqueda y filtrado avanzado
   - Campos personalizados (tags, descripción extendida)
   - Mayor flexibilidad en consultas

3. **Notificaciones asíncronas**: Aunque `notify-send` es síncrono, se mantiene la interfaz async para consistencia y futura implementación de notificaciones programadas.

### Limitaciones actuales

1. **Calcurse**:
   - No se implementaron notas para eventos/tareas (métodos stub)
   - No hay edición de eventos existentes
   - No hay eliminación de eventos

2. **Base de datos**:
   - No hay migraciones automáticas
   - No hay índices optimizados (por ahora no es necesario)

3. **Notificaciones**:
   - Solo funciona en sistemas con notify-send (Linux/Unix)
   - No hay notificaciones programadas (próximamente con APScheduler)

### Próximos pasos

1. Implementar notificaciones programadas con APScheduler
2. Agregar edición y eliminación de eventos en Calcurse
3. Implementar sincronización bidireccional Calcurse ↔ SQLite
4. Agregar búsqueda full-text en tareas
5. Implementar sistema de recordatorios inteligentes
