#!/usr/bin/env python3
"""
Local Listener - Ejecuta alarmas y notificaciones en PC local.

Este script:
1. Se conecta a PostgreSQL compartido
2. Monitorea recordatorios/alarmas pendientes cada 30 segundos
3. Ejecuta alarmas con sonido y notificaciones desktop
4. Sincroniza con Calcurse local
5. Marca como ejecutados en la base de datos

Uso:
    uv run python scripts/local_listener.py
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.postgres_db import PostgresDatabase
from src.integrations.notifications import NotificationManager, NotificationPriority
from src.integrations.alarm import AlarmManager, AlarmSound
from src.integrations.calcurse import Calcurse
from src.utils.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LocalListener:
    """
    Listener que ejecuta alarmas y notificaciones en PC local.

    Se conecta a PostgreSQL y ejecuta acciones pendientes que requieren
    hardware local (sonido, notificaciones desktop, Calcurse).
    """

    def __init__(self, database_url: str, user_id: str = "default"):
        """
        Inicializa el listener.

        Args:
            database_url: Connection string de PostgreSQL
            user_id: ID del usuario a monitorear
        """
        self.db = PostgresDatabase(database_url)
        self.user_id = user_id
        self.notifications = NotificationManager()
        self.alarm_manager = AlarmManager()
        self.calcurse = Calcurse()
        self.running = False

        logger.info(f"LocalListener inicializado para user_id: {user_id}")

    async def start(self):
        """Inicia el listener."""
        logger.info("🎧 Iniciando Local Listener...")

        try:
            # Conectar a PostgreSQL
            await self.db.connect()
            logger.info("✅ Conectado a PostgreSQL")

            # Notificar que el listener está activo
            self.notifications.send_notification(
                title="🎧 Local Listener Activo",
                message="Monitoreando alarmas y notificaciones desde PostgreSQL",
                priority=NotificationPriority.LOW,
            )

            self.running = True

            # Loop principal
            while self.running:
                try:
                    await self._check_and_execute_reminders()
                    await asyncio.sleep(30)  # Check cada 30 segundos
                except KeyboardInterrupt:
                    logger.info("Deteniendo listener...")
                    break
                except Exception as e:
                    logger.error(f"Error en loop principal: {e}")
                    await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Error fatal: {e}")
        finally:
            await self.db.disconnect()
            logger.info("Local Listener detenido")

    async def _check_and_execute_reminders(self):
        """Verifica y ejecuta recordatorios pendientes."""
        try:
            # Obtener recordatorios pendientes
            reminders = await self.db.get_pending_reminders(self.user_id)

            if not reminders:
                return

            logger.info(f"📋 {len(reminders)} recordatorios pendientes encontrados")

            for reminder in reminders:
                try:
                    await self._execute_reminder(reminder)
                    # Marcar como ejecutado
                    await self.db.mark_reminder_executed(reminder["id"])
                except Exception as e:
                    logger.error(
                        f"Error ejecutando recordatorio {reminder['id']}: {e}"
                    )

        except Exception as e:
            logger.error(f"Error verificando recordatorios: {e}")

    async def _execute_reminder(self, reminder: dict):
        """Ejecuta un recordatorio/alarma."""
        reminder_type = reminder.get("reminder_type", "notification")
        title = reminder["title"]
        message = reminder["message"]
        priority = reminder.get("priority", "normal")

        logger.info(f"⏰ Ejecutando {reminder_type}: {title}")

        if reminder_type == "alarm":
            # Ejecutar alarma con sonido
            sound_type_str = reminder.get("sound_type", "alarm")
            sound_map = {
                "alarm": AlarmSound.ALARM,
                "bell": AlarmSound.BELL,
                "gentle": AlarmSound.GENTLE,
                "beep": AlarmSound.BEEP,
            }
            sound = sound_map.get(sound_type_str, AlarmSound.ALARM)

            self.alarm_manager.trigger_alarm(
                title=title, message=message, sound=sound, persistent=True
            )

        elif reminder_type == "notification":
            # Enviar notificación desktop
            priority_map = {
                "low": NotificationPriority.LOW,
                "normal": NotificationPriority.NORMAL,
                "high": NotificationPriority.CRITICAL,
                "critical": NotificationPriority.CRITICAL,
            }
            notif_priority = priority_map.get(priority, NotificationPriority.NORMAL)

            self.notifications.send_notification(
                title=title, message=message, priority=notif_priority
            )

        else:
            logger.warning(f"Tipo de recordatorio desconocido: {reminder_type}")

    async def sync_events_to_calcurse(self):
        """
        Sincroniza eventos de PostgreSQL a Calcurse local.

        Obtiene eventos de los próximos 30 días y los agrega a Calcurse.
        """
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)

            events = await self.db.list_events(self.user_id, start_date, end_date)

            for event in events:
                # Convertir a formato Calcurse
                start_time = datetime.fromisoformat(event["start_time"])
                end_time = datetime.fromisoformat(event["end_time"])

                self.calcurse.saveEvent(
                    title=event["title"],
                    date=start_time.strftime("%m/%d/%Y"),
                    start_time=start_time.strftime("%H:%M"),
                    end_time=end_time.strftime("%H:%M"),
                )

            logger.info(f"✅ {len(events)} eventos sincronizados a Calcurse")

        except Exception as e:
            logger.error(f"Error sincronizando eventos a Calcurse: {e}")

    def stop(self):
        """Detiene el listener."""
        self.running = False


async def main():
    """Entry point del listener."""
    settings = get_settings()

    # Verificar que DATABASE_URL esté configurado
    database_url = settings.database_url
    if not database_url or database_url == "sqlite+aiosqlite:///data/db/tasks.db":
        logger.error("❌ DATABASE_URL no configurado en .env")
        logger.error("Configura DATABASE_URL con tu connection string de PostgreSQL")
        logger.error(
            "Ejemplo: DATABASE_URL=postgresql://user:pass@host:5432/dbname"
        )
        return

    # Obtener user_id (por defecto "default", o desde Telegram)
    user_id = "default"

    # Crear y ejecutar listener
    listener = LocalListener(database_url, user_id)

    try:
        await listener.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Listener detenido por usuario")
        listener.stop()


if __name__ == "__main__":
    print("=" * 60)
    print("🎧 LOCAL LISTENER - Agente Personal")
    print("=" * 60)
    print()
    print("Este script monitorea PostgreSQL y ejecuta:")
    print("  • ⏰ Alarmas con sonido")
    print("  • 🔔 Notificaciones desktop")
    print("  • 📅 Sincronización con Calcurse")
    print()
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
