# 📱 Integr aciones de Comunicaciones - Especificación Técnica

Este documento detalla la implementación de las integraciones con redes sociales y plataformas de comunicación.

---

## 🏗️ Arquitectura General

### Principios de Diseño

1. **Clasificación Inteligente de Contactos**
   - Sistema automático de categorización
   - Aprendizaje basado en interacciones
   - Reglas configurables por usuario

2. **Respuestas Automatizadas Éticas**
   - NUNCA responder automáticamente a familia/amigos
   - Solo contextos de negocio claramente identificados
   - Usuario tiene control total
   - Transparencia en todas las acciones

3. **Priorización Inteligente**
   - Análisis de contenido con IA
   - Urgencia basada en palabras clave
   - Contexto histórico del contacto
   - Deadlines y fechas importantes

---

## 📧 Gmail - Especificación Detallada

### Arquitectura

```python
src/integrations/gmail/
├── __init__.py
├── client.py           # GmailClient - API wrapper
├── classifier.py       # EmailClassifier - Priorización
├── responder.py        # AutoResponder - Plantillas
└── parser.py          # EmailParser - Extracción de info
```

### Flujo de Trabajo

```
1. Polling cada 5 min → Obtener nuevos emails
2. Clasificación → Urgente/Alto/Medio/Bajo
3. Análisis → Requiere acción? Es de trabajo?
4. Si es urgente → Notificación inmediata
5. Si es de negocio + auto-reply habilitado → Responder
6. Crear tarea si requiere seguimiento
7. Agregar a resumen diario
```

### Base de Datos

```sql
-- Tabla de emails procesados
emails:
  - id (message_id de Gmail)
  - from_email
  - from_name
  - subject
  - snippet
  - received_at
  - priority (urgent/high/medium/low)
  - category (work/personal/marketing/other)
  - requires_action (boolean)
  - action_deadline
  - auto_replied (boolean)
  - task_created_id
  - read_at
  - archived_at

-- Tabla de contactos clasificados
email_contacts:
  - email
  - name
  - classification (business/personal/vip/marketing)
  - auto_reply_enabled
  - priority_keywords []
  - interaction_count
  - last_interaction
  - notes
```

### Clasificación de Prioridad

**URGENTE:**
- De jefe/superiores directos
- Contiene: "urgente", "asap", "inmediato"
- CC a muchas personas importantes
- Respuesta requerida hoy

**ALTA:**
- De clientes/proveedores importantes
- Sobre proyectos activos
- Reuniones/deadlines próximos
- Contiene: "importante", "deadline"

**MEDIA:**
- Emails de trabajo normales
- Newsletters relevantes
- Notificaciones de servicios

**BAJA:**
- Marketing/promociones
- Notificaciones automáticas
- Spam

### Respuestas Automáticas

**Plantillas Configurables:**

```yaml
gmail:
  auto_reply:
    enabled: true
    only_business_hours: true
    templates:
      acknowledgment:
        text: "Gracias por tu email. Lo he recibido y te responderé a la brevedad."
        conditions:
          - priority: ["urgent", "high"]
          - first_contact: true

      out_of_office:
        text: "Estoy fuera de la oficina. Responderé tu mensaje el {return_date}."
        conditions:
          - user_status: "vacation"

      meeting_confirm:
        text: "Reunión confirmada para {date} a las {time}. Gracias!"
        conditions:
          - contains: ["reunión", "meeting", "junta"]

      custom_business:
        text: "Tu mensaje es importante. Estoy revisando varios asuntos y te contactaré pronto."
        conditions:
          - contact_type: "business"
          - working_hours: true
```

### Herramientas Implementadas

```python
class GmailReadTool(Tool):
    """Lee emails no leídos con filtros."""
    name = "gmail_read_unread"
    parameters:
      - priority: Optional[str]  # urgent/high/medium/low
      - limit: int = 10
      - category: Optional[str]  # work/personal/marketing

class GmailReplyTool(Tool):
    """Responde email con plantilla."""
    name = "gmail_reply_template"
    parameters:
      - email_id: str
      - template: str  # acknowledgment/meeting_confirm/custom
      - custom_text: Optional[str]

class GmailSummaryTool(Tool):
    """Genera resumen de emails."""
    name = "gmail_get_summary"
    parameters:
      - period: str  # today/week/month
      - priority: Optional[str]

class GmailCreateTaskTool(Tool):
    """Crea tarea desde email."""
    name = "gmail_create_task_from_email"
    parameters:
      - email_id: str
      - title: str
      - priority: str
      - due_date: Optional[str]
```

### Ejemplos de Uso

```python
# Usuario: "Muéstrame mis emails urgentes"
→ gmail_read_unread(priority="urgent", limit=5)

# Usuario: "Responde al email de Juan confirmando la reunión"
→ gmail_reply_template(email_id="abc123", template="meeting_confirm")

# Usuario: "Resumen de emails de hoy"
→ gmail_get_summary(period="today")

# Usuario: "Crea una tarea para responder el email de María"
→ gmail_create_task_from_email(email_id="xyz789", title="Responder a María")
```

---

## 🐙 GitHub - Especificación Detallada

### Arquitectura

```python
src/integrations/github/
├── __init__.py
├── client.py          # GitHubClient - API wrapper
├── notifier.py        # NotificationHandler
├── pr_manager.py      # PullRequestManager
└── issue_manager.py   # IssueManager
```

### Clasificación de Notificaciones

**CRÍTICO:**
- PRs que te bloquean
- Mentions directos en issues críticos
- Build failures en tus PRs
- Security alerts

**ALTO:**
- PRs asignados para review
- Issues asignados a ti
- Mentions en discusiones
- CI/CD completado en tus PRs

**MEDIO:**
- Actividad en PRs watching
- Nuevos issues en repos importantes
- Releases de dependencias

**BAJO:**
- Actividad en repos watching
- Stars/forks de tus repos
- Actualizaciones de issues cerrados

### Integración con Tareas

```python
# Sincronización bidireccional
Issues de GitHub ←→ Tareas del Agente

# Flujos:
1. Issue asignado en GitHub → Crea tarea automática
2. Tarea completada → Opción de comentar en issue
3. PR aprobado → Marca tarea de review como completada
4. Deadline en issue → Alarma/recordatorio automático
```

### Herramientas

```python
class GitHubNotificationsTool(Tool):
    """Lee notificaciones de GitHub."""
    name = "github_get_notifications"
    parameters:
      - priority: Optional[str]
      - unread_only: bool = True
      - participating_only: bool = False

class GitHubCreateIssueTool(Tool):
    """Crea issue en GitHub."""
    name = "github_create_issue"
    parameters:
      - repo: str
      - title: str
      - body: str
      - labels: Optional[List[str]]
      - assignees: Optional[List[str]]

class GitHubReviewPRTool(Tool):
    """Revisa PR (comentar/aprobar)."""
    name = "github_review_pr"
    parameters:
      - repo: str
      - pr_number: int
      - action: str  # comment/approve/request_changes
      - body: str

class GitHubSyncTasksTool(Tool):
    """Sincroniza issues con tareas."""
    name = "github_sync_tasks"
    parameters:
      - repo: Optional[str]
      - create_from_assigned: bool = True
```

---

## 💼 LinkedIn - Especificación Detallada

### Uso Ético y Limitaciones

**Importante:** LinkedIn tiene restricciones estrictas en su API. Esta integración es principalmente para:
- Notificaciones de mensajes
- Alertas de oportunidades laborales
- Gestión básica de networking

**NO para:**
- Spam o mensajes masivos
- Scraping agresivo
- Automatización de conexiones masivas

### Funcionalidades

```python
src/integrations/linkedin/
├── __init__.py
├── client.py          # LinkedInClient
├── job_alerts.py      # JobAlertManager
└── networking.py      # NetworkingManager
```

### Herramientas

```python
class LinkedInMessagesTool(Tool):
    """Lee mensajes de LinkedIn."""
    name = "linkedin_get_messages"
    parameters:
      - unread_only: bool = True
      - limit: int = 10

class LinkedInReplyTool(Tool):
    """Responde mensaje con plantilla."""
    name = "linkedin_reply_template"
    parameters:
      - conversation_id: str
      - template: str  # thanks_connection/interesting_proposal
      - custom_text: Optional[str]

class LinkedInJobAlertsTool(Tool):
    """Obtiene alertas de empleo."""
    name = "linkedin_get_job_alerts"
    parameters:
      - keywords: Optional[List[str]]
      - location: Optional[str]
      - remote_only: bool = False
```

---

## 📱 WhatsApp - Especificación Detallada

### Arquitectura

**Opción 1: WhatsApp Business API** (Oficial, requiere aprobación)
**Opción 2: whatsapp-web.js** (No oficial, más flexible)

```python
src/integrations/whatsapp/
├── __init__.py
├── client.py          # WhatsAppClient
├── classifier.py      # ContactClassifier
└── responder.py       # AutoResponder
```

### Sistema de Clasificación de Contactos

**CRÍTICO:**
```yaml
contact_classification:
  business:
    auto_reply: true
    templates_enabled: true
    notifications: immediate
    examples:
      - "+52XXXXXXXXXX"  # Cliente importante
      - "+52YYYYYYYYYY"  # Proveedor

  personal:
    auto_reply: false  # NUNCA
    templates_enabled: false
    notifications: normal
    examples:
      - "+52ZZZZZZZZZ"  # Familia
      - "+52AAAAAAAAA"  # Amigos

  networking:
    auto_reply: true
    templates_enabled: true
    notifications: normal
    # Contactos profesionales, pero no clientes directos
```

### Reglas de Auto-Reply

**Habilitado SOLO para:**
1. Contactos marcados explícitamente como "business"
2. Durante horario laboral (configurable)
3. Usuario no está marcado como "disponible"

**NUNCA para:**
1. Familia (lista negra)
2. Amigos cercanos
3. Grupos familiares
4. Fuera de horario laboral (opcional)

### Herramientas

```python
class WhatsAppReadTool(Tool):
    """Lee mensajes de WhatsApp."""
    name = "whatsapp_read_messages"
    parameters:
      - unread_only: bool = True
      - contact_type: Optional[str]  # business/personal/all
      - limit: int = 10

class WhatsAppReplyTool(Tool):
    """Responde SOLO a contactos de negocio."""
    name = "whatsapp_reply_business"
    parameters:
      - chat_id: str
      - template: str
      - custom_text: Optional[str]

    # Validación interna:
    # 1. Verificar que contacto es "business"
    # 2. Verificar que auto_reply está habilitado
    # 3. Verificar horario laboral
    # 4. Registrar acción para auditoría

class WhatsAppClassifyContactTool(Tool):
    """Clasifica un contacto."""
    name = "whatsapp_classify_contact"
    parameters:
      - phone: str
      - classification: str  # business/personal/networking
      - auto_reply_enabled: bool
      - notes: Optional[str]
```

### Plantillas de Respuesta

```yaml
whatsapp:
  templates:
    busy:
      text: "Hola! Estoy en una reunión. Te respondo en cuanto termine."
      conditions:
        - user_status: "busy"
        - contact_type: "business"

    acknowledgment:
      text: "Mensaje recibido. Te contacto pronto."
      conditions:
        - contact_type: "business"
        - first_message_day: true

    out_of_office:
      text: "Estoy fuera de la oficina hasta el {date}. Para asuntos urgentes, contacta a {backup_contact}."
      conditions:
        - user_status: "vacation"
```

---

## 🔒 Seguridad y Privacidad

### Principios

1. **Consentimiento Explícito**
   - Usuario debe activar cada integración
   - Usuario debe autorizar auto-respuestas
   - Usuario puede deshabilitar en cualquier momento

2. **Transparencia Total**
   - Todas las acciones automáticas se registran
   - Usuario puede ver qué se envió y a quién
   - Historial de respuestas automáticas

3. **Control de Acceso**
   - Tokens encriptados en base de datos
   - OAuth 2.0 para todas las APIs
   - Refresh tokens seguros

4. **Auditoría**
   - Log de todas las acciones automáticas
   - Exportable para revisión del usuario

### Tabla de Auditoría

```sql
automation_log:
  - id
  - timestamp
  - integration  # gmail/whatsapp/linkedin
  - action  # auto_reply/classification/notification
  - contact  # email/phone
  - message_sent
  - template_used
  - user_id
  - success
```

---

## 📊 Dashboard de Comunicaciones

### Vista Consolidada

```
┌─────────────────────────────────────────────────┐
│  Centro de Comunicaciones                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  📧 Gmail: 5 no leídos (2 urgentes)            │
│  🐙 GitHub: 3 notificaciones (1 PR bloqueante) │
│  💼 LinkedIn: 2 mensajes nuevos                 │
│  📱 WhatsApp: 4 mensajes (1 negocio)           │
│                                                  │
│  ⚡ Acciones Rápidas:                           │
│  • Responder emails urgentes                    │
│  • Revisar PR bloqueante                        │
│  • Leer mensajes de LinkedIn                    │
│                                                  │
│  🤖 Automatizaciones Hoy:                       │
│  • 3 emails auto-respondidos                    │
│  • 1 tarea creada desde email                   │
│  • 2 notificaciones de GitHub priorizadas       │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Plan de Implementación

### Fase 1: Gmail (2-3 semanas)
- Semana 1: Cliente Gmail + Clasificador
- Semana 2: Auto-respuestas + Plantillas
- Semana 3: Integración con tareas + Tests

### Fase 2: GitHub (1-2 semanas)
- Semana 1: Cliente + Notificaciones
- Semana 2: Sincronización con tareas

### Fase 3: LinkedIn (1 semana)
- Implementación básica
- Job alerts
- Mensajería

### Fase 4: WhatsApp (2 semanas)
- Semana 1: Cliente + Clasificación
- Semana 2: Auto-respuestas + Seguridad

---

Última actualización: Octubre 2025
