"""
BRN Reroll Analyzer - Leitor OCR
Responsável por extrair texto da tela e identificar o valor de Magic Find.
"""

import re
import pytesseract
import numpy as np


class OCRReader:
    """Leitor OCR especializado em extrair valores de Magic Find."""

    def __init__(self, tesseract_path=None):
        """
        Inicializa o leitor OCR.
        
        Args:
            tesseract_path: Caminho para o executável do Tesseract.
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.last_raw_text = ""
        self.last_extracted_value = 0.0
        self.confidence = 0.0

    def set_tesseract_path(self, path):
        """Define o caminho do Tesseract."""
        pytesseract.pytesseract.tesseract_cmd = path

    def extract_text(self, image, psm=6):
        """
        Extrai texto de uma imagem processada.
        """
        if image is None:
            return ""

        try:
            custom_config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(image, config=custom_config)
            self.last_raw_text = text
            return text
        except Exception as e:
            print(f"[OCRReader] Erro na extração de texto: {e}")
            return ""

    def extract_text_with_data(self, image, psm=6):
        """
        Extrai texto com dados de confiança do OCR.
        """
        if image is None:
            return "", 0.0

        try:
            custom_config = f'--oem 3 --psm {psm}'
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            words = []
            confidences = []
            
            if 'text' in data:
                for i, word in enumerate(data['text']):
                    if i < len(data['conf']):
                        conf = int(data['conf'][i])
                        if conf > 20 and word.strip():
                            words.append(word)
                            confidences.append(conf)
            
            text = " ".join(words)
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            
            self.last_raw_text = text
            self.confidence = avg_conf
            
            return text, avg_conf

        except Exception as e:
            print(f"[OCRReader] Erro na extração com dados: {e}")
            return "", 0.0

    def extract_magic_find(self, text):
        """
        Extrai o valor de Magic Find do texto de forma ultra-robusta.
        """
        if not text:
            return 0.0

        # Heurística agressiva: Limpeza e normalização
        def normalize_text(t):
            t = t.replace(',', '.')
            # Corrigir erros comuns onde números são lidos como letras
            t = re.sub(r'\bI([0-9])', r'1\g<1>', t) # I7 -> 17
            t = re.sub(r'\bl([0-9])', r'1\g<1>', t) # l7 -> 17
            t = re.sub(r'([0-9])O\b', r'\g<1>0', t) # 2O -> 20
            return t

        text_clean = normalize_text(text)
        
        try:
            # 1. Tentar padrões Regex específicos
            patterns = [
                r'Magic\s*Find\s*Increased\s*By\s*%\s*[:\-]?\s*(\d+[\.,]?\d*)',
                r'Magic\s*Find.*?(\d+[\.,]?\d*)',
                r'Magic.*?Find.*?(\d+[\.,]?\d*)',
                r'Magic.*?(\d+[\.,]?\d*)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_clean, re.IGNORECASE)
                if match:
                    try:
                        val = float(match.group(1).replace(',', '.'))
                        if 0.1 <= val <= 300.0:
                            self.last_extracted_value = val
                            return val
                    except: continue

            # 2. Fallback por linha: Procurar "Magic" e pegar o número MAIS PRÓXIMO NELA
            lines = text_clean.split('\n')
            for line in lines:
                line_lc = line.lower()
                if 'magic' in line_lc and 'find' in line_lc:
                    # Isolar a parte da linha APÓS o termo "Magic Find"
                    parts = re.split(r'find|:', line, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        target_area = parts[-1]
                        nums = re.findall(r'(\d+[\.,]\d+|\d+)', target_area)
                        if nums:
                            try:
                                val = float(nums[0].replace(',', '.'))
                                if 0.1 <= val <= 300.0:
                                    self.last_extracted_value = val
                                    return val
                            except: pass

            return 0.0

        except Exception as e:
            print(f"[OCRReader] Erro ao extrair Magic Find: {e}")
            return 0.0

    def process_image(self, image, enhance_green=False, psm=6):
        """
        Pipeline completo: extrai texto e Magic Find de uma imagem.
        
        Args:
            image: Imagem processada.
            enhance_green: Se True, tenta com foco em texto colorido primeiro.
            psm: Modo de segmentação do Tesseract.
            
        Returns:
            tuple: (valor_magic_find, texto_raw, confiança)
        """
        text, confidence = self.extract_text_with_data(image, psm=psm)
        magic_find = self.extract_magic_find(text)
        
        return magic_find, text, confidence

    def get_last_raw_text(self):
        """Retorna o último texto bruto extraído."""
        return self.last_raw_text

    def get_confidence(self):
        """Retorna a confiança da última leitura."""
        return self.confidence
