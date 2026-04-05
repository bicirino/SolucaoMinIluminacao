import logging
from typing import List, Dict, Optional
from pathlib import Path
from google.cloud import vision
from src.config import GOOGLE_CLOUD_CREDENTIALS_PATH, GOOGLE_PROJECT_ID

logger = logging.getLogger(__name__)


class VisionOCRService:
    """Serviço para leitura de imagens usando Google Cloud Vision API"""

    def __init__(self):
        """Inicializa o cliente do Google Cloud Vision"""
        try:
            # Configura as credenciais
            import os
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_CREDENTIALS_PATH
            
            self.client = vision.ImageAnnotatorClient()
            logger.info("Cliente Google Cloud Vision inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Cloud Vision: {e}")
            raise

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando OCR
        
        Args:
            image_path: Caminho da imagem a processar
            
        Returns:
            Texto extraído da imagem
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                logger.error(f"Arquivo não encontrado: {image_path}")
                return ""

            # Lê a imagem
            with open(image_path, "rb") as f:
                image_content = f.read()

            # Cria a requisição de OCR
            image = vision.Image(content=image_content)
            response = self.client.document_text_detection(image=image)

            if response.error.message:
                logger.error(f"Erro na requisição Google Vision: {response.error.message}")
                return ""

            # Extrai o texto
            text = response.full_text_annotation.text
            logger.info(f"Texto extraído de {image_path.name}: {len(text)} caracteres")
            return text

        except Exception as e:
            logger.error(f"Erro ao extrair texto da imagem: {e}")
            return ""

    def extract_names_from_scale(self, image_path: str) -> List[str]:
        """
        Extrai nomes de pessoas da escala (imagem PNG)
        
        Args:
            image_path: Caminho da imagem da escala
            
        Returns:
            Lista de nomes encontrados na escala
        """
        try:
            text = self.extract_text_from_image(image_path)
            if not text:
                logger.warning("Nenhum texto foi extraído da imagem")
                return []

            # Processa o texto para extrair nomes
            # Aqui você pode adicionar lógica específica para seu caso
            names = self._parse_scale_text(text)
            logger.info(f"Nomes extraídos: {names}")
            return names

        except Exception as e:
            logger.error(f"Erro ao extrair nomes da escala: {e}")
            return []

    def _parse_scale_text(self, text: str) -> List[str]:
        """
        Processa o texto extraído e retorna lista de nomes
        
        Args:
            text: Texto completo extraído da imagem
            
        Returns:
            Lista de nomes únicos
        """
        # Remove linhas vazias e muito curtas
        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if len(line) > 2]

        # Filtra linhas que provavelmente são nomes
        names = []
        for line in lines:
            # Remove números, datas e caracteres especiais comuns
            # Mantém apenas linhas com pelo menos 2 palavras ou palavras maiúsculas
            if any(char.isupper() for char in line) and not any(
                char.isdigit() for char in line
            ):
                # Limpa a linha
                cleaned = line.strip()
                if cleaned and len(cleaned) > 2:
                    names.append(cleaned)

        # Remove duplicatas mantendo ordem
        seen = set()
        unique_names = []
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)

        return unique_names

    def get_image_properties(self, image_path: str) -> Optional[Dict]:
        """
        Retorna propriedades da imagem
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Dicionário com propriedades da imagem
        """
        try:
            with open(image_path, "rb") as f:
                image_content = f.read()

            image = vision.Image(content=image_content)
            response = self.client.image_properties(image=image)

            if response.error.message:
                logger.error(f"Erro ao obter propriedades: {response.error.message}")
                return None

            colors = response.image_properties.dominant_colors.colors
            return {
                "colors_found": len(colors),
                "image_size": len(image_content),
                "dominant_color": colors[0] if colors else None
            }

        except Exception as e:
            logger.error(f"Erro ao obter propriedades da imagem: {e}")
            return None
