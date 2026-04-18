# BRN Reroll Analyzer – Automação Inteligente para ARK Survival Evolved

<p align="center">
  <strong>⚡ BRN Reroll Analyzer v1.0.0</strong><br>
  Automação inteligente de rerolls para Magic Find no ARK Survival Evolved
</p>

---

## 🎯 O que faz?

Automatiza o processo de reroll de itens no ARK Survival Evolved, detectando o valor de **Magic Find** via OCR e parando automaticamente quando a meta é atingida.

## 🏗️ Arquitetura

```
brn_reroll_analyzer/
├── main.py                    # Ponto de entrada
├── config.json                # Configurações persistentes
├── requirements.txt           # Dependências
│
├── core/                      # Backend / Lógica
│   ├── analyzer.py            # Motor de automação (worker thread)
│   ├── clicker.py             # Automação de cliques (PyAutoGUI)
│   ├── screen_capture.py      # Captura e processamento de tela
│   ├── ocr_reader.py          # Leitura OCR (Tesseract)
│   └── config_manager.py      # Gerenciador de configurações
│
├── ui/                        # Frontend / Interface
│   ├── main_window.py         # Janela principal + sidebar
│   ├── dashboard.py           # Dashboard com cards
│   ├── automation.py          # Controles de automação
│   ├── settings.py            # Configurações
│   ├── history.py             # Histórico de rolls
│   └── styles.py              # Design system (BRN UI)
│
├── assets/                    # Recursos visuais
└── logs/                      # Logs de execução
```

## ⚙️ Requisitos

- **Python 3.8+**
- **Tesseract OCR** instalado ([download](https://github.com/UB-Mannheim/tesseract/wiki))
- Windows 10/11

## 🚀 Instalação

```bash
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar Tesseract OCR
# Baixe de: https://github.com/UB-Mannheim/tesseract/wiki
# Instale em: C:\Program Files\Tesseract-OCR\

# 3. Executar
python main.py
```

## 📊 Telas

| Tela | Descrição |
|------|-----------|
| **Dashboard** | Status em tempo real, cards de estatísticas, barra de progresso |
| **Automação** | START/STOP/PAUSE, preview da captura, log de execução |
| **Configurações** | Posição do botão, região de captura, meta, modo OCR |
| **Histórico** | Tabela de resultados, exportação CSV, estatísticas |

## 🛡️ Segurança

- **ESC** = Parada de emergência imediata
- **PyAutoGUI Failsafe** = Mover mouse ao canto superior esquerdo para abortar
- Delays humanizados para evitar detecção

## 📦 Gerar Executável

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="BRN_Reroll_Analyzer" --icon=assets/icon.ico main.py
```

## 🔧 Configuração

As configurações são salvas automaticamente em `config.json`:
- Coordenadas do botão Reroll
- Região de captura da tela
- Meta de Magic Find (%)
- Delay entre cliques
- Modo de detecção (OCR / Imagem)
- Histórico completo

---

**BRN GROUP** © 2026 – Todos os direitos reservados