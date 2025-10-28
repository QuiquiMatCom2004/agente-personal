"""Sistema de persistencia con SQLite para tareas y eventos."""

import logging
import aiosqlite
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskDatabase:
    """Gestor de base de datos para tareas del agente."""

    def __init__(self, db_path: str = "data/tasks.db"):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        # Asegurar que el directorio existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Inicializa las tablas de la base de datos."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    due_date TEXT,
                    tags TEXT,
                    completed BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(id)
                )
            """
            )
            await db.commit()
            logger.info(f"Base de datos inicializada: {self.db_path}")

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
        """
        Crea una nueva tarea en la base de datos.

        Args:
            task_id: ID único de la tarea
            user_id: ID del usuario
            title: Título de la tarea
            description: Descripción
            priority: Prioridad (urgent, high, medium, low)
            due_date: Fecha límite (ISO format)
            tags: Lista de etiquetas

        Returns:
            Dict con la tarea creada
        """
        try:
            tags_str = ",".join(tags) if tags else ""
            created_at = datetime.now().isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO tasks
                    (id, user_id, title, description, priority, due_date, tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        task_id,
                        user_id,
                        title,
                        description,
                        priority,
                        due_date,
                        tags_str,
                        created_at,
                    ),
                )
                await db.commit()

            logger.info(f"Tarea creada en BD: {task_id} - {title}")

            return {
                "id": task_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "tags": tags or [],
                "completed": False,
                "created_at": created_at,
            }

        except Exception as e:
            logger.error(f"Error creando tarea en BD: {e}")
            raise

    async def list_tasks(
        self, user_id: str, filter_type: str = "pending", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lista las tareas de un usuario.

        Args:
            user_id: ID del usuario
            filter_type: Filtro (all, pending, completed, urgent)
            limit: Límite de resultados

        Returns:
            Lista de tareas
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Construir query según filtro
                if filter_type == "completed":
                    query = "SELECT * FROM tasks WHERE user_id = ? AND completed = 1"
                elif filter_type == "pending":
                    query = "SELECT * FROM tasks WHERE user_id = ? AND completed = 0"
                elif filter_type == "urgent":
                    query = """
                        SELECT * FROM tasks
                        WHERE user_id = ? AND completed = 0
                        AND priority IN ('urgent', 'high')
                    """
                else:  # all
                    query = "SELECT * FROM tasks WHERE user_id = ?"

                query += " ORDER BY created_at DESC LIMIT ?"

                async with db.execute(query, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()

                    tasks = []
                    for row in rows:
                        task = dict(row)
                        # Convertir tags de string a lista
                        if task.get("tags"):
                            task["tags"] = task["tags"].split(",")
                        else:
                            task["tags"] = []
                        # Convertir completed a bool
                        task["completed"] = bool(task["completed"])
                        tasks.append(task)

                    logger.info(f"Listadas {len(tasks)} tareas para usuario {user_id}")
                    return tasks

        except Exception as e:
            logger.error(f"Error listando tareas: {e}")
            return []

    async def complete_task(self, task_id: str, user_id: str) -> bool:
        """
        Marca una tarea como completada.

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario

        Returns:
            True si se completó exitosamente
        """
        try:
            completed_at = datetime.now().isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    UPDATE tasks
                    SET completed = 1, completed_at = ?
                    WHERE id = ? AND user_id = ?
                """,
                    (completed_at, task_id, user_id),
                )
                await db.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Tarea completada: {task_id}")
                    return True
                else:
                    logger.warning(f"Tarea no encontrada: {task_id}")
                    return False

        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
            return False

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Elimina una tarea.

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario

        Returns:
            True si se eliminó exitosamente
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
                )
                await db.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Tarea eliminada: {task_id}")
                    return True
                else:
                    logger.warning(f"Tarea no encontrada: {task_id}")
                    return False

        except Exception as e:
            logger.error(f"Error eliminando tarea: {e}")
            return False

    async def get_task(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una tarea específica.

        Args:
            task_id: ID de la tarea
            user_id: ID del usuario

        Returns:
            Dict con la tarea o None si no existe
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                async with db.execute(
                    "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
                ) as cursor:
                    row = await cursor.fetchone()

                    if row:
                        task = dict(row)
                        if task.get("tags"):
                            task["tags"] = task["tags"].split(",")
                        else:
                            task["tags"] = []
                        task["completed"] = bool(task["completed"])
                        return task

                    return None

        except Exception as e:
            logger.error(f"Error obteniendo tarea: {e}")
            return None
