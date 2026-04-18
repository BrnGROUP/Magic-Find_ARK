import pyautogui
import pytesseract
import cv2
import numpy as np
import time
from PIL import ImageGrab

# Caminho do tesseract (ajuste se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Coordenadas do botão Reroll
REROLL_X = 1200
REROLL_Y = 800

# Região onde aparece o texto (x1, y1, x2, y2)
REGION = (1000, 300, 1500, 800)

def capturar_texto():
    img = ImageGrab.grab(bbox=REGION)
    img_np = np.array(img)

    # Converter para escala de cinza
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    # Melhorar contraste
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCR
    texto = pytesseract.image_to_string(thresh)

    return texto

def extrair_magic_find(texto):
    linhas = texto.split('\n')
    
    for linha in linhas:
        if "Magic Find" in linha:
            try:
                valor = linha.split(':')[1]
                valor = valor.replace('%', '').strip()
                return float(valor)
            except:
                pass
    return 0

print("Iniciando automação... Pressione CTRL+C para parar.")

while True:
    # Clica no botão
    pyautogui.click(REROLL_X, REROLL_Y)

    time.sleep(2)  # espera atualizar

    texto = capturar_texto()
    magic = extrair_magic_find(texto)

    print(f"Magic Find atual: {magic}%")

    if magic >= 30:
        print("🔥 ENCONTROU ITEM BOM! PARANDO...")
        break