"""Herramienta para gestión de tareas."""

import logging
from datetime import datetime
from typing import Dict, Any, List
from .base import Tool, ToolParameter
from ..integrations.database import TaskDatabase

logger = logging.getLogger(__name__)

# Instancia global de la base de datos
_task_db = None


async def get_task_db() -> TaskDatabase:
    """Obtiene o crea la instancia de la base de datos de tareas."""
    global _task_db
    if _task_db is None:
        _task_db = TaskDatabase()
        await _task_db.initialize()
    return _task_db


class TaskCreateTool(Tool):
    """Herramienta para crear tareas."""

    @property
    def name(self) -> str:
        return "task_create"

    @property
    def description(self) -> str:
        return (
            "Crea una nueva tarea o recordatorio para el usuario. "
            "Úsala cuando el usuario pida crear una tarea, recordatorio, o algo por hacer."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="title",
                type="string",
                description="Título o nombre de la tarea",
                required=True,
            ),
            ToolParameter(
                name="description",
                type="string",
                description="Descripción detallada de la tarea",
                required=False,
            ),
            ToolParameter(
                name="priority",
                type="string",
                description="Prioridad de la tarea",
                required=False,
                enum=["urgent", "high", "medium", "low"],
            ),
            ToolParameter(
                name="due_date",
                type="string",
                description="Fecha límite en formato ISO 8601 (opcional)",
                required=False,
            ),
            ToolParameter(
                name="tags",
                type="array",
                description="Etiquetas para categorizar la tarea",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Crea una nueva tarea.

        Args:
            title: Título de la tarea
            description: Descripción
            priority: Prioridad (urgent, high, medium, low)
            due_date: Fecha límite
            tags: Lista de etiquetas

        Returns:
            Dict con el resultado de la operación
        """
        title = kwargs.get("title")
        description = kwargs.get("description", "")
        priority = kwargs.get("priority", "medium")
        due_date_str = kwargs.get("due_date")
        tags = kwargs.get("tags", [])
        user_id = kwargs.get("user_id", "default")

        try:
            # Generar ID único
            task_id = f"task_{int(datetime.now().timestamp())}"

            # Guardar en base de datos
            db = await get_task_db()
            task = await db.create_task(
                task_id=task_id,
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date_str,
                tags=tags,
            )

            logger.info(f"Tarea creada: {title} (prioridad: {priority})")

            return {
                "success": True,
                "message": f"Tarea '{title}' creada exitosamente con prioridad {priority}",
                "task": task,
            }

        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            return {"success": False, "error": f"Error creando tarea: {str(e)}"}


class TaskListTool(Tool):
    """Herramienta para listar tareas."""

    @property
    def name(self) -> str:
        return "task_list"

    @property
    def description(self) -> str:
        return (
            "Lista las tareas del usuario. "
            "Úsala cuando el usuario pregunte qué tareas tiene pendientes, "
            "qué debe hacer, o quiera ver sus to-dos."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="filter",
                type="string",
                description="Filtro para las tareas",
                required=False,
                enum=["all", "pending", "completed", "today", "urgent"],
            ),
            ToolParameter(
                name="limit",
                type="number",
                description="Número máximo de tareas a retornar (por defecto 10)",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Lista las tareas del usuario.

        Args:
            filter: Filtro a aplicar (all, pending, completed, today, urgent)
            limit: Límite de resultados

        Returns:
            Dict con las tareas encontradas
        """
        filter_type = kwargs.get("filter", "pending")
        limit = kwargs.get("limit", 10)
        user_id = kwargs.get("user_id", "default")

        try:
            # Obtener tareas desde la base de datos
            db = await get_task_db()
            tasks = await db.list_tasks(user_id=user_id, filter_type=filter_type, limit=limit)

            return {
                "success": True,
                "message": f"Se encontraron {len(tasks)} tareas",
                "tasks": tasks,
                "count": len(tasks),
            }

        except Exception as e:
            logger.error(f"Error listando tareas: {e}")
            return {"success": False, "error": f"Error listando tareas: {str(e)}"}


class TaskCompleteTool(Tool):
    """Herramienta para marcar tareas como completadas."""

    @property
    def name(self) -> str:
        return "task_complete"

    @property
    def description(self) -> str:
        return (
            "Marca una tarea como completada. "
            "Úsala cuando el usuario diga que completó una tarea o quiera marcarla como hecha."
        )

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="task_id",
                type="string",
                description="ID de la tarea a completar",
                required=True,
            )
        ]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Marca una tarea como completada.

        Args:
            task_id: ID de la tarea

        Returns:
            Dict con el resultado de la operación
        """
        task_id = kwargs.get("task_id")
        user_id = kwargs.get("user_id", "default")

        try:
            # Completar tarea en la base de datos
            db = await get_task_db()
            success = await db.complete_task(task_id=task_id, user_id=user_id)

            if success:
                return {
                    "success": True,
                    "message": f"Tarea {task_id} marcada como completada",
                }
            else:
                return {
                    "success": False,
                    "error": f"Tarea {task_id} no encontrada o ya completada",
                }

        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
            return {"success": False, "error": f"Error completando tarea: {str(e)}"}
