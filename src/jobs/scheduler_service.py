import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone
from typing import Callable, Optional, List, Dict

from src.config import (
    SCHEDULER_ENABLED,
    MESSAGE_ADVANCE_HOURS,
    CHECK_INTERVAL_MINUTES,
    TIMEZONE
)

logger = logging.getLogger(__name__)


class SchedulerService:
    """Serviço de agendamento para notificações automáticas"""

    def __init__(self):
        """Inicializa o scheduler"""
        self.scheduler = BackgroundScheduler(timezone=timezone(TIMEZONE))
        self.enabled = SCHEDULER_ENABLED
        self.message_advance_hours = MESSAGE_ADVANCE_HOURS
        self.check_interval_minutes = CHECK_INTERVAL_MINUTES
        self.job_id_counter = 0
        logger.info("Scheduler inicializado")

    def start(self) -> bool:
        """
        Inicia o scheduler
        
        Returns:
            True se iniciado com sucesso
        """
        try:
            if not self.enabled:
                logger.warning("Scheduler desabilitado nas configurações")
                return False

            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler iniciado")
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar scheduler: {e}")
            return False

    def stop(self) -> bool:
        """
        Para o scheduler
        
        Returns:
            True se parado com sucesso
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler parado")
            return True
        except Exception as e:
            logger.error(f"Erro ao parar scheduler: {e}")
            return False

    def add_interval_job(self, func: Callable, minutes: int = None, 
                        job_id: str = None, args: tuple = None) -> Optional[str]:
        """
        Adiciona uma tarefa repetida em intervalo
        
        Args:
            func: Função a executar
            minutes: Intervalo em minutos
            job_id: ID único do job
            args: Argumentos da função
            
        Returns:
            ID do job criado
        """
        try:
            minutes = minutes or self.check_interval_minutes
            job_id = job_id or f"job_{self.job_id_counter}"
            self.job_id_counter += 1

            self.scheduler.add_job(
                func=func,
                trigger=IntervalTrigger(minutes=minutes),
                id=job_id,
                args=args or (),
                replace_existing=True
            )
            logger.info(f"Job adicionado: {job_id} (intervalo: {minutes}min)")
            return job_id
        except Exception as e:
            logger.error(f"Erro ao adicionar job: {e}")
            return None

    def add_cron_job(self, func: Callable, hour: int, minute: int, 
                    job_id: str = None, args: tuple = None) -> Optional[str]:
        """
        Adiciona uma tarefa agendada para um horário específico
        
        Args:
            func: Função a executar
            hour: Hora (0-23)
            minute: Minuto (0-59)
            job_id: ID único do job
            args: Argumentos da função
            
        Returns:
            ID do job criado
        """
        try:
            job_id = job_id or f"cron_job_{self.job_id_counter}"
            self.job_id_counter += 1

            self.scheduler.add_job(
                func=func,
                trigger="cron",
                hour=hour,
                minute=minute,
                id=job_id,
                args=args or (),
                replace_existing=True
            )
            logger.info(f"Cron job adicionado: {job_id} ({hour:02d}:{minute:02d})")
            return job_id
        except Exception as e:
            logger.error(f"Erro ao adicionar cron job: {e}")
            return None

    def schedule_message(self, func: Callable, send_time: datetime, 
                        args: tuple = None, job_id: str = None) -> Optional[str]:
        """
        Agenda o envio de uma mensagem para um horário específico
        
        Args:
            func: Função de envio de mensagem
            send_time: Horário de envio
            args: Argumentos da função
            job_id: ID único do job
            
        Returns:
            ID do job criado
        """
        try:
            job_id = job_id or f"message_{self.job_id_counter}"
            self.job_id_counter += 1

            self.scheduler.add_job(
                func=func,
                trigger="date",
                run_date=send_time,
                id=job_id,
                args=args or (),
                replace_existing=True
            )
            logger.info(f"Mensagem agendada: {job_id} para {send_time}")
            return job_id
        except Exception as e:
            logger.error(f"Erro ao agendar mensagem: {e}")
            return None

    def remove_job(self, job_id: str) -> bool:
        """
        Remove um job agendado
        
        Args:
            job_id: ID do job a remover
            
        Returns:
            True se removido com sucesso
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removido: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Job não encontrado para remoção: {job_id}")
            return False

    def get_jobs(self) -> List[Dict]:
        """
        Retorna todos os jobs agendados
        
        Returns:
            Lista de dicionários com informações dos jobs
        """
        try:
            jobs_info = []
            for job in self.scheduler.get_jobs():
                jobs_info.append({
                    "id": job.id,
                    "func": str(job.func),
                    "trigger": str(job.trigger),
                    "next_run_time": job.next_run_time
                })
            return jobs_info
        except Exception as e:
            logger.error(f"Erro ao obter jobs: {e}")
            return []

    def pause_job(self, job_id: str) -> bool:
        """
        Pausa a execução de um job
        
        Args:
            job_id: ID do job
            
        Returns:
            True se pausado com sucesso
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                logger.info(f"Job pausado: {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao pausar job: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """
        Retoma a execução de um job
        
        Args:
            job_id: ID do job
            
        Returns:
            True se retomado com sucesso
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                logger.info(f"Job retomado: {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao retomar job: {e}")
            return False

    def get_scheduler_status(self) -> Dict:
        """
        Retorna o status do scheduler
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "running": self.scheduler.running,
            "enabled": self.enabled,
            "jobs_count": len(self.scheduler.get_jobs()),
            "timezone": TIMEZONE,
            "check_interval_minutes": self.check_interval_minutes,
            "message_advance_hours": self.message_advance_hours
        }
