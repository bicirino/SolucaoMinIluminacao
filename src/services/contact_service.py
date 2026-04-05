import json
import logging
from typing import Dict, Optional
from pathlib import Path
from src.config import CONTACTS_FILE_PATH

logger = logging.getLogger(__name__)


class ContactService:
    """Serviço para gerenciar contatos de escalas"""

    def __init__(self, file_path: str = CONTACTS_FILE_PATH):
        self.file_path = Path(file_path)
        self.contacts: Dict[str, str] = {}
        self._load_contacts()

    def _load_contacts(self) -> None:
        """Carrega contatos do arquivo JSON"""
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.contacts = data.get("contatos", {})
                logger.info(f"Contatos carregados: {len(self.contacts)} encontrados")
            else:
                logger.warning(f"Arquivo de contatos não encontrado: {self.file_path}")
                self.contacts = {}
        except Exception as e:
            logger.error(f"Erro ao carregar contatos: {e}")
            self.contacts = {}

    def get_contact(self, name: str) -> Optional[str]:
        """
        Retorna o número de WhatsApp de um contato pelo nome
        
        Args:
            name: Nome do contato na escala
            
        Returns:
            Número de WhatsApp ou None se não encontrado
        """
        # Tenta correspondência exata primeiro
        if name in self.contacts:
            return self.contacts[name]
        
        # Tenta correspondência case-insensitive
        for contact_name, phone in self.contacts.items():
            if contact_name.lower() == name.lower():
                return phone
        
        # Tenta correspondência parcial (primeiras letras)
        name_lower = name.lower()
        for contact_name, phone in self.contacts.items():
            if contact_name.lower().startswith(name_lower):
                return phone
        
        logger.warning(f"Contato não encontrado: {name}")
        return None

    def get_all_contacts(self) -> Dict[str, str]:
        """Retorna todos os contatos"""
        return self.contacts.copy()

    def add_contact(self, name: str, phone: str) -> bool:
        """
        Adiciona ou atualiza um contato
        
        Args:
            name: Nome do contato
            phone: Número de WhatsApp (formato: 55XXYYYYYYYYYY)
            
        Returns:
            True se adicionado com sucesso, False caso contrário
        """
        try:
            # Validação básica do número
            if not phone.startswith("55") or len(phone) < 12:
                logger.error(f"Número de WhatsApp inválido: {phone}")
                return False
            
            self.contacts[name] = phone
            self._save_contacts()
            logger.info(f"Contato adicionado: {name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar contato: {e}")
            return False

    def _save_contacts(self) -> None:
        """Salva contatos no arquivo JSON"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"contatos": self.contacts}, f, ensure_ascii=False, indent=2)
            logger.info("Contatos salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar contatos: {e}")

    def remove_contact(self, name: str) -> bool:
        """Remove um contato"""
        try:
            if name in self.contacts:
                del self.contacts[name]
                self._save_contacts()
                logger.info(f"Contato removido: {name}")
                return True
            logger.warning(f"Contato não encontrado para remoção: {name}")
            return False
        except Exception as e:
            logger.error(f"Erro ao remover contato: {e}")
            return False
