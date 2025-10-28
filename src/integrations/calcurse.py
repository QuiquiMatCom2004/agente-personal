"""Integración con Calcurse para gestión de calendario y tareas."""

import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Calcurse:
    """Cliente para interactuar con calcurse (calendario en terminal)."""

    def __init__(self, calendar_path: Optional[str] = None):
        """
        Inicializa el cliente de Calcurse.

        Args:
            calendar_path: Ruta al directorio de datos de calcurse
        """
        self.calendar_path = calendar_path or str(Path.home() / ".local/share/calcurse")

    def saveEvent(self, title: str, date: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Guarda un evento en calcurse usando formato iCal.

        Args:
            title: Título del evento
            date: Fecha en formato MM/DD/YYYY
            start_time: Hora de inicio en formato HH:MM
            end_time: Hora de fin en formato HH:MM

        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Convertir fecha MM/DD/YYYY a formato iCal YYYYMMDD
            from datetime import datetime

            dt = datetime.strptime(f"{date} {start_time}", "%m/%d/%Y %H:%M")
            dt_end = datetime.strptime(f"{date} {end_time}", "%m/%d/%Y %H:%M")

            dtstart = dt.strftime("%Y%m%dT%H%M%S")
            dtend = dt_end.strftime("%Y%m%dT%H%M%S")

            # Crear evento en formato iCal
            ical_event = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agente Personal//ES
BEGIN:VEVENT
UID:{dtstart}-{title.replace(' ', '-')}@agente
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{title}
END:VEVENT
END:VCALENDAR"""

            # Importar a calcurse
            subprocess.run(
                ["calcurse", "-i", "-", "-q"],
                input=ical_event,
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"Evento creado en calcurse: {title}")
            return {
                "success": True,
                "message": f"Evento '{title}' agregado exitosamente a calcurse",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creando evento en calcurse: {e.stderr}")
            return {"success": False, "message": f"Error: {e.stderr}"}
        except Exception as e:
            logger.error(f"Error inesperado creando evento: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def saveTask(self, title: str, priority: int = 0) -> Dict[str, Any]:
        """
        Guarda una tarea en calcurse usando formato iCal.

        Args:
            title: Título de la tarea
            priority: Prioridad (0-9, siendo 9 la más alta)

        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Crear tarea en formato iCal (VTODO)
            ical_task = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agente Personal//ES
BEGIN:VTODO
UID:{datetime.now().timestamp()}-{title.replace(' ', '-')}@agente
SUMMARY:{title}
PRIORITY:{priority}
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR"""

            # Importar a calcurse
            subprocess.run(
                ["calcurse", "-i", "-", "-q"],
                input=ical_task,
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"Tarea creada en calcurse: {title} (prioridad: {priority})")
            return {
                "success": True,
                "message": f"Tarea '{title}' creada exitosamente con prioridad {priority}",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creando tarea en calcurse: {e.stderr}")
            return {"success": False, "message": f"Error: {e.stderr}"}
        except Exception as e:
            logger.error(f"Error inesperado creando tarea: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def getAgenda(self, days: int = 1) -> Dict[str, Any]:
        """
        Obtiene la agenda de calcurse para los próximos N días.

        Args:
            days: Número de días a consultar

        Returns:
            Dict con los eventos y tareas encontrados
        """
        try:
            # Ejecutar calcurse con query para obtener eventos de los próximos N días
            # El argumento -r requiere el número sin espacio: -r3
            result = subprocess.run(
                ["calcurse", f"-r{days}"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parsear salida
            output = result.stdout.strip()
            events = []
            tasks = []

            if output:
                lines = output.split("\n")
                current_section = None

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Detectar secciones
                    if "appointments:" in line.lower() or line.startswith("---"):
                        current_section = "events"
                        continue
                    elif "todo:" in line.lower():
                        current_section = "tasks"
                        continue

                    # Parsear eventos (formato: - HH:MM -> HH:MM Título)
                    if current_section == "events" and "-" in line:
                        events.append(line)
                    # Parsear tareas (formato: [prioridad] Título)
                    elif current_section == "tasks" or (line.startswith("[") and "]" in line):
                        tasks.append(line)

            logger.info(f"Agenda obtenida: {len(events)} eventos, {len(tasks)} tareas")
            return {
                "success": True,
                "message": f"Agenda para los próximos {days} días",
                "events": events,
                "tasks": tasks,
                "raw_output": output,
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"Error obteniendo agenda de calcurse: {e.stderr}")
            return {
                "success": False,
                "message": f"Error: {e.stderr}",
                "events": [],
                "tasks": [],
            }
        except Exception as e:
            logger.error(f"Error inesperado obteniendo agenda: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "events": [],
                "tasks": [],
            }

    def saveEventNote(self, event_id: str, note: str) -> Dict[str, Any]:
        """
        Agrega una nota a un evento existente.

        Args:
            event_id: ID del evento
            note: Texto de la nota

        Returns:
            Dict con el resultado de la operación
        """
        # TODO: Implementar cuando se necesite agregar notas a eventos
        logger.warning("saveEventNote no implementado completamente")
        return {
            "success": False,
            "message": "Funcionalidad de notas de eventos no implementada aún",
        }

    def saveTaskNote(self, task_id: str, note: str) -> Dict[str, Any]:
        """
        Agrega una nota a una tarea existente.

        Args:
            task_id: ID de la tarea
            note: Texto de la nota

        Returns:
            Dict con el resultado de la operación
        """
        # TODO: Implementar cuando se necesite agregar notas a tareas
        logger.warning("saveTaskNote no implementado completamente")
        return {
            "success": False,
            "message": "Funcionalidad de notas de tareas no implementada aún",
        }
