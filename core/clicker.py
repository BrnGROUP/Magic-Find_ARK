"""
BRN Reroll Analyzer - Módulo de Clique Automatizado
Responsável por automatizar os cliques no botão Reroll com segurança.
"""

import pyautogui
import time
import random


# Segurança do PyAutoGUI
pyautogui.FAILSAFE = True  # Mover mouse ao canto superior esquerdo para abortar
pyautogui.PAUSE = 0.1       # Pequena pausa entre ações


class Clicker:
    """Automação de cliques com segurança e variação humanizada."""

    def __init__(self):
        self.click_count = 0
        self.is_active = False
        self.last_click_time = 0

    def click_reroll(self, x, y, humanize=True):
        """
        Realiza um clique na posição do botão Reroll.
        
        Args:
            x: Coordenada X do botão.
            y: Coordenada Y do botão.
            humanize: Adiciona pequena variação para simular comportamento humano.
            
        Returns:
            bool: True se o clique foi realizado com sucesso.
        """
        try:
            if humanize:
                # Pequena variação aleatória na posição (±3 pixels)
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                target_x = x + offset_x
                target_y = y + offset_y
            else:
                target_x = x
                target_y = y

            # Mover o mouse suavemente e clicar
            pyautogui.moveTo(target_x, target_y, duration=0.15)
            pyautogui.click(target_x, target_y)
            
            self.click_count += 1
            self.last_click_time = time.time()
            
            return True

        except pyautogui.FailSafeException:
            print("[Clicker] ⚠️ Failsafe ativado! Mouse no canto superior esquerdo.")
            self.is_active = False
            return False
        except Exception as e:
            print(f"[Clicker] Erro no clique: {e}")
            return False

    def wait(self, delay, jitter=True):
        """
        Aguarda antes do próximo clique.
        
        Args:
            delay: Tempo de espera em segundos.
            jitter: Adiciona variação aleatória no tempo.
        """
        if jitter:
            # Adiciona ±15% de variação no delay
            variation = delay * 0.15
            actual_delay = delay + random.uniform(-variation, variation)
            actual_delay = max(0.5, actual_delay)  # Mínimo de 0.5s
        else:
            actual_delay = delay

        time.sleep(actual_delay)

    def get_click_count(self):
        """Retorna o número total de cliques realizados."""
        return self.click_count

    def reset_count(self):
        """Reseta o contador de cliques."""
        self.click_count = 0

    @staticmethod
    def get_mouse_position():
        """Retorna a posição atual do mouse."""
        return pyautogui.position()

    def move_to(self, x, y, duration=0.2):
        """
        Move o mouse suavemente para uma posição.
        Usado para mover ao item após clicar no Reroll.
        
        Args:
            x: Coordenada X destino.
            y: Coordenada Y destino.
            duration: Duração do movimento em segundos.
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except pyautogui.FailSafeException:
            print("[Clicker] ⚠️ Failsafe ativado!")
            self.is_active = False
        except Exception as e:
            print(f"[Clicker] Erro ao mover mouse: {e}")

    @staticmethod
    def move_mouse_to(x, y):
        """Move o mouse para uma posição específica."""
        pyautogui.moveTo(x, y, duration=0.3)

