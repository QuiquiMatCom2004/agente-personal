# Contexto del Proyecto: Agente Personal Inteligente

## Visión General

Este es un agente personal inteligente potenciado por Claude (Anthropic) que ayuda al usuario a mantenerse organizado, gestionar su calendario, planificar aprendizaje de nuevas habilidades, y automatizar tareas diarias.

## Objetivos Principales

1. **Gestión de calendario y tareas**
   - Crear, modificar y consultar eventos
   - Detectar conflictos en el calendario
   - Sugerir horarios óptimos para tareas
   - Cancelar/reprogramar eventos

2. **Planificación de aprendizaje**
   - Analizar disponibilidad de tiempo del usuario
   - Crear planes estructurados para aprender nuevas habilidades
   - Implementar spaced repetition para retención
   - Ajustar dinámicamente el plan según progreso
   - Sugerir bloques de tiempo óptimos basados en energía/productividad

3. **Sistema de notificaciones proactivas**
   - Recordatorios basados en contexto
   - Alertas de deadlines
   - Notificaciones de conflictos
   - Resúmenes diarios/semanales

4. **Multi-interface**
   - CLI local (ya implementado)
   - Bot de Telegram (para acceso remoto)
   - API Web (para interfaz web/móvil)
   - Todas las interfaces comparten el mismo core del agente

5. **Launcher de aplicaciones**
   - Abrir aplicaciones relacionadas con tareas
   - Ejecutar scripts según contexto
   - Integración con el sistema operativo

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                 Interfaces (Frontends)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ CLI/TUI  │  │ Telegram │  │ Web API  │          │
│  │  Local   │  │   Bot    │  │ (REST)   │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼─────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────▼─────────────────────┐
        │      Agent Core (Backend)         │
        │  - LLM orchestration (Claude)     │
        │  - Business logic                 │
        │  - Task scheduling                │
        │  - Memory/context management      │
        │  - Learning planner               │
        └─────────────┬───────────────────┬─┘
                      │                   │
        ┌─────────────▼─────────┐  ┌─────▼──────┐
        │   Data Layer          │  │ Integrations│
        │  - SQLite DB          │  │ - Calendar  │
        │  - Task storage       │  │ - GitHub    │
        │  - Conversation hist  │  │ - Email     │
        │  - Vector store       │  │ - Logseq    │
        └───────────────────────┘  └────────────┘
```

## Stack Tecnológico

- **Python 3.11+** con UV package manager
- **Anthropic SDK** para Claude API
- **Rich** para CLI con colores/markdown
- **FastAPI** para Web API (futuro)
- **python-telegram-bot** para bot de Telegram
- **SQLAlchemy** para persistencia
- **APScheduler** para tareas programadas
- **Calcurse** integración para calendario local
- **Dunst** para notificaciones desktop (Linux)

## Sistema Operativo

- **Arch Linux** (sistema del usuario)
- Integración profunda con herramientas Unix
- Uso de dunst para notificaciones
- Calcurse para gestión de calendario

## Features Implementados (v0.1.0)

✅ Core del agente con Claude API
✅ Sistema de configuración (env + YAML)
✅ Interfaz CLI interactiva con Rich
✅ Historial de conversaciones por usuario
✅ System prompt personalizable
✅ Estructura modular y extensible
✅ Logging configurable

## Features Pendientes (Prioridad)

1. **Integración con calendario (calcurse)**
   - Leer eventos existentes
   - Crear nuevos eventos
   - Detectar conflictos
   - Proponer horarios óptimos

2. **Sistema de notificaciones**
   - Notificaciones desktop con dunst
   - Recordatorios programados con APScheduler
   - Integración con Telegram para notificaciones remotas

3. **Base de datos para tareas**
   - SQLite para almacenar tareas
   - Modelo de datos: Task, Event, LearningGoal
   - Queries para buscar/filtrar

4. **Bot de Telegram**
   - Comandos básicos (/agenda, /task, etc.)
   - Conversación natural igual que CLI
   - Notificaciones push

5. **Planificador de aprendizaje inteligente**
   - Analizar calendario actual
   - Calcular tiempo disponible
   - Crear curriculum progresivo
   - Spaced repetition scheduling
   - Ajuste dinámico según progreso

6. **Integración con knowledge bases**
   - Logseq (markdown files)
   - AppFlowy (base de datos)
   - Sincronización bidireccional

## Casos de Uso Clave

### Caso 1: Planificación de aprendizaje
```
Usuario: "Quiero aprender Flutter, tengo 8 horas por semana"

Agente analiza:
- Calendario actual del usuario
- Detecta 3 bloques de 2h libres entre semana
- Encuentra 2h el sábado por la mañana
- Revisa literatura: Flutter requiere ~100-120h para nivel básico

Agente propone:
- Plan de 15 semanas (8h/semana)
- Sesiones: Martes 10-12, Jueves 10-12, Viernes 15-17, Sábado 9-11
- Milestones cada 3 semanas
- Mini-proyectos para práctica
- Sistema de revisión con spaced repetition

Agente ejecuta:
- Crea eventos en calendario
- Crea página en Logseq con estructura
- Configura recordatorios 15min antes
- Programa revisiones en intervalos [1, 2, 4, 7, 14 días]
```

### Caso 2: Gestión diaria
```
Usuario: "Qué tengo hoy?"

Agente:
- Lee calendario de calcurse
- Consulta tareas pendientes de DB
- Revisa deadlines próximos
- Genera resumen contextualizado

"Hoy tienes:
- 10:00-11:00 Standup meeting
- 14:00-16:00 [BLOQUEADO] Sesión de aprendizaje Flutter
- 17:00 [RECORDATORIO] Enviar reporte semanal

Tareas pendientes:
- [URGENTE] Revisar PR #234 (deadline hoy)
- [ALTA] Escribir documentación API
- [MEDIA] Actualizar dependencias

Recomendación: Tienes 2h libres por la mañana, ideal para la tarea urgente."
```

## Principios de Diseño

1. **Proactividad**: El agente anticipa necesidades, no solo reacciona
2. **Contextualidad**: Mantiene memoria y entiende el contexto completo
3. **Modularidad**: Separación clara entre interfaces, core y integraciones
4. **Extensibilidad**: Fácil agregar nuevas interfaces o integraciones
5. **Privacy-first**: Datos almacenados localmente, opción de self-host
6. **Multi-plataforma**: Acceso desde CLI, Telegram, Web

## Notas de Implementación

- El agente NO debe sacrificar funcionalidad local por funcionalidad remota
- Telegram/Web son "ventanas adicionales" al mismo agente local
- Sincronización de estado entre interfaces mediante Redis (opcional)
- Priorizar UX: respuestas concisas, acciones claras
- El agente debe confirmar acciones importantes antes de ejecutarlas

## Configuración del Usuario

- **Zona horaria**: America/Mexico_City
- **Idioma**: Español
- **Horario de trabajo**: 09:00-18:00
- **Bloques de deep work**: 10:00-12:00, 15:00-17:00
- **Sistema**: Arch Linux

## Referencias

- Documentación de Anthropic: https://docs.anthropic.com
- Calcurse: https://calcurse.org/
- Python-telegram-bot: https://python-telegram-bot.org/
