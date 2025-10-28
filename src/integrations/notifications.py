"""Sistema de notificaciones usando dunst (notificaciones de escritorio en Linux)."""

import subprocess
import logging
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Niveles de prioridad para notificaciones."""

    LOW = "low"
    NORMAL = "normal"
    CRITICAL = "critical"


class NotificationManager:
    """Gestor de notificaciones de escritorio usando dunst/notify-send."""

    def __init__(self, app_name: str = "Agente Personal", enable_sound: bool = True):
        """
        Inicializa el gestor de notificaciones.

        Args:
            app_name: Nombre de la aplicación para las notificaciones
            enable_sound: Si se debe reproducir sonido con las notificaciones
        """
        self.app_name = app_name
        self.enable_sound = enable_sound
        self._check_availability()

    def _check_availability(self):
        """Verifica que notify-send esté disponible en el sistema."""
        try:
            subprocess.run(
                ["which", "notify-send"],
                capture_output=True,
                check=True,
            )
            logger.info("Sistema de notificaciones disponible (notify-send)")
        except subprocess.CalledProcessError:
            logger.warning(
                "notify-send no está disponible. "
                "Las notificaciones de escritorio no funcionarán."
            )

    def send(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        timeout: int = 5000,
        icon: Optional[str] = None,
    ) -> bool:
        """
        Envía una notificación de escritorio.

        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            priority: Prioridad (low, normal, critical)
            timeout: Tiempo de visualización en milisegundos (0 = no expira)
            icon: Nombre o ruta del icono a mostrar

        Returns:
            True si la notificación se envió exitosamente
        """
        try:
            cmd = [
                "notify-send",
                title,
                message,
                "--app-name",
                self.app_name,
                "--urgency",
                priority.value,
                "--expire-time",
                str(timeout),
            ]

            # Agregar icono si se especificó
            if icon:
                cmd.extend(["--icon", icon])

            # Deshabilitar sonido si es necesario
            if not self.enable_sound:
                cmd.append("--hint=string:sound-name:none")

            subprocess.run(cmd, check=True, capture_output=True)

            logger.info(f"Notificación enviada: {title}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error enviando notificación: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("notify-send no está instalado")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando notificación: {e}")
            return False

    def send_task_reminder(self, task_title: str, priority: str = "medium") -> bool:
        """
        Envía un recordatorio de tarea.

        Args:
            task_title: Título de la tarea
            priority: Prioridad de la tarea (urgent, high, medium, low)

        Returns:
            True si la notificación se envió exitosamente
        """
        # Mapear prioridad de tarea a prioridad de notificación
        priority_map = {
            "urgent": NotificationPriority.CRITICAL,
            "high": NotificationPriority.NORMAL,
            "medium": NotificationPriority.NORMAL,
            "low": NotificationPriority.LOW,
        }

        notif_priority = priority_map.get(priority, NotificationPriority.NORMAL)

        # Seleccionar icono según prioridad
        icon = "dialog-warning" if priority in ["urgent", "high"] else "dialog-information"

        return self.send(
            title=f"Recordatorio: {task_title}",
            message=f"Tarea pendiente con prioridad {priority}",
            priority=notif_priority,
            icon=icon,
            timeout=10000,  # 10 segundos
        )

    def send_event_reminder(
        self, event_title: str, start_time: str, minutes_before: int = 15
    ) -> bool:
        """
        Envía un recordatorio de evento.

        Args:
            event_title: Título del evento
            start_time: Hora de inicio del evento
            minutes_before: Minutos de anticipación

        Returns:
            True si la notificación se envió exitosamente
        """
        return self.send(
            title=f"Próximo evento: {event_title}",
            message=f"Comienza en {minutes_before} minutos ({start_time})",
            priority=NotificationPriority.NORMAL,
            icon="appointment-soon",
            timeout=15000,  # 15 segundos
        )

    def send_success(self, message: str) -> bool:
        """
        Envía una notificación de éxito.

        Args:
            message: Mensaje a mostrar

        Returns:
            True si la notificación se envió exitosamente
        """
        return self.send(
            title="✓ Éxito",
            message=message,
            priority=NotificationPriority.LOW,
            icon="dialog-positive",
            timeout=3000,
        )

    def send_error(self, message: str) -> bool:
        """
        Envía una notificación de error.

        Args:
            message: Mensaje de error a mostrar

        Returns:
            True si la notificación se envió exitosamente
        """
        return self.send(
            title="✗ Error",
            message=message,
            priority=NotificationPriority.CRITICAL,
            icon="dialog-error",
            timeout=0,  # No expira automáticamente
        )

    def send_daily_summary(self, tasks_count: int, events_count: int) -> bool:
        """
        Envía un resumen diario.

        Args:
            tasks_count: Número de tareas pendientes
            events_count: Número de eventos del día

        Returns:
            True si la notificación se envió exitosamente
        """
        message = f"Tareas pendientes: {tasks_count}\nEventos hoy: {events_count}"

        return self.send(
            title="Resumen del día",
            message=message,
            priority=NotificationPriority.NORMAL,
            icon="dialog-information",
            timeout=10000,
        )
