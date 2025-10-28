# 🗺️ Roadmap del Agente Personal

Este documento describe la hoja de ruta completa del proyecto, incluyendo funcionalidades implementadas y planificadas.

---

## ✅ Fase 1: Core del Agente (COMPLETADO)

### Sistema Base
- [x] **Arquitectura de orquestación** - Function calling con OpenRouter
- [x] **Sistema de herramientas (Tools)** - Framework extensible
- [x] **Gestión de configuración** - `.env` + `agent_config.yaml`
- [x] **Sistema de logging** - Logs estructurados
- [x] **Multi-usuario** - Soporte via `user_id`

### Integraciones Core
- [x] **Calcurse** - Calendario y tareas en terminal
- [x] **SQLite** - Persistencia de tareas con aiosqlite
- [x] **Dunst** - Notificaciones desktop
- [x] **APScheduler** - Recordatorios programados
- [x] **Sistema de alarmas** - Alarmas con sonido persistente

### Interfaces
- [x] **CLI** - Interfaz de línea de comandos con Rich
- [x] **Bot de Telegram** - Interface móvil completa

### Herramientas Implementadas (10)
1. `calendar_create_event` - Crear eventos
2. `calendar_get_agenda` - Ver agenda
3. `task_create` - Crear tareas
4. `task_list` - Listar tareas
5. `task_complete` - Completar tareas
6. `notification_send` - Notificaciones
7. `reminder_create` - Recordatorios
8. `reminder_list` - Ver recordatorios
9. `reminder_cancel` - Cancelar recordatorios
10. `alarm_create` - Alarmas con sonido

---

## 🚀 Fase 2: Gestión de Comunicaciones (EN PROGRESO)

### Integraciones de Redes Sociales y Comunicación

#### 📧 Gmail - Gestión Inteligente de Emails
**Estado:** Planificado
**Prioridad:** ALTA

**Funcionalidades:**
- [ ] Leer emails no leídos
- [ ] Clasificación automática por prioridad
  - Urgente: De jefes, clientes importantes, palabras clave
  - Alta: Trabajo, proyectos activos
  - Media: Newsletters relevantes
  - Baja: Marketing, promociones
- [ ] Respuestas automatizadas con plantillas de negocio
  - Plantilla: "Recibido, te respondo en X horas"
  - Plantilla: "Gracias por tu email, lo reviso y te contesto"
  - Plantilla: "Reunión confirmada para X fecha"
- [ ] Resúmenes diarios/semanales
- [ ] Detección de emails que requieren acción
- [ ] Integración con tareas (crear tarea desde email)

**Herramientas:**
- `gmail_read_unread` - Leer emails no leídos
- `gmail_send` - Enviar email
- `gmail_reply_template` - Responder con plantilla
- `gmail_get_summary` - Resumen de emails
- `gmail_create_task_from_email` - Crear tarea desde email

**Configuración:**
```yaml
integrations:
  gmail:
    enabled: true
    check_interval: 300  # 5 minutos
    priority_keywords:
      urgent: ["urgente", "asap", "importante"]
      business: ["reunión", "proyecto", "entrega"]
    auto_reply:
      enabled: true
      only_business_hours: true
      templates:
        acknowledgment: "Gracias por tu email. Lo revisaré pronto."
        meeting_confirm: "Reunión confirmada."
```

---

#### 🐙 GitHub - Notificaciones y Gestión de Proyectos
**Estado:** Planificado
**Prioridad:** ALTA

**Funcionalidades:**
- [ ] Notificaciones de PRs, issues, mentions
- [ ] Clasificación por prioridad
  - Crítico: PRs que te bloquean, mentions directos
  - Alto: PRs para review, issues asignados
  - Medio: Actividad en repos watching
- [ ] Resumen diario de actividad
- [ ] Creación rápida de issues
- [ ] Review de PRs (comentarios, aprobar)
- [ ] Integración con tareas (crear tarea desde issue)

**Herramientas:**
- `github_get_notifications` - Obtener notificaciones
- `github_create_issue` - Crear issue
- `github_review_pr` - Revisar PR
- `github_get_summary` - Resumen de actividad
- `github_sync_tasks` - Sincronizar con tareas

**Configuración:**
```yaml
integrations:
  github:
    enabled: true
    check_interval: 600  # 10 minutos
    repos_watching:
      - "user/important-repo"
      - "org/project"
    notifications:
      priority_labels:
        critical: ["bug", "urgent", "blocking"]
        high: ["enhancement", "needs-review"]
```

---

#### 💼 LinkedIn - Networking y Oportunidades
**Estado:** Planificado
**Prioridad:** MEDIA

**Funcionalidades:**
- [ ] Notificaciones de mensajes
- [ ] Resumen de actividad de tu red
- [ ] Alertas de empleos relevantes
- [ ] Respuestas automatizadas (solo networking)
  - Plantilla: "Gracias por conectar, charlemos pronto"
  - Plantilla: "Interesante propuesta, te contacto en X días"
- [ ] Programar posts (contenido profesional)

**Herramientas:**
- `linkedin_get_messages` - Leer mensajes
- `linkedin_reply_template` - Responder con plantilla
- `linkedin_get_job_alerts` - Alertas de empleo
- `linkedin_schedule_post` - Programar publicación

**Configuración:**
```yaml
integrations:
  linkedin:
    enabled: true
    check_interval: 3600  # 1 hora
    job_alerts:
      enabled: true
      keywords: ["python", "ai", "remote"]
    auto_reply:
      enabled: true
      only_connections: true  # Solo responder a conexiones
```

---

#### 📱 WhatsApp - Mensajes de Negocio
**Estado:** Planificado
**Prioridad:** MEDIA

**Funcionalidades:**
- [ ] Leer mensajes de WhatsApp Web
- [ ] Clasificación por contacto (negocio vs personal)
- [ ] Respuestas automatizadas SOLO para negocio
  - Plantilla: "Hola, estoy en una reunión. Te respondo en X minutos"
  - Plantilla: "Mensaje recibido, te contacto pronto"
- [ ] NO responder automáticamente a familiares/amigos
- [ ] Notificaciones de mensajes importantes
- [ ] Programar mensajes

**Herramientas:**
- `whatsapp_read_messages` - Leer mensajes
- `whatsapp_send` - Enviar mensaje
- `whatsapp_reply_template` - Responder con plantilla (solo negocio)
- `whatsapp_schedule_message` - Programar mensaje

**Configuración:**
```yaml
integrations:
  whatsapp:
    enabled: true
    business_contacts:
      - "+1234567890"  # Cliente
      - "+0987654321"  # Proveedor
    auto_reply:
      enabled: true
      only_business: true  # SOLO contactos de negocio
      blacklist_family: true  # NO responder a familia
      templates:
        busy: "Estoy en una reunión, te respondo pronto."
        acknowledgment: "Mensaje recibido."
```

---

#### 📲 Telegram - Notificaciones del Bot
**Estado:** ✅ COMPLETADO
**Prioridad:** ALTA

**Funcionalidades:**
- [x] Bot completo funcional
- [x] Comandos: /start, /help, /agenda, /tareas
- [x] Conversación en lenguaje natural
- [x] Todas las herramientas disponibles
- [x] Sistema de autorización por user_id
- [x] Notificaciones push (futuro)

**Configuración:**
```yaml
integrations:
  telegram:
    enabled: true
    allowed_users:
      - 123456789
      - 987654321
    notifications:
      enabled: true
      events: true
      tasks: true
      reminders: true
```

---

## 💰 Fase 3: Gestión Financiera Personal (NUEVA!)

### Sistema de Finanzas Inteligente

**Estado:** Planificado
**Prioridad:** ALTA

#### Funcionalidades Core

##### 📊 Tracking de Gastos
- [ ] Registro manual de gastos
- [ ] Importación desde bancos (CSV/API)
- [ ] Categorización automática con IA
  - Comida y restaurantes
  - Transporte
  - Entretenimiento
  - Servicios (luz, agua, internet)
  - Suscripciones
  - Inversiones
  - Otros
- [ ] Detección de gastos recurrentes
- [ ] Alertas de gastos inusuales
- [ ] Presupuesto por categoría

##### 💳 Gestión de Cuentas
- [ ] Múltiples cuentas (banco, efectivo, tarjetas)
- [ ] Balance total consolidado
- [ ] Transferencias entre cuentas
- [ ] Historial de transacciones
- [ ] Sincronización con bancos (Open Banking API)

##### 📈 Inversiones y Ahorros
- [ ] Tracking de inversiones
- [ ] Metas de ahorro
- [ ] Proyecciones de ahorro
- [ ] Análisis de rentabilidad
- [ ] Alertas de objetivos alcanzados

##### 🧾 Facturas y Pagos
- [ ] Recordatorios de facturas por pagar
- [ ] Tracking de pagos recurrentes (Netflix, Spotify, etc.)
- [ ] Alertas antes de vencimiento
- [ ] Historial de pagos
- [ ] Detección de suscripciones olvidadas

##### 📊 Reportes e Insights
- [ ] Resumen mensual de gastos
- [ ] Comparación mes a mes
- [ ] Gráficos de gastos por categoría
- [ ] Análisis de tendencias
- [ ] Predicción de gastos futuros
- [ ] Recomendaciones de ahorro

**Herramientas Planificadas:**
- `finance_add_expense` - Registrar gasto
- `finance_add_income` - Registrar ingreso
- `finance_get_balance` - Ver balance actual
- `finance_get_summary` - Resumen financiero
- `finance_set_budget` - Establecer presupuesto
- `finance_get_insights` - Análisis inteligente
- `finance_import_transactions` - Importar desde banco
- `finance_track_investment` - Seguimiento de inversiones

**Base de Datos:**
```sql
-- Transacciones
transactions:
  - id
  - type (expense/income)
  - amount
  - category
  - description
  - account
  - date
  - recurring
  - tags

-- Cuentas
accounts:
  - id
  - name
  - type (bank/cash/card)
  - balance
  - currency

-- Presupuestos
budgets:
  - id
  - category
  - amount
  - period (daily/weekly/monthly)
  - alerts

-- Inversiones
investments:
  - id
  - name
  - type (stocks/crypto/fund)
  - amount_invested
  - current_value
  - date
```

**Integraciones:**
- [ ] Open Banking APIs (BBVA, Santander, etc.)
- [ ] Stripe/PayPal para freelancers
- [ ] Crypto exchanges (opcional)
- [ ] Google Sheets para backup
- [ ] Exportar a Excel/PDF

**Configuración:**
```yaml
finance:
  enabled: true
  default_currency: "MXN"
  accounts:
    - name: "Banco Principal"
      type: "bank"
    - name: "Efectivo"
      type: "cash"
  budgets:
    monthly:
      food: 5000
      transport: 2000
      entertainment: 1500
      services: 3000
  alerts:
    high_expense_threshold: 1000
    low_balance_warning: 500
    budget_warning_percent: 80
  auto_categorization:
    enabled: true
    learning: true  # Aprende de tus categorizaciones
```

**Ejemplos de Uso:**
```
"Registra un gasto de $250 en comida"
"Cuál es mi balance total?"
"Cuánto he gastado este mes en transporte?"
"Estoy dentro de mi presupuesto de comida?"
"Crea una meta de ahorro de $10,000 para diciembre"
"Muéstrame mi resumen financiero del mes"
"Importa mis transacciones del banco"
"Alértame si gasto más de $1000 en un día"
```

---

## 📊 Fase 4: Análisis y Business Intelligence (FUTURO)

### Informes Inteligentes

#### Resúmenes Automáticos
- [ ] Resumen diario (mañana, 8 AM)
  - Emails importantes recibidos
  - PRs/issues que requieren atención
  - Tareas del día
  - Eventos del día
  - Mensajes de negocio pendientes

- [ ] Resumen semanal (domingo, 6 PM)
  - Productividad de la semana
  - Tareas completadas vs pendientes
  - Actividad en redes sociales
  - Oportunidades no atendidas

- [ ] Alertas en tiempo real
  - Email urgente detectado
  - PR crítico requiere review
  - Mensaje importante en WhatsApp
  - Conflicto en calendario

#### Dashboard Web
- [ ] Vista unificada de todas las plataformas
- [ ] Gráficos de productividad
- [ ] Timeline de actividades
- [ ] Centro de notificaciones consolidado

---

## 🧠 Fase 4: Inteligencia Avanzada (FUTURO)

### Aprendizaje y Automatización

#### Sistema de Aprendizaje
- [ ] Aprender patrones de respuesta del usuario
- [ ] Sugerir respuestas basadas en contexto
- [ ] Detectar contactos de negocio automáticamente
- [ ] Mejorar clasificación de prioridades con uso

#### Automatizaciones Inteligentes
- [ ] Crear tareas automáticamente desde emails
- [ ] Sincronizar deadlines de GitHub con calendario
- [ ] Sugerir tiempos óptimos para responder
- [ ] Detectar oportunidades de networking

#### Integraciones Adicionales
- [ ] Slack - Mensajes de equipo
- [ ] Discord - Comunidades y proyectos
- [ ] Google Calendar - Sincronización bidireccional
- [ ] Notion/Obsidian - Knowledge base
- [ ] Trello/Jira - Gestión de proyectos

---

## 🏗️ Fase 5: Infraestructura Avanzada (FUTURO)

### Escalabilidad
- [ ] API REST completa (FastAPI)
- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Sincronización multi-dispositivo (Redis)
- [ ] App móvil nativa (React Native)
- [ ] Extensión de navegador (Chrome/Firefox)

### Seguridad
- [ ] Encriptación de datos sensibles
- [ ] Autenticación OAuth para todas las integraciones
- [ ] Auditoría de acciones automáticas
- [ ] Modo "solo lectura" para respuestas automáticas

### Performance
- [ ] Caché inteligente de consultas
- [ ] Procesamiento asíncrono de notificaciones
- [ ] Queue system para tareas pesadas
- [ ] CDN para assets estáticos

---

## 📅 Timeline Estimado

### Q1 2025
- ✅ Core del agente (Fase 1) - COMPLETADO
- ✅ Bot de Telegram - COMPLETADO
- ✅ Sistema de alarmas - COMPLETADO
- 🔄 Integración Gmail - SIGUIENTE
- 🔄 Integración GitHub - SIGUIENTE

### Q2 2025
- 💰 Sistema de finanzas personal
- 📱 LinkedIn, WhatsApp
- 📊 Resúmenes automáticos
- 🌐 Dashboard web básico

### Q3 2025
- 🧠 Inteligencia avanzada
- 🤖 Automatizaciones
- 🔌 Más integraciones (Slack, Discord)

### Q4 2025
- 🏗️ Infraestructura escalable
- 📱 App móvil
- 🔧 Extensión de navegador

---

## 🎯 Prioridades Actuales

### Completadas
1. ✅ **Sistema de alarmas** - COMPLETADO
2. ✅ **Bot de Telegram** - COMPLETADO

### En Cola (Orden de Implementación)
3. 🔄 **Integración Gmail** - ALTA PRIORIDAD
   - Clasificación inteligente
   - Respuestas automáticas de negocio
   - Resúmenes diarios

4. 🔄 **Integración GitHub** - ALTA PRIORIDAD
   - Notificaciones priorizadas
   - Gestión de PRs/issues
   - Sincronización con tareas

5. 💰 **Sistema de Finanzas** - ALTA PRIORIDAD
   - Tracking de gastos
   - Presupuestos y metas
   - Análisis inteligente

6. 📱 **LinkedIn** - MEDIA PRIORIDAD
   - Networking automatizado
   - Alertas de oportunidades

7. 📱 **WhatsApp** - MEDIA PRIORIDAD
   - Respuestas de negocio
   - Clasificación de contactos

8. 🌐 **Dashboard Web** - MEDIA PRIORIDAD
   - Visualización consolidada
   - Centro de control

---

## 🤝 Contribuciones

Este es un proyecto personal, pero las ideas y sugerencias son bienvenidas.

Para proponer nuevas integraciones o features:
1. Abre un issue en GitHub
2. Describe el caso de uso
3. Sugiere la prioridad

---

## 📝 Notas de Diseño

### Filosofía de Respuestas Automáticas

**Principios:**
1. **NUNCA** responder automáticamente a familia/amigos
2. Respuestas automáticas **SOLO** en contexto de negocio
3. Siempre dar la opción de deshabilitar auto-respuestas
4. Las plantillas deben ser profesionales pero cercanas
5. Informar al usuario de todas las acciones automáticas

**Clasificación de Contactos:**
- **Negocio:** Clientes, proveedores, colegas de trabajo
- **Personal:** Familia, amigos cercanos
- **Networking:** Contactos profesionales, LinkedIn
- **Marketing:** Newsletters, promociones

**Niveles de Automatización:**
- **Nivel 0:** Solo notificaciones (familia)
- **Nivel 1:** Notificaciones + resúmenes (networking)
- **Nivel 2:** Notificaciones + respuestas plantilla (negocio)
- **Nivel 3:** Automatización completa (marketing)

---

## 🔒 Consideraciones de Privacidad

- Todas las credenciales en `.env` (nunca en código)
- OAuth 2.0 para todas las integraciones
- Encriptación de tokens en base de datos
- Logs sin información sensible
- Opción de borrar todo el historial
- Exportar/importar configuración

---

Última actualización: Octubre 2025
