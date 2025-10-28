"""Sistema de recordatorios programados usando APScheduler."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from .notifications import NotificationManager
from .database import TaskDatabase

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Gestor de recordatorios programados."""

    def __init__(
        self,
        notification_manager: Optional[NotificationManager] = None,
        task_db: Optional[TaskDatabase] = None,
    ):
        """
        Inicializa el scheduler de recordatorios.

        Args:
            notification_manager: Gestor de notificaciones
            task_db: Base de datos de tareas
        """
        self.scheduler = AsyncIOScheduler()
        self.notification_manager = notification_manager or NotificationManager()
        self.task_db = task_db or TaskDatabase()
        self._initialized = False

        logger.info("ReminderScheduler inicializado")

    async def start(self):
        """Inicia el scheduler."""
        if not self._initialized:
            await self.task_db.initialize()
            self._initialized = True

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler iniciado")

            # Programar tareas recurrentes
            await self._schedule_daily_summary()
            await self._schedule_event_reminders()

    def stop(self):
        """Detiene el scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler detenido")

    async def schedule_reminder(
        self,
        reminder_id: str,
        title: str,
        message: str,
        trigger_time: datetime,
        priority: str = "normal",
    ) -> bool:
        """
        Programa un recordatorio único.

        Args:
            reminder_id: ID único del recordatorio
            title: Título del recordatorio
            message: Mensaje del recordatorio
            trigger_time: Cuándo disparar el recordatorio
            priority: Prioridad de la notificación

        Returns:
            True si se programó exitosamente
        """
        try:
            # Validar que el tiempo sea futuro
            if trigger_time <= datetime.now():
                logger.warning(f"Tiempo de recordatorio {trigger_time} está en el pasado")
                return False

            # Programar job
            self.scheduler.add_job(
                func=self._send_reminder,
                trigger=DateTrigger(run_date=trigger_time),
                args=[title, message, priority],
                id=reminder_id,
                replace_existing=True,
            )

            logger.info(f"Recordatorio programado: {reminder_id} para {trigger_time}")
            return True

        except Exception as e:
            logger.error(f"Error programando recordatorio: {e}")
            return False

    async def schedule_task_reminder(
        self, task_id: str, task_title: str, remind_at: datetime
    ) -> bool:
        """
        Programa un recordatorio para una tarea.

        Args:
            task_id: ID de la tarea
            task_title: Título de la tarea
            remind_at: Cuándo recordar

        Returns:
            True si se programó exitosamente
        """
        return await self.schedule_reminder(
            reminder_id=f"task_{task_id}",
            title=f"Recordatorio: {task_title}",
            message=f"No olvides completar la tarea: {task_title}",
            trigger_time=remind_at,
            priority="normal",
        )

    async def schedule_event_reminder(
        self,
        event_id: str,
        event_title: str,
        event_time: datetime,
        minutes_before: int = 15,
    ) -> bool:
        """
        Programa un recordatorio para un evento.

        Args:
            event_id: ID del evento
            event_title: Título del evento
            event_time: Hora del evento
            minutes_before: Cuántos minutos antes recordar

        Returns:
            True si se programó exitosamente
        """
        remind_at = event_time - timedelta(minutes=minutes_before)

        return await self.schedule_reminder(
            reminder_id=f"event_{event_id}",
            title=f"Próximo evento: {event_title}",
            message=f"Comienza en {minutes_before} minutos a las {event_time.strftime('%H:%M')}",
            trigger_time=remind_at,
            priority="normal",
        )

    def cancel_reminder(self, reminder_id: str) -> bool:
        """
        Cancela un recordatorio programado.

        Args:
            reminder_id: ID del recordatorio a cancelar

        Returns:
            True si se canceló exitosamente
        """
        try:
            self.scheduler.remove_job(reminder_id)
            logger.info(f"Recordatorio cancelado: {reminder_id}")
            return True
        except Exception as e:
            logger.warning(f"No se pudo cancelar recordatorio {reminder_id}: {e}")
            return False

    async def _send_reminder(self, title: str, message: str, priority: str = "normal"):
        """
        Envía una notificación de recordatorio.

        Args:
            title: Título del recordatorio
            message: Mensaje del recordatorio
            priority: Prioridad de la notificación
        """
        from .notifications import NotificationPriority

        priority_map = {
            "low": NotificationPriority.LOW,
            "normal": NotificationPriority.NORMAL,
            "critical": NotificationPriority.CRITICAL,
        }

        notif_priority = priority_map.get(priority, NotificationPriority.NORMAL)

        self.notification_manager.send(
            title=title,
            message=message,
            priority=notif_priority,
            icon="dialog-information",
            timeout=10000,
        )

        logger.info(f"Recordatorio enviado: {title}")

    async def _schedule_daily_summary(self):
        """Programa el resumen diario de tareas."""
        try:
            # Resumen a las 8:00 AM todos los días
            self.scheduler.add_job(
                func=self._send_daily_summary,
                trigger=CronTrigger(hour=8, minute=0),
                id="daily_summary",
                replace_existing=True,
            )
            logger.info("Resumen diario programado para las 8:00 AM")

        except Exception as e:
            logger.error(f"Error programando resumen diario: {e}")

    async def _send_daily_summary(self):
        """Envía el resumen diario de tareas y eventos."""
        try:
            # Obtener tareas pendientes
            tasks = await self.task_db.list_tasks(
                user_id="default", filter_type="pending", limit=100
            )

            # TODO: Obtener eventos del día desde Calcurse
            events_count = 0

            # Enviar notificación
            self.notification_manager.send_daily_summary(
                tasks_count=len(tasks), events_count=events_count
            )

            logger.info(f"Resumen diario enviado: {len(tasks)} tareas, {events_count} eventos")

        except Exception as e:
            logger.error(f"Error enviando resumen diario: {e}")

    async def _schedule_event_reminders(self):
        """Programa recordatorios para eventos próximos."""
        try:
            # Revisar eventos cada hora
            self.scheduler.add_job(
                func=self._check_upcoming_events,
                trigger=IntervalTrigger(hours=1),
                id="check_events",
                replace_existing=True,
            )
            logger.info("Revisión de eventos programada cada hora")

        except Exception as e:
            logger.error(f"Error programando revisión de eventos: {e}")

    async def _check_upcoming_events(self):
        """Revisa eventos próximos y programa recordatorios."""
        try:
            # TODO: Obtener eventos del día desde Calcurse
            # Por ahora, solo log
            logger.debug("Revisando eventos próximos...")

        except Exception as e:
            logger.error(f"Error revisando eventos: {e}")

    def list_scheduled_reminders(self) -> list:
        """
        Lista todos los recordatorios programados.

        Returns:
            Lista de jobs programados
        """
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]
