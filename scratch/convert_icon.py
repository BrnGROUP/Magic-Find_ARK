from PIL import Image
import os

img_path = r'C:\Users\claud\.gemini\antigravity\brain\8844fa18-6e48-4253-b06e-213c9e6a19bc\icon_ark_magic_find_1776538023503.png'
save_path = r'd:\PROJETOS\Magic-Find_ARK\Magic-Find_ARK\assets\icon.ico'

if os.path.exists(img_path):
    img = Image.open(img_path)
    # Ensure it's square and high res
    img.save(save_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Icon saved to {save_path}")
else:
    print(f"Image not found at {img_path}")
