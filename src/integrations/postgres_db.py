"""
Base de datos PostgreSQL para sincronización entre Railway y PC local.

Reemplaza SQLite para permitir que múltiples instancias (Railway + PC)
compartan la misma base de datos.
"""

import asyncpg
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PostgresDatabase:
    """
    Cliente de PostgreSQL para tareas, eventos y recordatorios.

    Permite sincronización entre:
    - Bot en Railway (crea tareas/eventos)
    - PC local (ejecuta alarmas/notificaciones)
    """

    def __init__(self, database_url: str):
        """
        Inicializa el cliente de PostgreSQL.

        Args:
            database_url: Connection string de PostgreSQL
                Ejemplo: postgresql://user:pass@host:5432/dbname
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        logger.info("PostgresDatabase inicializado")

    async def connect(self):
        """Crea el pool de conexiones."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )
            logger.info("Pool de conexiones PostgreSQL creado")
            await self._create_tables()
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise

    async def disconnect(self):
        """Cierra el pool de conexiones."""
        if self.pool:
            await self.pool.close()
            logger.info("Pool de conexiones PostgreSQL cerrado")

    async def _create_tables(self):
        """Crea las tablas si no existen."""
        async with self.pool.acquire() as conn:
            # Tabla de tareas
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT DEFAULT 'medium',
                    due_date TEXT,
                    tags TEXT DEFAULT '',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
                """
            )

            # Tabla de eventos (calendario)
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )

            # Tabla de recordatorios/alarmas
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    trigger_time TIMESTAMP NOT NULL,
                    reminder_type TEXT DEFAULT 'notification',
                    priority TEXT DEFAULT 'normal',
                    sound_type TEXT,
                    executed BOOLEAN DEFAULT FALSE,
                    executed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )

            # Índices para mejor performance
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reminders_executed ON reminders(executed)"
            )

            logger.info("Tablas de PostgreSQL verificadas/creadas")

    # ==================== TAREAS ====================

    async def create_task(
        self,
        task_id: str,
        user_id: str,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Crea una nueva tarea."""
        try:
            tags_str = ",".join(tags) if tags else ""
            created_at = datetime.now()

            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO tasks (id, user_id, title, description, priority, due_date, tags, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    task_id,
                    user_id,
                    title,
                    description,
                    priority,
                    due_date,
                    tags_str,
                    created_at,
                )

            logger.info(f"Tarea creada en PostgreSQL: {task_id}")
            return {
                "id": task_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "tags": tags or [],
                "completed": False,
                "created_at": created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            raise

    async def list_tasks(
        self, user_id: str, filter_type: str = "pending"
    ) -> List[Dict[str, Any]]:
        """Lista tareas con filtros."""
        try:
            async with self.pool.acquire() as conn:
                if filter_type == "pending":
                    rows = await conn.fetch(
                        "SELECT * FROM tasks WHERE user_id = $1 AND completed = FALSE ORDER BY created_at DESC",
                        user_id,
                    )
                elif filter_type == "completed":
                    rows = await conn.fetch(
                        "SELECT * FROM tasks WHERE user_id = $1 AND completed = TRUE ORDER BY completed_at DESC",
                        user_id,
                    )
                elif filter_type == "urgent":
                    rows = await conn.fetch(
                        "SELECT * FROM tasks WHERE user_id = $1 AND priority = 'urgent' AND completed = FALSE ORDER BY created_at DESC",
                        user_id,
                    )
                else:  # all
                    rows = await conn.fetch(
                        "SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC",
                        user_id,
                    )

            tasks = []
            for row in rows:
                tasks.append(
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "title": row["title"],
                        "description": row["description"],
                        "priority": row["priority"],
                        "due_date": row["due_date"],
                        "tags": row["tags"].split(",") if row["tags"] else [],
                        "completed": row["completed"],
                        "created_at": row["created_at"].isoformat()
                        if row["created_at"]
                        else None,
                        "completed_at": row["completed_at"].isoformat()
                        if row["completed_at"]
                        else None,
                    }
                )

            logger.info(f"Tareas listadas: {len(tasks)} ({filter_type})")
            return tasks
        except Exception as e:
            logger.error(f"Error listando tareas: {e}")
            return []

    async def complete_task(self, task_id: str, user_id: str) -> bool:
        """Marca una tarea como completada."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "UPDATE tasks SET completed = TRUE, completed_at = NOW() WHERE id = $1 AND user_id = $2",
                    task_id,
                    user_id,
                )

            success = result != "UPDATE 0"
            if success:
                logger.info(f"Tarea completada: {task_id}")
            return success
        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
            return False

    # ==================== EVENTOS ====================

    async def create_event(
        self,
        event_id: str,
        user_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
    ) -> Dict[str, Any]:
        """Crea un evento de calendario."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO events (id, user_id, title, description, start_time, end_time)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    event_id,
                    user_id,
                    title,
                    description,
                    start_time,
                    end_time,
                )

            logger.info(f"Evento creado en PostgreSQL: {event_id}")
            return {
                "id": event_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creando evento: {e}")
            raise

    async def list_events(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Lista eventos en un rango de fechas."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM events
                    WHERE user_id = $1 AND start_time >= $2 AND start_time <= $3
                    ORDER BY start_time ASC
                    """,
                    user_id,
                    start_date,
                    end_date,
                )

            events = []
            for row in rows:
                events.append(
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "title": row["title"],
                        "description": row["description"],
                        "start_time": row["start_time"].isoformat(),
                        "end_time": row["end_time"].isoformat(),
                    }
                )

            logger.info(f"Eventos listados: {len(events)}")
            return events
        except Exception as e:
            logger.error(f"Error listando eventos: {e}")
            return []

    # ==================== RECORDATORIOS/ALARMAS ====================

    async def create_reminder(
        self,
        reminder_id: str,
        user_id: str,
        title: str,
        message: str,
        trigger_time: datetime,
        reminder_type: str = "notification",
        priority: str = "normal",
        sound_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crea un recordatorio o alarma."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO reminders
                    (id, user_id, title, message, trigger_time, reminder_type, priority, sound_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    reminder_id,
                    user_id,
                    title,
                    message,
                    trigger_time,
                    reminder_type,
                    priority,
                    sound_type,
                )

            logger.info(f"Recordatorio creado en PostgreSQL: {reminder_id}")
            return {
                "id": reminder_id,
                "user_id": user_id,
                "title": title,
                "message": message,
                "trigger_time": trigger_time.isoformat(),
                "reminder_type": reminder_type,
                "priority": priority,
                "sound_type": sound_type,
                "executed": False,
            }
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            raise

    async def get_pending_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene recordatorios pendientes de ejecutar."""
        try:
            now = datetime.now()
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM reminders
                    WHERE user_id = $1 AND executed = FALSE AND trigger_time <= $2
                    ORDER BY trigger_time ASC
                    """,
                    user_id,
                    now,
                )

            reminders = []
            for row in rows:
                reminders.append(
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "title": row["title"],
                        "message": row["message"],
                        "trigger_time": row["trigger_time"].isoformat(),
                        "reminder_type": row["reminder_type"],
                        "priority": row["priority"],
                        "sound_type": row["sound_type"],
                    }
                )

            if reminders:
                logger.info(f"Recordatorios pendientes encontrados: {len(reminders)}")
            return reminders
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios pendientes: {e}")
            return []

    async def mark_reminder_executed(self, reminder_id: str) -> bool:
        """Marca un recordatorio como ejecutado."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "UPDATE reminders SET executed = TRUE, executed_at = NOW() WHERE id = $1",
                    reminder_id,
                )

            success = result != "UPDATE 0"
            if success:
                logger.info(f"Recordatorio marcado como ejecutado: {reminder_id}")
            return success
        except Exception as e:
            logger.error(f"Error marcando recordatorio: {e}")
            return False

    async def list_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Lista todos los recordatorios del usuario."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM reminders
                    WHERE user_id = $1 AND executed = FALSE
                    ORDER BY trigger_time ASC
                    """,
                    user_id,
                )

            reminders = []
            for row in rows:
                reminders.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "message": row["message"],
                        "trigger_time": row["trigger_time"].isoformat(),
                        "reminder_type": row["reminder_type"],
                        "priority": row["priority"],
                    }
                )

            return reminders
        except Exception as e:
            logger.error(f"Error listando recordatorios: {e}")
            return []

    async def cancel_reminder(self, reminder_id: str, user_id: str) -> bool:
        """Cancela (elimina) un recordatorio."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM reminders WHERE id = $1 AND user_id = $2",
                    reminder_id,
                    user_id,
                )

            success = result != "DELETE 0"
            if success:
                logger.info(f"Recordatorio cancelado: {reminder_id}")
            return success
        except Exception as e:
            logger.error(f"Error cancelando recordatorio: {e}")
            return False
