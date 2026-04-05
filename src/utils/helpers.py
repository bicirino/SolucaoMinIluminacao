import re
import logging
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)


class StringFormatter:
    """Utilitários para formatação de strings"""

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Remove caracteres especiais do número de telefone
        
        Args:
            phone: Número com formatação
            
        Returns:
            Número sem formatação
        """
        return re.sub(r"[^\d]", "", phone)

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Formata número para padrão brasileiro
        
        Args:
            phone: Número sem formatação
            
        Returns:
            Número formatado (55XX9YYYYYYY)
        """
        clean = StringFormatter.clean_phone_number(phone)
        if len(clean) >= 12:
            return f"+{clean[:2]} ({clean[2:4]}) {clean[4:9]}-{clean[9:]}"
        return clean

    @staticmethod
    def clean_name(name: str) -> str:
        """
        Limpa e normaliza um nome
        
        Args:
            name: Nome a limpar
            
        Returns:
            Nome normalizado
        """
        # Remove espaços extras
        name = " ".join(name.split())
        # Capitaliza primeira letra de cada palavra
        name = name.title()
        return name

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Valida se é um número de WhatsApp válido
        
        Args:
            phone: Número a validar
            
        Returns:
            True se válido
        """
        clean = StringFormatter.clean_phone_number(phone)
        return clean.startswith("55") and len(clean) >= 12


class DateTimeHelper:
    """Utilitários para datas e horas"""

    @staticmethod
    def parse_date_string(date_str: str, format: str = "%d/%m/%Y") -> datetime:
        """
        Parseia string de data
        
        Args:
            date_str: String da data
            format: Formato esperado
            
        Returns:
            Objeto datetime
        """
        try:
            return datetime.strptime(date_str, format)
        except ValueError as e:
            logger.error(f"Erro ao parsear data: {e}")
            return None

    @staticmethod
    def format_date(date: datetime, format: str = "%d/%m/%Y") -> str:
        """
        Formata data para string
        
        Args:
            date: Objeto datetime
            format: Formato desejado
            
        Returns:
            Data formatada
        """
        return date.strftime(format)

    @staticmethod
    def get_weekday_name(date: datetime, locale: str = "pt_BR") -> str:
        """
        Retorna nome do dia da semana
        
        Args:
            date: Objeto datetime
            locale: Localidade
            
        Returns:
            Nome do dia
        """
        weekdays = {
            "pt_BR": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        }
        
        weekday_list = weekdays.get(locale, weekdays["pt_BR"])
        return weekday_list[date.weekday()]


class ListProcessor:
    """Utilitários para processamento de listas"""

    @staticmethod
    def remove_duplicates(items: List[str], case_sensitive: bool = False) -> List[str]:
        """
        Remove itens duplicados mantendo ordem
        
        Args:
            items: Lista de itens
            case_sensitive: Se deve diferenciar maiúsculas/minúsculas
            
        Returns:
            Lista sem duplicatas
        """
        seen = set()
        result = []
        
        for item in items:
            item_key = item if case_sensitive else item.lower()
            if item_key not in seen:
                seen.add(item_key)
                result.append(item)
        
        return result

    @staticmethod
    def filter_empty(items: List[str]) -> List[str]:
        """
        Remove strings vazias
        
        Args:
            items: Lista de strings
            
        Returns:
            Lista sem vazias
        """
        return [item.strip() for item in items if item.strip()]

    @staticmethod
    def split_by_length(text: str, max_length: int = 1000) -> List[str]:
        """
        Separa texto em partes de tamanho máximo
        Útil para cumprir limite de caracteres do WhatsApp (~1000)
        
        Args:
            text: Texto a separar
            max_length: Tamanho máximo de cada parte
            
        Returns:
            Lista de partes
        """
        parts = []
        current = ""
        
        for word in text.split():
            if len(current) + len(word) + 1 <= max_length:
                current += word + " "
            else:
                if current:
                    parts.append(current.strip())
                current = word + " "
        
        if current:
            parts.append(current.strip())
        
        return parts


class MessageBuilder:
    """Builder para criar mensagens padronizadas"""

    @staticmethod
    def build_reminder_message(person_name: str, event_date: str, event_time: str) -> str:
        """
        Constrói mensagem de lembrança
        
        Args:
            person_name: Nome da pessoa
            event_date: Data do evento (formato: DD/MM)
            event_time: Hora do evento (formato: HH:MM)
            
        Returns:
            Mensagem formatada
        """
        message = f"""
Oi {person_name}! 👋

📢 Lembrancinha importante! 📢

Você está escalado(a) para o ministério de iluminação:

📅 Data: {event_date}
🕐 Horário: {event_time}

Que Deus te abençoe! 🙏✨

---
*Mensagem automática - Sistema de Escalas*
        """.strip()
        
        return message

    @staticmethod
    def build_confirmation_message(event_count: int) -> str:
        """
        Constrói mensagem de confirmação
        
        Args:
            event_count: Quantidade de eventos
            
        Returns:
            Mensagem de confirmação
        """
        return f"✓ {event_count} notificações foram enviadas com sucesso!"


def validate_environment() -> bool:
    """
    Valida se o ambiente está configurado corretamente
    
    Returns:
        True se válido
    """
    try:
        from src.config import (
            CONTACTS_FILE_PATH,
            GOOGLE_CLOUD_CREDENTIALS_PATH,
            LOG_FILE
        )
        
        logger.info("✓ Configurações carregadas")
        return True
    except Exception as e:
        logger.error(f"✗ Erro na validação do ambiente: {e}")
        return False
