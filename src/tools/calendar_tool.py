"""Herramienta para gestión de calendario."""

import logging
from datetime import datetime
from typing import Dict, Any, List
from .base import Tool, ToolParameter
from ..integrations import calcurse

logger = logging.getLogger(__name__)


class CalendarTool(Tool):
    """Herramienta para gestionar eventos en el calendario."""

    @property
    def name(self) -> str:
        return "calendar_create_event"

    @property
    def description(self) -> str:
        return (
            "Crea un evento en el calendario del usuario. "
            "Úsala cuando el usuario quiera agendar algo, programar una reunión, "
            "o reservar tiempo para una actividad."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="title", type="string", description="Título o nombre del evento", required=True
            ),
            ToolParameter(
                name="start_time",
                type="string",
                description=(
                    "Hora de inicio en formato ISO 8601 (ej: '2025-10-15T10:00:00'). "
                    "Si el usuario dice 'mañana a las 3pm', calcula la fecha correcta."
                ),
                required=True,
            ),
            ToolParameter(
                name="duration_minutes",
                type="number",
                description="Duración del evento en minutos (por defecto 60)",
                required=False,
            ),
            ToolParameter(
                name="description",
                type="string",
                description="Descripción o notas adicionales del evento",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Crea un evento en el calendario.

        Args:
            title: Título del evento
            start_time: Hora de inicio (ISO 8601)
            duration_minutes: Duración en minutos
            description: Descripción del evento

        Returns:
            Dict con el resultado de la operación
        """
        title = kwargs.get("title")
        start_time_str = kwargs.get("start_time")
        duration_minutes = kwargs.get("duration_minutes", 60)
        kwargs.get("description", "")

        # Parsear la fecha
        start_time = datetime.fromisoformat(start_time_str)
        date = start_time.strftime("%m/%d/%Y")
        start_t = start_time.strftime("%H:%M")

        from datetime import timedelta

        end_dt = start_time + timedelta(minutes=duration_minutes)
        end_t = end_dt.strftime("%H:%M")
        c = calcurse.Calcurse()
        return c.saveEvent(title, date, start_t, end_t)


class CalendarGetAgendaTool(Tool):
    """Herramienta para obtener la agenda del usuario."""

    @property
    def name(self) -> str:
        return "calendar_get_agenda"

    @property
    def description(self) -> str:
        return (
            "Obtiene los eventos del calendario del usuario. "
            "Úsala cuando el usuario pregunte qué tiene agendado, "
            "qué eventos tiene hoy, mañana o esta semana."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="days",
                type="number",
                description="Número de días a consultar (por defecto 1 = solo hoy)",
                required=False,
            ),
            ToolParameter(
                name="start_date",
                type="string",
                description="Fecha de inicio en formato ISO 8601 (por defecto hoy)",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Obtiene la agenda del usuario.

        Args:
            days: Número de días a consultar
            start_date: Fecha de inicio

        Returns:
            Dict con los eventos encontrados
        """
        days = kwargs.get("days", 1)
        kwargs.get("start_date")

        try:
            # Obtener agenda desde calcurse
            c = calcurse.Calcurse()
            result = c.getAgenda(days=days)

            if result.get("success"):
                return {
                    "success": True,
                    "message": result.get("message", f"Agenda para los próximos {days} días"),
                    "events": result.get("events", []),
                    "tasks": result.get("tasks", []),
                    "raw_output": result.get("raw_output", ""),
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error obteniendo agenda: {e}")
            return {"success": False, "error": f"Error obteniendo agenda: {str(e)}"}
