"""Herramienta para programar recordatorios."""

import logging
from datetime import datetime
from typing import Dict, Any, List
from .base import Tool, ToolParameter

logger = logging.getLogger(__name__)

# Instancia global del scheduler
_reminder_scheduler = None


async def get_reminder_scheduler():
    """Obtiene o crea la instancia del scheduler de recordatorios."""
    global _reminder_scheduler
    if _reminder_scheduler is None:
        from ..integrations.scheduler import ReminderScheduler

        _reminder_scheduler = ReminderScheduler()
        await _reminder_scheduler.start()
    return _reminder_scheduler


class ReminderCreateTool(Tool):
    """Herramienta para crear recordatorios programados."""

    @property
    def name(self) -> str:
        return "reminder_create"

    @property
    def description(self) -> str:
        return (
            "Programa un recordatorio para una fecha/hora específica. "
            "Úsala cuando el usuario pida que le recuerdes algo en el futuro. "
            "Ejemplo: 'recuérdame llamar al dentista en 2 horas' o "
            "'recuérdame la reunión mañana a las 3pm'"
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="title",
                type="string",
                description="Título breve del recordatorio",
                required=True,
            ),
            ToolParameter(
                name="message",
                type="string",
                description="Mensaje detallado del recordatorio",
                required=True,
            ),
            ToolParameter(
                name="remind_at",
                type="string",
                description="Fecha y hora del recordatorio en formato ISO 8601 (ej: '2025-10-28T15:00:00')",
                required=True,
            ),
            ToolParameter(
                name="priority",
                type="string",
                description="Prioridad del recordatorio",
                required=False,
                enum=["low", "normal", "critical"],
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Programa un recordatorio.

        Args:
            title: Título del recordatorio
            message: Mensaje del recordatorio
            remind_at: Cuándo recordar (ISO 8601)
            priority: Prioridad (low, normal, critical)

        Returns:
            Dict con el resultado de la operación
        """
        title = kwargs.get("title")
        message = kwargs.get("message")
        remind_at_str = kwargs.get("remind_at")
        priority = kwargs.get("priority", "normal")

        try:
            # Parsear fecha
            remind_at = datetime.fromisoformat(remind_at_str)

            # Validar que sea futuro
            if remind_at <= datetime.now():
                return {
                    "success": False,
                    "error": "La fecha del recordatorio debe ser en el futuro",
                }

            # Generar ID único
            reminder_id = f"reminder_{int(datetime.now().timestamp())}"

            # Programar recordatorio
            scheduler = await get_reminder_scheduler()
            success = await scheduler.schedule_reminder(
                reminder_id=reminder_id,
                title=title,
                message=message,
                trigger_time=remind_at,
                priority=priority,
            )

            if success:
                # Calcular tiempo hasta el recordatorio
                time_until = remind_at - datetime.now()
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)

                time_desc = ""
                if hours > 0:
                    time_desc = f"{hours} hora{'s' if hours != 1 else ''}"
                    if minutes > 0:
                        time_desc += f" y {minutes} minuto{'s' if minutes != 1 else ''}"
                else:
                    time_desc = f"{minutes} minuto{'s' if minutes != 1 else ''}"

                return {
                    "success": True,
                    "message": f"Recordatorio '{title}' programado para {remind_at.strftime('%d/%m/%Y a las %H:%M')} (en {time_desc})",
                    "reminder_id": reminder_id,
                    "remind_at": remind_at.isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo programar el recordatorio",
                }

        except ValueError as e:
            return {
                "success": False,
                "error": f"Formato de fecha inválido: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Error programando recordatorio: {e}")
            return {
                "success": False,
                "error": f"Error programando recordatorio: {str(e)}",
            }


class ReminderListTool(Tool):
    """Herramienta para listar recordatorios programados."""

    @property
    def name(self) -> str:
        return "reminder_list"

    @property
    def description(self) -> str:
        return (
            "Lista todos los recordatorios programados. "
            "Úsala cuando el usuario pregunte qué recordatorios tiene activos."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return []

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Lista recordatorios programados.

        Returns:
            Dict con los recordatorios encontrados
        """
        try:
            scheduler = await get_reminder_scheduler()
            reminders = scheduler.list_scheduled_reminders()

            # Filtrar solo recordatorios de usuario (excluir jobs del sistema)
            user_reminders = [
                r for r in reminders if r["id"].startswith(("reminder_", "task_", "event_"))
            ]

            return {
                "success": True,
                "message": f"Se encontraron {len(user_reminders)} recordatorios programados",
                "reminders": user_reminders,
                "count": len(user_reminders),
            }

        except Exception as e:
            logger.error(f"Error listando recordatorios: {e}")
            return {
                "success": False,
                "error": f"Error listando recordatorios: {str(e)}",
            }


class ReminderCancelTool(Tool):
    """Herramienta para cancelar recordatorios."""

    @property
    def name(self) -> str:
        return "reminder_cancel"

    @property
    def description(self) -> str:
        return (
            "Cancela un recordatorio programado. "
            "Úsala cuando el usuario quiera cancelar un recordatorio existente."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="reminder_id",
                type="string",
                description="ID del recordatorio a cancelar",
                required=True,
            )
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Cancela un recordatorio.

        Args:
            reminder_id: ID del recordatorio

        Returns:
            Dict con el resultado de la operación
        """
        reminder_id = kwargs.get("reminder_id")

        try:
            scheduler = await get_reminder_scheduler()
            success = scheduler.cancel_reminder(reminder_id)

            if success:
                return {
                    "success": True,
                    "message": f"Recordatorio {reminder_id} cancelado exitosamente",
                }
            else:
                return {
                    "success": False,
                    "error": f"No se encontró el recordatorio {reminder_id}",
                }

        except Exception as e:
            logger.error(f"Error cancelando recordatorio: {e}")
            return {
                "success": False,
                "error": f"Error cancelando recordatorio: {str(e)}",
            }
