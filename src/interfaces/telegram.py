"""Interfaz de Telegram Bot para el agente personal."""

import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from ..core.agent import PersonalAgent
from ..utils.config import Settings, load_yaml_config

logger = logging.getLogger(__name__)


class TelegramBot:
    """Bot de Telegram para el agente personal."""

    def __init__(self, settings: Settings, agent: PersonalAgent):
        """
        Inicializa el bot de Telegram.

        Args:
            settings: Configuración del sistema
            agent: Instancia del agente personal
        """
        self.settings = settings
        self.agent = agent
        self.allowed_users = self._parse_allowed_users(settings.telegram_allowed_user_ids)

        # Crear aplicación de telegram
        self.app = Application.builder().token(settings.telegram_bot_token).build()

        # Registrar handlers
        self._register_handlers()

        logger.info(f"TelegramBot inicializado. Usuarios permitidos: {len(self.allowed_users)}")

    def _parse_allowed_users(self, user_ids_str: str) -> set:
        """
        Parsea la lista de IDs de usuarios permitidos.

        Args:
            user_ids_str: String con IDs separados por comas

        Returns:
            Set de IDs de usuarios
        """
        if not user_ids_str:
            return set()

        try:
            return set(int(uid.strip()) for uid in user_ids_str.split(",") if uid.strip())
        except ValueError as e:
            logger.error(f"Error parseando IDs de usuarios: {e}")
            return set()

    def _register_handlers(self):
        """Registra los handlers del bot."""
        # Comandos
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("agenda", self.agenda_command))
        self.app.add_handler(CommandHandler("tareas", self.tasks_command))
        self.app.add_handler(CommandHandler("clear", self.clear_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))

        # Mensajes de texto (conversación)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Error handler
        self.app.add_error_handler(self.error_handler)

        logger.info("Handlers de Telegram registrados")

    def _check_authorization(self, update: Update) -> bool:
        """
        Verifica si el usuario está autorizado.

        Args:
            update: Update de Telegram

        Returns:
            True si está autorizado
        """
        user_id = update.effective_user.id

        # Si no hay lista de usuarios permitidos, permitir a todos
        if not self.allowed_users:
            return True

        return user_id in self.allowed_users

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /start."""
        if not self._check_authorization(update):
            await update.message.reply_text(
                "❌ No estás autorizado para usar este bot.\n"
                "Contacta al administrador para obtener acceso."
            )
            return

        user_name = update.effective_user.first_name

        welcome_message = f"""
👋 ¡Hola {user_name}!

Soy tu Agente Personal Inteligente. Puedo ayudarte con:

📅 **Calendario y Eventos**
- Crear y consultar eventos
- Ver tu agenda

✅ **Gestión de Tareas**
- Crear tareas con prioridades
- Listar tareas pendientes
- Completar tareas

⏰ **Recordatorios y Alarmas**
- Programar recordatorios
- Crear alarmas con sonido

🔔 **Notificaciones**
- Notificaciones desktop
- Alertas inteligentes

**Comandos disponibles:**
/help - Ver ayuda completa
/agenda - Ver tu agenda
/tareas - Ver tus tareas
/clear - Limpiar historial
/stats - Ver estadísticas

También puedes hablar conmigo en lenguaje natural. Por ejemplo:
- "Recuérdame llamar a mamá en 2 horas"
- "Crea una tarea urgente para revisar el código"
- "Qué tengo programado para mañana?"
- "Ponme una alarma para las 9am"

¡Escribe tu mensaje para comenzar! 💬
"""

        await update.message.reply_text(welcome_message)
        logger.info(f"Usuario {update.effective_user.id} inició el bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /help."""
        if not self._check_authorization(update):
            return

        help_text = """
**📚 Ayuda del Agente Personal**

**Comandos disponibles:**

📅 `/agenda [días]` - Ver tu agenda
   Ejemplo: `/agenda 3` (próximos 3 días)

✅ `/tareas [filtro]` - Ver tus tareas
   Filtros: pending, completed, urgent, all
   Ejemplo: `/tareas urgent`

🗑️ `/clear` - Limpiar historial de conversación

📊 `/stats` - Ver estadísticas de uso

**Ejemplos de uso natural:**

- "Crea un evento: Reunión con el equipo mañana a las 3pm"
- "Recuérdame comprar leche en 2 horas"
- "Ponme una alarma para despertar a las 7am"
- "Qué tareas tengo pendientes?"
- "Marca como completada la tarea de revisar emails"
- "Envíame un resumen de mi día"

¡Simplemente escribe lo que necesites en lenguaje natural! 🚀
"""

        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def agenda_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /agenda."""
        if not self._check_authorization(update):
            return

        # Obtener días del argumento (por defecto 1)
        days = 1
        if context.args and len(context.args) > 0:
            try:
                days = int(context.args[0])
            except ValueError:
                days = 1

        # Delegar al agente
        user_id = str(update.effective_user.id)
        message = f"Muéstrame mi agenda de los próximos {days} días"

        await self._process_agent_message(update, user_id, message)

    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /tareas."""
        if not self._check_authorization(update):
            return

        # Obtener filtro del argumento
        filter_type = "pending"
        if context.args and len(context.args) > 0:
            filter_type = context.args[0].lower()

        # Delegar al agente
        user_id = str(update.effective_user.id)
        message = f"Muéstrame mis tareas {filter_type}"

        await self._process_agent_message(update, user_id, message)

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /clear."""
        if not self._check_authorization(update):
            return

        user_id = str(update.effective_user.id)
        self.agent.clear_history(user_id)

        await update.message.reply_text(
            "✅ Historial de conversación limpiado.\nPuedes comenzar una nueva conversación."
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /stats."""
        if not self._check_authorization(update):
            return

        user_id = str(update.effective_user.id)

        # Obtener estadísticas del agente
        history_length = len(self.agent.conversation_history.get(user_id, []))
        tools_count = len(self.agent.tool_registry.get_all())

        stats_text = f"""
📊 **Estadísticas del Agente**

👤 **Tu usuario:** `{user_id}`
💬 **Mensajes en historial:** {history_length}
🔧 **Herramientas disponibles:** {tools_count}
🤖 **Modelo:** {self.settings.agent_model}
"""

        await update.message.reply_text(stats_text, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensajes de texto normales."""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No estás autorizado para usar este bot.")
            return

        user_id = str(update.effective_user.id)
        message = update.message.text

        # Mostrar indicador de escritura
        await update.message.chat.send_action("typing")

        # Procesar con el agente
        await self._process_agent_message(update, user_id, message)

    async def _process_agent_message(self, update: Update, user_id: str, message: str):
        """
        Procesa un mensaje con el agente y envía la respuesta.

        Args:
            update: Update de Telegram
            user_id: ID del usuario
            message: Mensaje a procesar
        """
        try:
            # Procesar con el agente
            response = await self.agent.process(message, user_id=user_id)

            # Enviar respuesta (dividir si es muy larga)
            if len(response) > 4096:
                # Telegram tiene límite de 4096 caracteres
                chunks = [response[i : i + 4096] for i in range(0, len(response), 4096)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Lo siento, ocurrió un error al procesar tu mensaje:\n{str(e)}"
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para errores."""
        logger.error(f"Error en Telegram bot: {context.error}", exc_info=context.error)

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error inesperado. Por favor, intenta de nuevo."
            )

    async def setup_commands(self):
        """Configura los comandos del bot en el menú de Telegram."""
        commands = [
            BotCommand("start", "Iniciar el bot"),
            BotCommand("help", "Ver ayuda"),
            BotCommand("agenda", "Ver tu agenda"),
            BotCommand("tareas", "Ver tus tareas"),
            BotCommand("clear", "Limpiar historial"),
            BotCommand("stats", "Ver estadísticas"),
        ]

        await self.app.bot.set_my_commands(commands)
        logger.info("Comandos del bot configurados en Telegram")

    async def start(self):
        """Inicia el bot de Telegram."""
        try:
            # Configurar comandos
            await self.setup_commands()

            # Iniciar polling
            logger.info("Iniciando Telegram bot...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(
                allowed_updates=Update.ALL_TYPES, drop_pending_updates=True
            )

            logger.info("✅ Telegram bot activo y esperando mensajes")

            # Mantener el bot corriendo
            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"Error iniciando bot de Telegram: {e}", exc_info=True)
            raise

    async def stop(self):
        """Detiene el bot de Telegram."""
        logger.info("Deteniendo Telegram bot...")
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
        logger.info("Telegram bot detenido")


async def start_telegram_bot(settings: Settings):
    """
    Inicia el bot de Telegram.

    Args:
        settings: Configuración del sistema
    """
    # Cargar configuración
    config = load_yaml_config()

    # Crear agente
    agent = PersonalAgent(settings=settings, config=config)

    # Crear y arrancar bot
    bot = TelegramBot(settings=settings, agent=agent)

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
        await bot.stop()
    except Exception as e:
        logger.error(f"Error en bot de Telegram: {e}", exc_info=True)
        raise
