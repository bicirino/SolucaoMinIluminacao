import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import LOG_LEVEL, LOG_FILE
from src.services.contact_service import ContactService
from src.services.vision_ocr_service import VisionOCRService
from src.services.whatsapp_bot_service import WhatsAppBotService
from src.jobs.scheduler_service import SchedulerService

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)


class MinisterioIluminacaoBot:
    """Orquestrador principal do bot de escalas de iluminação"""

    def __init__(self):
        """Inicializa todos os serviços"""
        logger.info("=" * 60)
        logger.info("Iniciando Ministério Iluminação Bot")
        logger.info("=" * 60)

        self.contact_service = ContactService()
        self.scheduler_service = SchedulerService()
        self.whatsapp_service = WhatsAppBotService()
        
        # Vision service é opcional (requer credenciais Google)
        self.vision_service = None
        try:
            self.vision_service = VisionOCRService()
        except Exception as e:
            logger.warning(f"Google Vision não disponível: {e}")
            logger.warning("Você precisará fornecer os nomes manualmente")

        logger.info("Todos os serviços inicializados")

    def setup_whatsapp_session(self) -> bool:
        """
        Configura a sessão do WhatsApp (escaneamento do QR Code)
        
        Returns:
            True se configurado com sucesso
        """
        logger.info("="*60)
        logger.info("CONFIGURAÇÃO DO WHATSAPP")
        logger.info("="*60)
        
        success = self.whatsapp_service.setup_session()
        
        if success:
            logger.info("✓ Sessão configurada com sucesso")
            logger.info("Você pode agora usar o bot para enviar mensagens")
        else:
            logger.error("✗ Erro ao configurar a sessão")
        
        return success

    def process_scale_image(self, image_path: str) -> list:
        """
        Processa a imagem da escala e extrai nomes
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Lista de nomes extraídos
        """
        logger.info(f"Processando imagem: {image_path}")
        
        if not self.vision_service:
            logger.error("Serviço Vision não disponível")
            logger.info("Forneça os nomes manualmente")
            return []

        names = self.vision_service.extract_names_from_scale(image_path)
        logger.info(f"Nomes extraídos: {names}")
        return names

    def send_notification_to_all(self, names_and_dates: dict) -> None:
        """
        Envia notificações para todas as pessoas na escala
        
        Args:
            names_and_dates: Dicionário com {nome: data_evento}
                            Ex: {"João Silva": "2024-04-15 19:30"}
        """
        logger.info("="*60)
        logger.info("ENVIANDO NOTIFICAÇÕES")
        logger.info("="*60)

        total = len(names_and_dates)
        success_count = 0

        for name, event_datetime_str in names_and_dates.items():
            try:
                # Obtém o número de WhatsApp do contato
                phone = self.contact_service.get_contact(name)
                
                if not phone:
                    logger.warning(f"Contato não encontrado: {name}")
                    continue

                # Parseia a data/hora do evento
                event_datetime = datetime.fromisoformat(event_datetime_str)
                event_date = event_datetime.strftime("%d/%m")
                event_time = event_datetime.strftime("%H:%M")

                # Envia a notificação
                success = self.whatsapp_service.send_notification(
                    phone_number=phone,
                    person_name=name,
                    event_date=event_date,
                    event_time=event_time
                )

                if success:
                    success_count += 1
                    logger.info(f"✓ Notificação enviada para {name}")
                else:
                    logger.error(f"✗ Erro ao enviar para {name}")

            except Exception as e:
                logger.error(f"Erro ao processar {name}: {e}")

        logger.info(f"Resumo: {success_count}/{total} notificações enviadas")

    def schedule_all_notifications(self, names_and_dates: dict) -> None:
        """
        Agenda notificações para 24h antes de cada evento
        
        Args:
            names_and_dates: Dicionário com {nome: data_evento}
        """
        logger.info("="*60)
        logger.info("AGENDANDO NOTIFICAÇÕES (24h antes)")
        logger.info("="*60)

        self.scheduler_service.start()

        for name, event_datetime_str in names_and_dates.items():
            try:
                phone = self.contact_service.get_contact(name)
                
                if not phone:
                    logger.warning(f"Contato não encontrado: {name}")
                    continue

                event_datetime = datetime.fromisoformat(event_datetime_str)
                
                # Agenda para 24h antes
                send_time = event_datetime - timedelta(hours=24)
                
                if send_time <= datetime.now():
                    logger.warning(f"Horário já passou para {name}, enviando agora")
                    self.whatsapp_service.send_notification(
                        phone_number=phone,
                        person_name=name,
                        event_date=event_datetime.strftime("%d/%m"),
                        event_time=event_datetime.strftime("%H:%M")
                    )
                else:
                    job_id = self.scheduler_service.schedule_message(
                        func=self.whatsapp_service.send_notification,
                        send_time=send_time,
                        args=(phone, name, event_datetime.strftime("%d/%m"), 
                              event_datetime.strftime("%H:%M")),
                        job_id=f"notif_{name.replace(' ', '_')}"
                    )
                    logger.info(f"✓ Notificação agendada para {name}: {job_id}")

            except Exception as e:
                logger.error(f"Erro ao agendar para {name}: {e}")

    def start_continuous_monitoring(self) -> None:
        """
        Inicia monitoramento contínuo
        Verifica periodicamente se há novos eventos para notificar
        """
        logger.info("="*60)
        logger.info("INICIANDO MONITORAMENTO CONTÍNUO")
        logger.info("="*60)

        self.scheduler_service.start()
        logger.info("Scheduler iniciado e rodando em background")
        logger.info("O bot continuará enviando notificações 24/7")

    def add_contact_interactive(self) -> bool:
        """
        Adiciona um contato interativamente
        
        Returns:
            True se adicionado com sucesso
        """
        logger.info("="*60)
        logger.info("ADICIONAR NOVO CONTATO")
        logger.info("="*60)

        name = input("Nome: ").strip()
        if not name:
            logger.error("Nome vazio")
            return False

        phone = input("Número WhatsApp (55XXYYYYYYYYYY): ").strip()
        if not phone:
            logger.error("Número vazio")
            return False

        success = self.contact_service.add_contact(name, phone)
        if success:
            logger.info(f"✓ Contato adicionado: {name}")
        else:
            logger.error("✗ Erro ao adicionar contato")
        
        return success

    def list_contacts(self) -> None:
        """Lista todos os contatos cadastrados"""
        logger.info("="*60)
        logger.info("CONTATOS CADASTRADOS")
        logger.info("="*60)

        contacts = self.contact_service.get_all_contacts()
        
        if not contacts:
            logger.info("Nenhum contato cadastrado")
            return

        for name, phone in contacts.items():
            logger.info(f"  • {name}: {phone}")

    def get_scheduler_status(self) -> None:
        """Exibe o status do scheduler"""
        status = self.scheduler_service.get_scheduler_status()
        
        logger.info("="*60)
        logger.info("STATUS DO SCHEDULER")
        logger.info("="*60)
        logger.info(f"Ativo: {'Sim' if status['running'] else 'Não'}")
        logger.info(f"Habilitado: {'Sim' if status['enabled'] else 'Não'}")
        logger.info(f"Jobs agendados: {status['jobs_count']}")
        logger.info(f"Fuso horário: {status['timezone']}")
        logger.info(f"Intervalo de verificação: {status['check_interval_minutes']}min")
        logger.info(f"Notificação com antecedência: {status['message_advance_hours']}h")

    def show_menu(self) -> None:
        """Exibe menu interativo"""
        while True:
            print("\n" + "="*60)
            print("MINISTÉRIO ILUMINAÇÃO - MENU PRINCIPAL")
            print("="*60)
            print("1. Configurar WhatsApp (QR Code)")
            print("2. Adicionar Contato")
            print("3. Listar Contatos")
            print("4. Enviar Notificações Agora")
            print("5. Status do Scheduler")
            print("6. Monitoramento Contínuo")
            print("0. Sair")
            print("="*60)
            
            choice = input("Selecione uma opção: ").strip()
            
            if choice == "1":
                self.setup_whatsapp_session()
            elif choice == "2":
                self.add_contact_interactive()
            elif choice == "3":
                self.list_contacts()
            elif choice == "4":
                # Exemplo de envio
                names_dates = {
                    "João Silva": "2024-04-15 19:30",
                    # Adicione mais conforme necessário
                }
                self.send_notification_to_all(names_dates)
            elif choice == "5":
                self.get_scheduler_status()
            elif choice == "6":
                self.start_continuous_monitoring()
                input("Pressione ENTER para sair do monitoramento...")
                self.scheduler_service.stop()
            elif choice == "0":
                logger.info("Encerrando aplicação...")
                self.scheduler_service.stop()
                break
            else:
                logger.warning("Opção inválida")


def main():
    """Função principal"""
    try:
        bot = MinisterioIluminacaoBot()
        bot.show_menu()
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
