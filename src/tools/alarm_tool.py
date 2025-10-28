"""Herramienta para crear alarmas con sonido."""

import logging
from datetime import datetime
from typing import Dict, Any, List
from .base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class AlarmCreateTool(Tool):
    """Herramienta para crear alarmas con sonido y notificación persistente."""

    @property
    def name(self) -> str:
        return "alarm_create"

    @property
    def description(self) -> str:
        return (
            "Crea una ALARMA con sonido y notificación persistente. "
            "Úsala cuando el usuario necesite ser alertado de algo MUY IMPORTANTE. "
            "La alarma sonará y mostrará una notificación que NO se cierra automáticamente. "
            "Ejemplo: 'ponme una alarma para despertar en 30 minutos' o "
            "'alarma para la reunión importante mañana a las 9am'"
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="title",
                type="string",
                description="Título de la alarma (breve y claro)",
                required=True,
            ),
            ToolParameter(
                name="message",
                type="string",
                description="Mensaje detallado de la alarma",
                required=True,
            ),
            ToolParameter(
                name="alarm_time",
                type="string",
                description="Hora de la alarma en formato ISO 8601 (ej: '2025-10-28T09:00:00')",
                required=True,
            ),
            ToolParameter(
                name="sound_type",
                type="string",
                description="Tipo de sonido de la alarma",
                required=False,
                enum=["alarm", "bell", "gentle", "beep"],
            ),
            ToolParameter(
                name="repeat_sound",
                type="number",
                description="Cuántas veces repetir el sonido (por defecto 3)",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Programa una alarma con sonido.

        Args:
            title: Título de la alarma
            message: Mensaje de la alarma
            alarm_time: Cuándo sonar (ISO 8601)
            sound_type: Tipo de sonido (alarm, bell, gentle, beep)
            repeat_sound: Cuántas veces repetir

        Returns:
            Dict con el resultado de la operación
        """
        from ..integrations.alarm import AlarmManager, AlarmSound

        title = kwargs.get("title")
        message = kwargs.get("message")
        alarm_time_str = kwargs.get("alarm_time")
        sound_type = kwargs.get("sound_type", "alarm")
        repeat_sound = kwargs.get("repeat_sound", 3)

        try:
            # Parsear fecha
            alarm_time = datetime.fromisoformat(alarm_time_str)

            # Validar que sea futuro
            if alarm_time <= datetime.now():
                return {
                    "success": False,
                    "error": "La hora de la alarma debe ser en el futuro",
                }

            # Generar ID único
            alarm_id = f"alarm_{int(datetime.now().timestamp())}"

            # Obtener scheduler
            from .reminder_tool import get_reminder_scheduler

            scheduler = await get_reminder_scheduler()

            # Mapear sound type
            sound_map = {
                "alarm": AlarmSound.ALARM,
                "bell": AlarmSound.BELL,
                "gentle": AlarmSound.GENTLE,
                "beep": AlarmSound.BEEP,
            }
            sound = sound_map.get(sound_type, AlarmSound.ALARM)

            # Crear función de alarma
            alarm_manager = AlarmManager()

            async def trigger_alarm():
                alarm_manager.trigger_alarm(
                    title=title,
                    message=message,
                    sound=sound,
                    repeat_sound=int(repeat_sound),
                    persistent=True,
                )

            # Programar la alarma
            from apscheduler.triggers.date import DateTrigger

            scheduler.scheduler.add_job(
                func=trigger_alarm,
                trigger=DateTrigger(run_date=alarm_time),
                id=alarm_id,
                replace_existing=True,
            )

            # Calcular tiempo hasta la alarma
            time_until = alarm_time - datetime.now()
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
                "message": f"🚨 Alarma '{title}' programada para {alarm_time.strftime('%d/%m/%Y a las %H:%M')} (en {time_desc})",
                "alarm_id": alarm_id,
                "alarm_time": alarm_time.isoformat(),
                "sound_type": sound_type,
            }

        except ValueError as e:
            return {
                "success": False,
                "error": f"Formato de fecha inválido: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Error programando alarma: {e}")
            return {
                "success": False,
                "error": f"Error programando alarma: {str(e)}",
            }
