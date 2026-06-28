"""
BRN Reroll Analyzer - Módulo de Auto-Clique Rápido (Burst Clicker)
Detecta cliques físicos rápidos do usuário e simula instantaneamente um burst de cliques.
"""

import ctypes
from ctypes import wintypes
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# Windows API constants
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201

# Windows API structures
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", ctypes.c_ulong),
        ("flags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_ulonglong)
    ]

# Load DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Configure ctypes signatures to prevent 64-bit handle truncation issues
user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int,
    ctypes.c_void_p,
    wintypes.HINSTANCE,
    wintypes.DWORD
]
user32.SetWindowsHookExW.restype = ctypes.c_void_p

user32.UnhookWindowsHookEx.argtypes = [
    ctypes.c_void_p
]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.CallNextHookEx.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
]
user32.CallNextHookEx.restype = ctypes.c_longlong

kernel32.GetModuleHandleW.argtypes = [
    wintypes.LPCWSTR
]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE


class AutoClicker(QObject):
    """
    Gerencia o monitoramento de cliques globais e simula bursts rápidos de cliques.
    Funciona em segundo plano e se integra com o loop do PyQt5.
    """
    triggered = pyqtSignal(int)      # Disparado ao iniciar o burst (quantidade)
    click_detected = pyqtSignal(int) # Disparado a cada clique físico válido (contador atual)
    log_message = pyqtSignal(str)     # Emite mensagens de log/status para a UI

    _instance = None  # Referência estática para o callback de Hook do Windows

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self._hook_handle = None
        self._callback_ref = None
        self._click_times = []
        self._is_simulating = False
        AutoClicker._instance = self

    def start(self):
        """Ativa o monitoramento global de cliques."""
        if self._hook_handle is not None:
            return True

        self._click_times.clear()
        self._is_simulating = False

        # Define o tipo da função de callback do hook
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        self._callback_ref = HOOKPROC(AutoClicker._hook_callback)

        # Instala o hook global de mouse de baixo nível
        self._hook_handle = user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            self._callback_ref,
            kernel32.GetModuleHandleW(None),
            0
        )

        if not self._hook_handle:
            error_code = kernel32.GetLastError()
            self.log_message.emit(f"❌ Falha ao instalar monitor de mouse (Hook). Código de Erro: {error_code}")
            return False
        
        self.log_message.emit("🟢 Monitor de cliques ativado! (Aguardando cliques rápidos)")
        return True

    def stop(self):
        """Desativa o monitoramento de cliques."""
        if self._hook_handle is not None:
            user32.UnhookWindowsHookEx(self._hook_handle)
            self._hook_handle = None
            self._callback_ref = None
            self.log_message.emit("🔴 Monitor de cliques desativado.")

    def is_active(self):
        """Verifica se o monitoramento está rodando."""
        return self._hook_handle is not None

    @staticmethod
    def _hook_callback(nCode, wParam, lParam):
        """Callback executado pelo Windows a cada evento de mouse global."""
        instance = AutoClicker._instance
        
        if instance and nCode >= 0 and not instance._is_simulating:
            if wParam == WM_LBUTTONDOWN:
                try:
                    # Carregar dados da estrutura
                    data = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                    # LLMHF_INJECTED (bit 0) identifica se o evento foi simulado por software
                    is_injected = bool(data.flags & 1)
                    
                    if not is_injected:
                        # Executa o processamento do clique de forma assíncrona para liberar o Hook imediatamente
                        # Evita lentidão no mouse caso a thread do PyQt esteja ocupada
                        QTimer.singleShot(0, instance._on_physical_click)
                except Exception as e:
                    print(f"[AutoClicker] Erro no hook: {e}")

        # Passa o evento para o próximo Hook na fila do Windows
        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def _on_physical_click(self):
        """Processa um clique físico do usuário."""
        if self._is_simulating:
            return

        now = time.time()
        window = self.config.get_autoclick_time_window()
        
        # Filtra os cliques mantendo apenas os dentro da janela de tempo configurada
        self._click_times = [t for t in self._click_times if now - t <= window]
        self._click_times.append(now)

        trigger_clicks = self.config.get_autoclick_trigger_clicks()
        current_count = len(self._click_times)
        
        # Emite sinal indicando a detecção
        self.click_detected.emit(current_count)

        if current_count >= trigger_clicks:
            # Reseta o histórico para evitar ativações repetitivas no próximo clique
            self._click_times.clear()
            
            burst_clicks = self.config.get_autoclick_burst_clicks()
            self.log_message.emit(f"🔥 {trigger_clicks} cliques seguidos! Iniciando autoclick de {burst_clicks}x...")
            
            # Bloqueia detecção de novos cliques e dispara o burst
            self._is_simulating = True
            self.triggered.emit(burst_clicks)
            QTimer.singleShot(0, self._perform_burst)

    def _perform_burst(self):
        """Simula o burst de cliques."""
        try:
            burst_clicks = self.config.get_autoclick_burst_clicks()
            
            # Executa cliques de forma rápida
            # MOUSEEVENTF_LEFTDOWN = 0x0002
            # MOUSEEVENTF_LEFTUP = 0x0004
            for _ in range(burst_clicks):
                user32.mouse_event(0x0002, 0, 0, 0, 0)
                user32.mouse_event(0x0004, 0, 0, 0, 0)
            
            self.log_message.emit(f"✅ Executados {burst_clicks} cliques com sucesso!")
        except Exception as e:
            self.log_message.emit(f"❌ Erro ao simular cliques: {e}")
        finally:
            # Pequena pausa antes de reativar a escuta para garantir que o Windows processe
            # os eventos pendentes na fila de mensagens sem auto-detecção recursiva
            QTimer.singleShot(200, self._reset_simulation_flag)

    def _reset_simulation_flag(self):
        """Reativa a captura de novos cliques do usuário."""
        self._is_simulating = False
