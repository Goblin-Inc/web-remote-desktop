import asyncio
import io
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from mss import mss
from PIL import Image
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

app = FastAPI()
mouse = MouseController()
keyboard = KeyboardController()

# Чтение HTML-шаблона
with open("templates/index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

@app.get("/")
async def get():
    return HTMLResponse(html_code)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Задача для отправки видеопотока
    async def send_frames():
        with mss() as sct:
            monitor = sct.monitors[1]  # Основной монитор
            while True:
                try:
                    # Захват экрана
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    # Уменьшаем разрешение для высокой скорости (например, до width=1280)
                    img.thumbnail((1280, 720))
                    
                    # Сжатие в JPEG
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=50)
                    frame_bytes = buffer.getvalue()
                    
                    # Отправка кадров в бинарном виде
                    await websocket.send_bytes(frame_bytes)
                    await asyncio.sleep(0.03)  # ~30 FPS
                except Exception:
                    break

    # Задача для приема команд от браузера
    async def receive_input():
        while True:
            try:
                data = await websocket.receive_json()
                event_type = data.get("type")

                if event_type == "mousemove":
                    # data['x'] и data['y'] в процентах (0.0 - 1.0)
                    with mss() as sct:
                        mon = sct.monitors[1]
                        abs_x = mon["left"] + int(data["x"] * mon["width"])
                        abs_y = mon["top"] + int(data["y"] * mon["height"])
                        mouse.position = (abs_x, abs_y)

                elif event_type == "click":
                    btn = Button.left if data.get("button") == 0 else Button.right
                    mouse.click(btn)

                elif event_type == "keydown":
                    key = data.get("key")
                    if len(key) == 1:
                        keyboard.press(key)
                        keyboard.release(key)

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Input error: {e}")

    # Запускаем две задачи параллельно
    try:
        await asyncio.gather(send_frames(), receive_input())
    except Exception:
        pass