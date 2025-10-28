#!/usr/bin/env python3
"""Script de prueba para verificar las integraciones del agente."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.calcurse import Calcurse
from src.integrations.database import TaskDatabase
from src.integrations.notifications import NotificationManager
from datetime import datetime, timedelta


async def test_calcurse():
    """Prueba la integración con Calcurse."""
    print("=== Probando integración con Calcurse ===")

    c = Calcurse()

    # Probar creación de evento
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%m/%d/%Y")
    result = c.saveEvent(
        title="Reunión de prueba",
        date=date_str,
        start_time="10:00",
        end_time="11:00",
    )
    print(f"Crear evento: {result}")

    # Probar creación de tarea
    result = c.saveTask(title="Tarea de prueba", priority=5)
    print(f"Crear tarea: {result}")

    # Obtener agenda
    result = c.getAgenda(days=7)
    print(f"Obtener agenda: {result}")

    print()


async def test_database():
    """Prueba la base de datos de tareas."""
    print("=== Probando base de datos de tareas ===")

    db = TaskDatabase(db_path="data/test_tasks.db")
    await db.initialize()

    # Crear tarea
    task = await db.create_task(
        task_id="test_001",
        user_id="test_user",
        title="Tarea de prueba",
        description="Esta es una tarea de prueba",
        priority="high",
        tags=["prueba", "testing"],
    )
    print(f"Tarea creada: {task}")

    # Listar tareas
    tasks = await db.list_tasks(user_id="test_user", filter_type="pending")
    print(f"Tareas pendientes: {len(tasks)}")

    # Completar tarea
    success = await db.complete_task(task_id="test_001", user_id="test_user")
    print(f"Tarea completada: {success}")

    # Verificar que está completada
    tasks = await db.list_tasks(user_id="test_user", filter_type="completed")
    print(f"Tareas completadas: {len(tasks)}")

    print()


def test_notifications():
    """Prueba el sistema de notificaciones."""
    print("=== Probando sistema de notificaciones ===")

    nm = NotificationManager(app_name="Test Agente")

    # Enviar notificación de prueba
    success = nm.send(
        title="Prueba de notificación",
        message="Si ves esto, las notificaciones funcionan correctamente",
    )
    print(f"Notificación enviada: {success}")

    # Enviar recordatorio de tarea
    success = nm.send_task_reminder(task_title="Tarea importante", priority="high")
    print(f"Recordatorio de tarea enviado: {success}")

    print()


async def main():
    """Ejecuta todas las pruebas."""
    print("Iniciando pruebas de integraciones...\n")

    try:
        await test_calcurse()
        await test_database()
        test_notifications()

        print("✓ Todas las pruebas completadas exitosamente")

    except Exception as e:
        print(f"✗ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
