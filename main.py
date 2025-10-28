"""Punto de entrada principal del Agente Personal."""
import asyncio
import logging
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import get_settings
from src.interfaces.cli import start_cli
from src.interfaces.telegram import start_telegram_bot


def setup_logging(log_level: str = "INFO", log_path: Path = None):
    """Configura el sistema de logging."""
    if log_path:
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "agent.log"
    else:
        log_file = None
    
    # Formato del log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


def main():
    """Función principal."""
    try:
        # Cargar configuración
        settings = get_settings()
        
        # Configurar logging
        setup_logging(settings.log_level, settings.log_path)
        
        logger = logging.getLogger(__name__)
        logger.info("Iniciando Agente Personal...")

        # Determinar qué interfaces iniciar
        interfaces_enabled = []

        if settings.enable_cli:
            interfaces_enabled.append("CLI")
        if settings.enable_telegram:
            interfaces_enabled.append("Telegram")
        if settings.enable_web:
            interfaces_enabled.append("Web")

        if not interfaces_enabled:
            logger.error("No hay interfaces habilitadas. Habilita CLI, Telegram o Web en .env")
            sys.exit(1)

        logger.info(f"Interfaces habilitadas: {', '.join(interfaces_enabled)}")

        # Iniciar la interfaz solicitada
        if settings.enable_telegram and not settings.enable_cli:
            # Solo Telegram
            asyncio.run(start_telegram_bot(settings))
        elif settings.enable_cli:
            # CLI (por defecto o si está habilitado)
            asyncio.run(start_cli(settings))
        else:
            # Otras interfaces (Web, etc.)
            logger.error("Interfaz Web aún no implementada")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nAgente detenido por el usuario.")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
