# Web Remote Desktop

> 🌐 **Language:** **English** | [Русский (README_Ru.md)](README_Ru.md)

A low-latency browser-based remote desktop (KVM) streaming server built with **FastAPI** and **WebSockets**.

## ✨ Features
- 🖥️ **Real-Time Screen Streaming (~30 FPS)** — fast monitor capture via `mss`, JPEG frame compression (`Pillow`), and binary streaming over WebSockets.
- 🖱️ **Remote Mouse & Keyboard Control** — captures cursor coordinates, clicks, and keystrokes in the browser and emulates native host input via `pynput`.
- 🌐 **Zero-Client Architecture** — requires nothing more than a modern web browser to connect.

## 🚀 Installation & Usage

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
