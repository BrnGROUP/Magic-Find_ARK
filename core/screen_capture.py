"""
BRN Reroll Analyzer - Captura de Tela
Responsável por capturar regiões da tela e pré-processar imagens para OCR.
"""

import cv2
import numpy as np
from PIL import ImageGrab


class ScreenCapture:
    """Captura e processa regiões da tela para análise."""

    def __init__(self):
        self.last_capture = None
        self.last_processed = None

    def capture_region(self, region):
        """
        Captura uma região específica da tela.
        
        Args:
            region: Tupla (x1, y1, x2, y2) definindo a região de captura.
            
        Returns:
            numpy.ndarray: Imagem capturada como array NumPy (BGR).
        """
        try:
            img = ImageGrab.grab(bbox=region)
            img_np = np.array(img)
            # PIL retorna RGB, converter para BGR para OpenCV
            self.last_capture = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            return self.last_capture.copy()
        except Exception as e:
            print(f"[ScreenCapture] Erro na captura: {e}")
            return None

    def capture_full_screen(self):
        """Captura a tela inteira."""
        try:
            img = ImageGrab.grab()
            img_np = np.array(img)
            self.last_capture = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            return self.last_capture.copy()
        except Exception as e:
            print(f"[ScreenCapture] Erro na captura full-screen: {e}")
            return None

    def preprocess_for_ocr(self, image, enhance_green=False, invert=False):
        """
        Pré-processa imagem para melhorar a acurácia do OCR em textos com contorno (ARK).
        """
        if image is None:
            return None

        try:
            # 1. Redimensionar primeiro para processar em alta resolução
            scale_factor = 2
            h, w = image.shape[:2]
            img = cv2.resize(image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)

            if enhance_green:
                # Converter para HSV
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                
                # Máscaras ultra-amplas para capturar texto com transparência/fundo escuro
                # Verde
                mask_green = cv2.inRange(hsv, np.array([30, 30, 40]), np.array([95, 255, 255]))
                # Ciano/Azul (Random Stats) - Pegando desde o cinza-azulado até o ciano brilhante
                mask_cyan = cv2.inRange(hsv, np.array([75, 10, 80]), np.array([130, 255, 255]))
                # Branco/Valores
                mask_white = cv2.inRange(hsv, np.array([0, 0, 100]), np.array([180, 80, 255]))
                
                mask = cv2.bitwise_or(mask_green, mask_cyan)
                mask = cv2.bitwise_or(mask, mask_white)
                
                # Isolar apenas o texto colorido
                result = cv2.bitwise_and(img, img, mask=mask)
                gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if invert:
                gray = cv2.bitwise_not(gray)

            # 2. Suavização para eliminar contornos finos e serrilhados (Anti-Aliasing)
            # Isso ajuda o OCR a ver a letra como um bloco sólido e não como linha+fundo
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # 3. Aumentar contraste
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # 4. Binarização inteligente
            # Usamos uma combinação de Threshold global (Otsu) e Adaptativo
            _, thresh_otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh_adapt = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
            
            # Mesclar os dois reduz ruído de fundo preservando as letras
            final_thresh = cv2.bitwise_and(thresh_otsu, thresh_adapt)

            # 5. Operação morfológica leve para "engrossar" letras que podem estar falhadas
            kernel = np.ones((2, 2), np.uint8)
            final_thresh = cv2.dilate(final_thresh, kernel, iterations=1)

            self.last_processed = final_thresh
            return final_thresh

        except Exception as e:
            print(f"[ScreenCapture] Erro no pré-processamento v2: {e}")
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            except:
                return None

    def get_capture_preview(self, region, max_size=(400, 300)):
        """
        Captura e redimensiona uma região para preview na interface.
        
        Args:
            region: Tupla (x1, y1, x2, y2).
            max_size: Tamanho máximo (largura, altura) do preview.
            
        Returns:
            numpy.ndarray: Imagem redimensionada para preview.
        """
        img = self.capture_region(region)
        if img is None:
            return None

        h, w = img.shape[:2]
        max_w, max_h = max_size

        # Calcular escala mantendo proporção
        scale = min(max_w / w, max_h / h)
        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        return img
