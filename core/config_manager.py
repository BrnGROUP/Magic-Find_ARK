"""
BRN Reroll Analyzer - Gerenciador de Configurações
Responsável por carregar, salvar e gerenciar todas as configurações do sistema.
"""

import json
import os
from datetime import datetime

# Caminho padrão do arquivo de configuração
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

# Configurações padrão (Otimizadas para 1366x768)
DEFAULT_CONFIG = {
    "reroll_x": 683,
    "reroll_y": 560,
    "item_hover_x": 1050,
    "item_hover_y": 350,
    "capture_region": [980, 200, 1330, 750],
    "min_magic_find": 30.0,
    "click_delay": 2.5,
    "hover_delay": 1.5,
    "mode": "ocr",
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "emergency_key": "esc",
    "history": []
}


class ConfigManager:
    """Gerencia as configurações do sistema com persistência em JSON."""

    def __init__(self, config_path=None):
        self.config_path = config_path or CONFIG_PATH
        self.config = {}
        self.load()

    def load(self):
        """Carrega configurações do arquivo JSON."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # Preenche campos faltantes com valores padrão
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self.config:
                        self.config[key] = value
            else:
                self.config = DEFAULT_CONFIG.copy()
                self.save()
        except (json.JSONDecodeError, IOError):
            self.config = DEFAULT_CONFIG.copy()
            self.save()

    def save(self):
        """Salva configurações no arquivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[ConfigManager] Erro ao salvar configurações: {e}")

    def get(self, key, default=None):
        """Retorna o valor de uma configuração."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Define o valor de uma configuração e salva."""
        self.config[key] = value
        self.save()

    def get_reroll_position(self):
        """Retorna a posição (x, y) do botão Reroll."""
        return (self.config.get("reroll_x", 960), self.config.get("reroll_y", 540))

    def get_item_hover_position(self):
        """Retorna a posição (x, y) do item para hover (exibir tooltip)."""
        return (self.config.get("item_hover_x", 960), self.config.get("item_hover_y", 400))

    def get_hover_delay(self):
        """Retorna o delay de espera após mover o mouse ao item (para tooltip aparecer)."""
        return self.config.get("hover_delay", 1.0)

    def get_capture_region(self):
        """Retorna a região de captura como tupla (x1, y1, x2, y2)."""
        region = self.config.get("capture_region", [800, 200, 1200, 600])
        return tuple(region)

    def get_min_magic_find(self):
        """Retorna o valor mínimo de Magic Find desejado."""
        return self.config.get("min_magic_find", 30.0)

    def get_click_delay(self):
        """Retorna o delay entre cliques em segundos."""
        return self.config.get("click_delay", 2.0)

    def get_mode(self):
        """Retorna o modo de detecção (ocr ou image)."""
        return self.config.get("mode", "ocr")

    def get_tesseract_path(self):
        """Retorna o caminho do executável do Tesseract."""
        return self.config.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    def add_history_entry(self, magic_find_value):
        """Adiciona uma entrada ao histórico de resultados."""
        entry = {
            "value": magic_find_value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if "history" not in self.config:
            self.config["history"] = []
        self.config["history"].append(entry)
        # Manter apenas os últimos 500 registros
        if len(self.config["history"]) > 500:
            self.config["history"] = self.config["history"][-500:]
        self.save()
        return entry

    def get_history(self):
        """Retorna o histórico de resultados."""
        return self.config.get("history", [])

    def clear_history(self):
        """Limpa o histórico de resultados."""
        self.config["history"] = []
        self.save()

    def export_history_csv(self, filepath):
        """Exporta o histórico para um arquivo CSV."""
        import csv
        history = self.get_history()
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data/Hora", "Magic Find (%)"])
                for entry in history:
                    writer.writerow([entry.get("timestamp", ""), entry.get("value", "")])
            return True
        except IOError:
            return False
