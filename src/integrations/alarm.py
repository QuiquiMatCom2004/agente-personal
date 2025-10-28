"""Sistema de alarmas con sonido y notificaciones persistentes."""

import subprocess
import logging
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class AlarmSound(Enum):
    """Sonidos de alarma disponibles."""

    BEEP = "beep"  # Beep del sistema
    BELL = "bell"  # Campana
    ALARM = "alarm"  # Alarma fuerte
    GENTLE = "gentle"  # Alarma suave


class AlarmManager:
    """Gestor de alarmas con sonido."""

    def __init__(self, sound_enabled: bool = True):
        """
        Inicializa el gestor de alarmas.

        Args:
            sound_enabled: Si se debe reproducir sonido
        """
        self.sound_enabled = sound_enabled
        self._check_audio_system()
        logger.info("AlarmManager inicializado")

    def _check_audio_system(self):
        """Verifica que haya un sistema de audio disponible."""
        # Verificar paplay (PulseAudio)
        try:
            subprocess.run(["which", "paplay"], capture_output=True, check=True, timeout=2)
            self.audio_player = "paplay"
            logger.info("Sistema de audio: PulseAudio (paplay)")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

        # Verificar mpv
        try:
            subprocess.run(["which", "mpv"], capture_output=True, check=True, timeout=2)
            self.audio_player = "mpv"
            logger.info("Sistema de audio: mpv")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

        # Fallback a beep del sistema
        self.audio_player = "beep"
        logger.warning("No se encontró paplay/mpv. Usando beep del sistema como fallback")

    def trigger_alarm(
        self,
        title: str,
        message: str,
        sound: AlarmSound = AlarmSound.ALARM,
        repeat_sound: int = 3,
        persistent: bool = True,
    ) -> bool:
        """
        Dispara una alarma con sonido y notificación.

        Args:
            title: Título de la alarma
            message: Mensaje de la alarma
            sound: Tipo de sonido a reproducir
            repeat_sound: Cuántas veces repetir el sonido
            persistent: Si la notificación debe ser persistente (no expira)

        Returns:
            True si se disparó exitosamente
        """
        try:
            # Enviar notificación persistente CRITICAL
            self._send_alarm_notification(title, message, persistent)

            # Reproducir sonido si está habilitado
            if self.sound_enabled:
                self._play_alarm_sound(sound, repeat_sound)

            logger.info(f"Alarma disparada: {title}")
            return True

        except Exception as e:
            logger.error(f"Error disparando alarma: {e}")
            return False

    def _send_alarm_notification(self, title: str, message: str, persistent: bool):
        """
        Envía una notificación de alarma.

        Args:
            title: Título
            message: Mensaje
            persistent: Si debe ser persistente
        """
        try:
            timeout = "0" if persistent else "30000"  # 0 = no expira nunca

            cmd = [
                "notify-send",
                f"🚨 ALARMA: {title}",
                message,
                "--urgency",
                "critical",
                "--expire-time",
                timeout,
                "--icon",
                "alarm-symbolic",
                "--category",
                "alarm",
            ]

            # Hacer la notificación más visible con acciones
            if persistent:
                cmd.extend(["--action", "dismiss=Desactivar Alarma"])

            subprocess.run(cmd, check=True, timeout=5)

        except Exception as e:
            logger.error(f"Error enviando notificación de alarma: {e}")

    def _play_alarm_sound(self, sound: AlarmSound, repeat: int):
        """
        Reproduce el sonido de alarma.

        Args:
            sound: Tipo de sonido
            repeat: Cuántas veces repetir
        """
        try:
            if self.audio_player == "paplay":
                self._play_with_paplay(sound, repeat)
            elif self.audio_player == "mpv":
                self._play_with_mpv(sound, repeat)
            else:
                self._play_system_beep(repeat)

        except Exception as e:
            logger.error(f"Error reproduciendo sonido: {e}")

    def _play_with_paplay(self, sound: AlarmSound, repeat: int):
        """Reproduce sonido con paplay (PulseAudio)."""
        # Sonidos del sistema en /usr/share/sounds
        sound_files = {
            AlarmSound.BEEP: "/usr/share/sounds/freedesktop/stereo/message.oga",
            AlarmSound.BELL: "/usr/share/sounds/freedesktop/stereo/bell.oga",
            AlarmSound.ALARM: "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
            AlarmSound.GENTLE: "/usr/share/sounds/freedesktop/stereo/complete.oga",
        }

        sound_file = sound_files.get(sound, sound_files[AlarmSound.ALARM])

        # Verificar si existe el archivo
        if not Path(sound_file).exists():
            logger.warning(f"Archivo de sonido no encontrado: {sound_file}")
            # Fallback a beep
            self._play_system_beep(repeat)
            return

        # Reproducir el sonido 'repeat' veces
        for _ in range(repeat):
            subprocess.run(["paplay", sound_file], check=False, timeout=5, capture_output=True)

    def _play_with_mpv(self, sound: AlarmSound, repeat: int):
        """Reproduce sonido con mpv."""
        sound_files = {
            AlarmSound.BEEP: "/usr/share/sounds/freedesktop/stereo/message.oga",
            AlarmSound.BELL: "/usr/share/sounds/freedesktop/stereo/bell.oga",
            AlarmSound.ALARM: "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
            AlarmSound.GENTLE: "/usr/share/sounds/freedesktop/stereo/complete.oga",
        }

        sound_file = sound_files.get(sound, sound_files[AlarmSound.ALARM])

        if not Path(sound_file).exists():
            self._play_system_beep(repeat)
            return

        # Reproducir con mpv
        for _ in range(repeat):
            subprocess.run(
                ["mpv", "--quiet", "--no-video", sound_file],
                check=False,
                timeout=5,
                capture_output=True,
            )

    def _play_system_beep(self, repeat: int):
        """Reproduce beep del sistema como fallback."""
        for _ in range(repeat):
            # Usar el beep visual/auditivo del terminal
            print("\a", end="", flush=True)

    def create_dialog_alarm(self, title: str, message: str) -> bool:
        """
        Crea una alarma con diálogo modal que requiere interacción del usuario.

        Args:
            title: Título de la alarma
            message: Mensaje de la alarma

        Returns:
            True si se mostró el diálogo
        """
        try:
            # Intentar con zenity (diálogo gráfico)
            subprocess.run(
                [
                    "zenity",
                    "--warning",
                    "--title",
                    f"ALARMA: {title}",
                    "--text",
                    message,
                    "--width",
                    "400",
                ],
                check=False,
                timeout=None,  # Esperar a que el usuario cierre
            )
            return True

        except FileNotFoundError:
            logger.warning("zenity no está instalado, usando notificación persistente")
            self._send_alarm_notification(title, message, persistent=True)
            return True

        except Exception as e:
            logger.error(f"Error mostrando diálogo: {e}")
            return False

    def snooze_alarm(self, alarm_id: str, minutes: int = 5) -> bool:
        """
        Pospone una alarma por X minutos.

        Args:
            alarm_id: ID de la alarma
            minutes: Minutos a posponer

        Returns:
            True si se pospuso exitosamente
        """
        # Esta funcionalidad requiere integración con el scheduler
        # Se implementará en reminder_tool.py
        logger.info(f"Alarma {alarm_id} pospuesta por {minutes} minutos")
        return True
