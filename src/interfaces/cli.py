"""Interfaz CLI para el agente personal."""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from typing import Optional

from ..core.agent import PersonalAgent
from ..utils.config import Settings, load_yaml_config


console = Console()


class CLIInterface:
    """Interfaz de línea de comandos para interactuar con el agente."""

    def __init__(self, agent: PersonalAgent):
        """
        Inicializa la interfaz CLI.

        Args:
            agent: Instancia del agente personal
        """
        self.agent = agent
        self.running = False

    def print_welcome(self):
        """Muestra mensaje de bienvenida."""
        welcome_text = """
# Agente Personal

Hola! Soy tu asistente personal inteligente.

**Puedo ayudarte con:**
- Gestionar tu calendario y tareas
- Crear recordatorios
- Planificar tiempo de aprendizaje
- Responder preguntas y más

**Comandos especiales:**
- `/help` - Mostrar ayuda
- `/agenda` - Ver tu agenda
- `/clear` - Limpiar historial de conversación
- `/exit` - Salir

Escribe tu mensaje para comenzar...
        """
        console.print(Panel(Markdown(welcome_text), border_style="cyan"))

    def print_help(self):
        """Muestra ayuda sobre comandos disponibles."""
        help_text = """
## Comandos Disponibles

**Comandos especiales:**
- `/help` - Muestra esta ayuda
- `/agenda [días]` - Muestra tu agenda (por defecto 1 día)
- `/clear` - Limpia el historial de conversación
- `/exit` - Sale del agente

**Ejemplos de uso:**
- "Qué tengo programado para mañana?"
- "Agenda una reunión con el equipo el lunes a las 3pm"
- "Recuérdame revisar el email en 2 horas"
- "Ayúdame a aprender Python, tengo 5 horas por semana"
- "Cancela mi reunión de las 4pm"
        """
        console.print(Panel(Markdown(help_text), border_style="yellow"))

    async def handle_command(self, command: str) -> bool:
        """
        Maneja comandos especiales del CLI.

        Args:
            command: Comando a ejecutar

        Returns:
            True si debe continuar, False si debe salir
        """
        cmd = command.lower().strip()

        if cmd == "/exit" or cmd == "/quit":
            console.print("[yellow]Hasta luego![/yellow]")
            return False

        elif cmd == "/help":
            self.print_help()

        elif cmd == "/clear":
            self.agent.clear_history()
            console.print("[green]Historial limpiado.[/green]")

        elif cmd.startswith("/agenda"):
            parts = cmd.split()
            days = int(parts[1]) if len(parts) > 1 else 1
            agenda = await self.agent.get_agenda(days=days)
            console.print(Panel(agenda, title="Tu Agenda", border_style="blue"))

        else:
            console.print(
                "[red]Comando no reconocido. Usa /help para ver comandos disponibles.[/red]"
            )

        return True

    async def run(self):
        """Ejecuta el loop principal del CLI."""
        self.running = True
        self.print_welcome()

        while self.running:
            try:
                # Leer input del usuario
                user_input = Prompt.ask("\n[bold cyan]Tú[/bold cyan]")

                if not user_input.strip():
                    continue

                # Manejar comandos especiales
                if user_input.startswith("/"):
                    should_continue = await self.handle_command(user_input)
                    if not should_continue:
                        break
                    continue

                # Procesar mensaje con el agente
                console.print("[dim]Pensando...[/dim]")
                response = await self.agent.process(user_input)

                # Mostrar respuesta
                console.print(
                    Panel(
                        Markdown(response),
                        title="[bold green]Agente[/bold green]",
                        border_style="green",
                    )
                )

            except KeyboardInterrupt:
                console.print(
                    "\n[yellow]Interrumpido. Usa /exit para salir correctamente.[/yellow]"
                )
                break

            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                continue


async def start_cli(settings: Optional[Settings] = None):
    """
    Punto de entrada para iniciar la interfaz CLI.

    Args:
        settings: Configuración del agente
    """
    # Cargar configuración
    if settings is None:
        settings = Settings()

    config = load_yaml_config()

    # Crear agente
    agent = PersonalAgent(settings=settings, config=config)

    # Crear y ejecutar CLI
    cli = CLIInterface(agent)
    await cli.run()
