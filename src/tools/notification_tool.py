"""Herramienta para enviar notificaciones de escritorio."""

import logging
from typing import Dict, Any, List
from .base import Tool, ToolParameter
from ..integrations import NotificationManager, NotificationPriority

logger = logging.getLogger(__name__)

# Instancia global del gestor de notificaciones
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """Obtiene o crea la instancia del gestor de notificaciones."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


class NotificationSendTool(Tool):
    """Herramienta para enviar notificaciones de escritorio."""

    @property
    def name(self) -> str:
        return "notification_send"

    @property
    def description(self) -> str:
        return (
            "Envía una notificación de escritorio al usuario. "
            "Úsala para recordatorios importantes, alertas o confirmaciones de acciones."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="title",
                type="string",
                description="Título de la notificación",
                required=True,
            ),
            ToolParameter(
                name="message",
                type="string",
                description="Mensaje de la notificación",
                required=True,
            ),
            ToolParameter(
                name="priority",
                type="string",
                description="Prioridad de la notificación",
                required=False,
                enum=["low", "normal", "critical"],
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Envía una notificación de escritorio.

        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            priority: Prioridad (low, normal, critical)

        Returns:
            Dict con el resultado de la operación
        """
        title = kwargs.get("title")
        message = kwargs.get("message")
        priority_str = kwargs.get("priority", "normal")

        try:
            # Convertir prioridad de string a enum
            priority_map = {
                "low": NotificationPriority.LOW,
                "normal": NotificationPriority.NORMAL,
                "critical": NotificationPriority.CRITICAL,
            }
            priority = priority_map.get(priority_str, NotificationPriority.NORMAL)

            # Enviar notificación
            nm = get_notification_manager()
            success = nm.send(title=title, message=message, priority=priority)

            if success:
                return {
                    "success": True,
                    "message": f"Notificación enviada: {title}",
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo enviar la notificación",
                }

        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return {
                "success": False,
                "error": f"Error enviando notificación: {str(e)}",
            }
