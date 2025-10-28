"""Clases base para el sistema de herramientas."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolParameter:
    """Representa un parámetro de una herramienta."""

    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class Tool(ABC):
    """
    Clase base para todas las herramientas del agente.

    Cada herramienta debe implementar:
    - name: nombre único de la herramienta
    - description: qué hace la herramienta
    - parameters: lista de parámetros que acepta
    - execute: lógica de ejecución
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre único de la herramienta."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción de qué hace la herramienta."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Lista de parámetros que acepta la herramienta."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la herramienta con los parámetros proporcionados.

        Returns:
            Dict con el resultado de la ejecución
        """
        pass

    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Convierte la herramienta al formato esperado por OpenAI Function Calling.

        Returns:
            Dict en formato OpenAI tool
        """
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {"type": param.type, "description": param.description}

            if param.enum:
                param_schema["enum"] = param.enum

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": properties, "required": required},
            },
        }


class ToolRegistry:
    """
    Registro central de todas las herramientas disponibles.

    Permite registrar herramientas y obtenerlas por nombre.
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        logger.info("ToolRegistry inicializado")

    def register(self, tool: Tool):
        """Registra una nueva herramienta."""
        self._tools[tool.name] = tool
        logger.info(f"Herramienta registrada: {tool.name}")

    def get(self, name: str) -> Optional[Tool]:
        """Obtiene una herramienta por su nombre."""
        return self._tools.get(name)

    def get_all(self) -> List[Tool]:
        """Obtiene todas las herramientas registradas."""
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las herramientas en formato OpenAI.

        Returns:
            Lista de herramientas en formato OpenAI Function Calling
        """
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta por su nombre.

        Args:
            tool_name: Nombre de la herramienta
            **kwargs: Parámetros para la herramienta

        Returns:
            Resultado de la ejecución
        """
        tool = self.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Herramienta no encontrada: {tool_name}"}

        try:
            result = await tool.execute(**kwargs)
            logger.info(f"Herramienta ejecutada: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {tool_name}: {e}")
            return {"success": False, "error": f"Error ejecutando {tool_name}: {str(e)}"}
