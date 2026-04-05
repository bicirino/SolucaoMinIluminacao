import logging
import pywhatkit
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
from src.config import WHATSAPP_SESSION_PATH, WHATSAPP_DELAY_SECONDS

logger = logging.getLogger(__name__)


class WhatsAppBotService:
    """Serviço para envio de mensagens via WhatsApp usando PyWhatKit"""

    def __init__(self):
        """Inicializa o serviço de WhatsApp"""
        self.session_path = Path(WHATSAPP_SESSION_PATH)
        self.delay_seconds = WHATSAPP_DELAY_SECONDS
        logger.info("Serviço WhatsApp inicializado")

    def setup_session(self) -> bool:
        """
        Configura a sessão do WhatsApp (gera QR Code para scan)
        
        Returns:
            True se a sessão foi configurada com sucesso
        """
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)
            logger.info("Sessão do WhatsApp preparada")
            logger.info("Escaneie o código QR com seu telefone para autorizar")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar sessão: {e}")
            return False

    def send_message(self, phone_number: str, message: str, schedule_hour: Optional[int] = None, 
                    schedule_minute: Optional[int] = None) -> bool:
        """
        Envia uma mensagem de WhatsApp
        
        Args:
            phone_number: Número do WhatsApp (formato: 55XXYYYYYYYYYY)
            message: Texto da mensagem
            schedule_hour: Hora de envio (opcional)
            schedule_minute: Minuto de envio (opcional)
            
        Returns:
            True se a mensagem foi enviada/agendada com sucesso
        """
        try:
            # Validação do número
            if not self._validate_phone_number(phone_number):
                logger.error(f"Número de WhatsApp inválido: {phone_number}")
                return False

            # Formata o número para PyWhatKit (remove o "+")
            formatted_number = f"+{phone_number}"

            if schedule_hour is not None and schedule_minute is not None:
                # Agenda o envio para uma hora específica
                pywhatkit.sendwhatmsg(
                    phone_no=formatted_number,
                    message=message,
                    time_hour=schedule_hour,
                    time_min=schedule_minute,
                    wait_time=self.delay_seconds
                )
                logger.info(f"Mensagem agendada para {formatted_number} às {schedule_hour}:{schedule_minute:02d}")
            else:
                # Envia a mensagem imediatamente (abre o navegador)
                pywhatkit.sendwhatmsg_instantly(
                    phone_no=formatted_number,
                    message=message,
                    wait_time=self.delay_seconds,
                    tab_close=False
                )
                logger.info(f"Mensagem enviada para {formatted_number}")

            return True

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False

    def send_message_12h_before(self, phone_number: str, message: str, event_time: datetime) -> bool:
        """
        Envia uma mensagem 12 horas antes de um evento
        
        Args:
            phone_number: Número do WhatsApp
            message: Texto da mensagem
            event_time: Data/hora do evento
            
        Returns:
            True se a mensagem foi agendada
        """
        try:
            # Calcula a hora de envio (12h antes)
            send_time = event_time - timedelta(hours=12)
            
            # Se o horário já passou, envia imediatamente
            if send_time <= datetime.now():
                logger.warning(f"Horário de envio já passou, enviando imediatamente")
                return self.send_message(phone_number, message)

            # Agenda o envio
            return self.send_message(
                phone_number=phone_number,
                message=message,
                schedule_hour=send_time.hour,
                schedule_minute=send_time.minute
            )

        except Exception as e:
            logger.error(f"Erro ao agendar envio 12h antes: {e}")
            return False

    def send_notification(self, phone_number: str, person_name: str, event_date: str, 
                         event_time: str) -> bool:
        """
        Envia notificação padronizada de escala
        
        Args:
            phone_number: Número do WhatsApp
            person_name: Nome da pessoa
            event_date: Data do evento (ex: "15/04")
            event_time: Hora do evento (ex: "19:30")
            
        Returns:
            True se a notificação foi enviada
        """
        try:
            message = self._create_notification_message(
                person_name=person_name,
                event_date=event_date,
                event_time=event_time
            )
            return self.send_message(phone_number, message)

        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            return False

    def _create_notification_message(self, person_name: str, event_date: str, 
                                     event_time: str) -> str:
        """
        Cria a mensagem padronizada de notificação
        
        Args:
            person_name: Nome da pessoa
            event_date: Data do evento
            event_time: Hora do evento
            
        Returns:
            Mensagem formatada
        """
        message = f"""
Olá {person_name}! 👋

Lembrando que você está escalado(a) para o ministério de iluminação! 💡

📅 Data: {event_date}
🕐 Horário: {event_time}

Que Deus te abençoe! 🙏

---
*Mensagem automática do Sistema de Escalas*
        """.strip()
        
        return message

    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida o formato do número de WhatsApp
        
        Args:
            phone_number: Número a validar
            
        Returns:
            True se o número é válido
        """
        # Remove caracteres especiais
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Deve começar com 55 (Brasil) e ter pelo menos 12 dígitos
        return clean_number.startswith("55") and len(clean_number) >= 12

    def close_browser(self) -> None:
        """
        Fecha o navegador do PyWhatKit
        Útil quando enviando mensagens instantaneamente
        """
        try:
            import time
            import pyautogui
            
            # Tenta fechar abas do navegador
            pyautogui.hotkey("ctrl", "w")
            time.sleep(1)
            logger.info("Navegador fechado")
        except Exception as e:
            logger.warning(f"Não foi possível fechar o navegador: {e}")
