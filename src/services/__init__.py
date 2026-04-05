"""
Módulo de serviços da aplicação.

Contém os serviços principais:
- ContactService: Gerenciamento de contatos
- VisionOCRService: Leitura e OCR de imagens
- WhatsAppBotService: Integração com WhatsApp
"""

from .contact_service import ContactService
from .vision_ocr_service import VisionOCRService
from .whatsapp_bot_service import WhatsAppBotService

__all__ = [
    "ContactService",
    "VisionOCRService",
    "WhatsAppBotService",
]
