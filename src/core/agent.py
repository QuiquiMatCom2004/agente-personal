"""Core del agente personal - Orquestación principal."""

from openai import OpenAI
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..utils.config import Settings
from ..tools import (
    ToolRegistry,
    CalendarTool,
    CalendarGetAgendaTool,
    TaskCreateTool,
    TaskListTool,
    TaskCompleteTool,
    NotificationSendTool,
    ReminderCreateTool,
    ReminderListTool,
    ReminderCancelTool,
    AlarmCreateTool,
)
from ..integrations import NotificationManager


logger = logging.getLogger(__name__)


class PersonalAgent:
    """
    Agente personal inteligente que gestiona tareas, calendario y aprendizaje.

    Este es el núcleo del sistema - maneja la lógica de negocio y orquesta
    todas las integraciones (calendario, notificaciones, etc.)
    """

    def __init__(self, settings: Optional[Settings] = None, config: Optional[Dict] = None):
        """
        Inicializa el agente personal.

        Args:
            settings: Configuración desde variables de entorno
            config: Configuración desde archivo YAML
        """
        self.settings = settings
        self.config = config or {}

        # Cliente de OpenAI configurado para OpenRouter
        self.client = OpenAI(
            api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url
        )

        # Registro de herramientas
        self.tool_registry = ToolRegistry()
        self._register_tools()

        # Gestor de notificaciones
        self.notification_manager = NotificationManager(
            app_name=self.config.get("agent", {}).get("name", "Agente Personal"),
            enable_sound=settings.notification_sound,
        )

        # Historial de conversación por usuario
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

        # Contexto del agente (system prompt)
        self.system_prompt = self._build_system_prompt()

        logger.info(f"Agente personal inicializado - Modelo: {settings.agent_model}")

    def _register_tools(self):
        """Registra todas las herramientas disponibles."""
        # Herramientas de calendario
        self.tool_registry.register(CalendarTool())
        self.tool_registry.register(CalendarGetAgendaTool())

        # Herramientas de tareas
        self.tool_registry.register(TaskCreateTool())
        self.tool_registry.register(TaskListTool())
        self.tool_registry.register(TaskCompleteTool())

        # Herramientas de notificaciones
        self.tool_registry.register(NotificationSendTool())

        # Herramientas de recordatorios
        self.tool_registry.register(ReminderCreateTool())
        self.tool_registry.register(ReminderListTool())
        self.tool_registry.register(ReminderCancelTool())

        # Herramientas de alarmas
        self.tool_registry.register(AlarmCreateTool())

        logger.info(f"{len(self.tool_registry.get_all())} herramientas registradas")

    def _build_system_prompt(self) -> str:
        """Construye el system prompt del agente basado en la configuración."""
        agent_name = self.config.get("agent", {}).get("name", "Agente Personal")
        personality = self.config.get("agent", {}).get("personality", "profesional y proactivo")
        language = self.config.get("agent", {}).get("language", "es")

        prompt = f"""Eres {agent_name}, un asistente personal inteligente con personalidad {personality}.

Tu propósito es ayudar al usuario a mantenerse organizado, productivo y alcanzar sus objetivos.

Capacidades:
- Gestionar tareas y eventos en el calendario
- Planificar tiempo de aprendizaje de nuevas habilidades
- Enviar recordatorios y notificaciones proactivas
- Detectar conflictos en el calendario
- Proponer horarios óptimos para tareas
- Lanzar aplicaciones relacionadas con tareas
- Mantener contexto de conversaciones previas

Principios de comportamiento:
1. Sé proactivo: anticipa necesidades y sugiere mejoras
2. Sé conciso: respuestas claras y directas
3. Sé contextual: recuerda conversaciones y tareas previas
4. Sé útil: prioriza la acción sobre la explicación
5. Comunícate en {language}

Cuando el usuario te pida:
- "agenda algo": crea un evento en el calendario
- "recuérdame": configura un recordatorio
- "cancela X": elimina o marca como completado
- "qué tengo": muestra agenda del día/semana
- "ayúdame a aprender X": crea un plan de aprendizaje estructurado

Siempre confirma acciones importantes antes de ejecutarlas."""

        return prompt

    async def process(self, message: str, user_id: str = "default") -> str:
        """
        Procesa un mensaje del usuario y genera una respuesta.

        Este método implementa un loop de orquestación:
        1. Envía el mensaje al LLM con las herramientas disponibles
        2. Si el LLM quiere usar herramientas, las ejecuta
        3. Envía los resultados de vuelta al LLM
        4. Repite hasta que el LLM genere una respuesta final

        Args:
            message: Mensaje del usuario
            user_id: Identificador del usuario (para multi-usuario)

        Returns:
            Respuesta del agente
        """
        try:
            # Obtener o crear historial de conversación
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            history = self.conversation_history[user_id]

            # Agregar mensaje del usuario al historial
            history.append({"role": "user", "content": message})

            # Limitar tamaño del historial
            max_messages = self.settings.agent_max_context_messages
            if len(history) > max_messages:
                history = history[-max_messages:]
                self.conversation_history[user_id] = history

            # Construir mensajes con system prompt al inicio
            messages = [{"role": "system", "content": self.system_prompt}] + history

            # Obtener herramientas en formato OpenAI
            tools = self.tool_registry.get_openai_tools()

            # Loop de orquestación (máximo 5 iteraciones para evitar loops infinitos)
            max_iterations = 5
            for iteration in range(max_iterations):
                # Llamar a OpenRouter con herramientas
                response = self.client.chat.completions.create(
                    model=self.settings.agent_model,
                    messages=messages,
                    tools=tools if tools else None,
                    max_tokens=2048,
                    temperature=self.settings.agent_temperature,
                )

                response_message = response.choices[0].message

                # Si no hay tool calls, retornar la respuesta
                if not response_message.tool_calls:
                    assistant_message = response_message.content or ""
                    history.append({"role": "assistant", "content": assistant_message})
                    logger.info(f"Mensaje procesado para usuario {user_id}")
                    return assistant_message

                # Hay tool calls - ejecutarlas
                logger.info(f"Ejecutando {len(response_message.tool_calls)} herramientas")

                # Agregar el mensaje del asistente al historial (con tool calls)
                messages.append(
                    {
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in response_message.tool_calls
                        ],
                    }
                )

                # Ejecutar cada tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Ejecutando herramienta: {tool_name} con args: {tool_args}")

                    # Ejecutar la herramienta
                    result = await self.tool_registry.execute_tool(tool_name, **tool_args)

                    # Agregar resultado al historial
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )

            # Si llegamos aquí, excedimos el máximo de iteraciones
            error_msg = "Se excedió el límite de iteraciones en la orquestación"
            logger.warning(error_msg)
            history.append({"role": "assistant", "content": error_msg})
            return error_msg

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            return f"Lo siento, ocurrió un error: {str(e)}"

    async def get_agenda(self, user_id: str = "default", days: int = 1) -> str:
        """
        Obtiene la agenda del usuario para los próximos N días.

        Args:
            user_id: Identificador del usuario
            days: Número de días a mostrar

        Returns:
            Resumen de la agenda
        """
        # TODO: Integrar con calendario real (calcurse)
        return f"Agenda para los próximos {days} días:\n(Integración con calendario pendiente)"

    async def create_task(
        self, title: str, description: str = "", priority: str = "medium", user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Crea una nueva tarea.

        Args:
            title: Título de la tarea
            description: Descripción detallada
            priority: Prioridad (urgent, high, medium, low)
            user_id: Identificador del usuario

        Returns:
            Información de la tarea creada
        """
        # TODO: Guardar en base de datos y/o integrar con Logseq
        task = {
            "id": f"task_{datetime.now().timestamp()}",
            "title": title,
            "description": description,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "completed": False,
            "user_id": user_id,
        }

        logger.info(f"Tarea creada: {task['id']}")
        return task

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int = 60,
        description: str = "",
        user_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Crea un evento en el calendario.

        Args:
            title: Título del evento
            start_time: Hora de inicio
            duration_minutes: Duración en minutos
            description: Descripción del evento
            user_id: Identificador del usuario

        Returns:
            Información del evento creado
        """
        # TODO: Integrar con calcurse
        event = {
            "id": f"event_{datetime.now().timestamp()}",
            "title": title,
            "start_time": start_time.isoformat(),
            "duration_minutes": duration_minutes,
            "description": description,
            "user_id": user_id,
        }

        logger.info(f"Evento creado: {event['id']}")
        return event

    def clear_history(self, user_id: str = "default"):
        """Limpia el historial de conversación de un usuario."""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
            logger.info(f"Historial limpiado para usuario {user_id}")
