import asyncio
import json
import websockets
from src.ConfigManager.ConfigManager import ConfigManager
from src.logger import logger


class ParserClient:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.config_manager = ConfigManager()

    async def connect(self):
        """
        Підключається до WebSocket сервера і слухає оновлення.
        """
        async with websockets.connect(self.websocket_url) as websocket:
            await logger.info("[✅] Підключено до WebSocket сервера")
            try:
                while True:
                    message = await websocket.recv()
                    await self.handle_message(message)
            except websockets.exceptions.ConnectionClosed:
                await logger.info("[⚠] WebSocket з'єднання закрито")
            except Exception as e:
                await logger.error(f"[❌] Помилка WebSocket: {e}")

    async def handle_message(self, message):
        """
        Обробляє отримані повідомлення від сервера.
        """
        try:
            data = json.loads(message)
            if data.get("event") == "WEBHOOK_UPDATED":
                new_webhook = data.get("WEBHOOK_URL")
                if new_webhook:
                    await self.config_manager.update_value_in_file('WEBHOOK_URL', str(new_webhook))
                    await logger.info(f"[🔄] WEBHOOK_URL оновлено: {new_webhook}")
            if data.get("event") == "SCAN_INTERVAL_UPDATED":
                new_scan_interval = data.get("scan_interval")
                if new_scan_interval:
                    await self.config_manager.update_value_in_file('scan_interval', new_scan_interval)
                    await logger.info(f"[🔄] scan_interval оновлено: {new_scan_interval}")
            if data.get("event") == "LOG_DETAILS_UPDATED":
                new_log_details = str(data.get("Log_Details"))
                if new_log_details:
                    await self.config_manager.update_value_in_file('Log_Details', int(new_log_details))
                    await logger.info(f"[🔄] Log_Details оновлено: {new_log_details}")
            if data.get("event") == "PROXY_UPDATED":
                new_proxy_list = data.get("proxy")
                if new_proxy_list or new_proxy_list == []:
                    await self.config_manager.set_proxy_list(new_proxy_list)
                    await logger.info(f"[🔄] proxy_list оновлено: {new_proxy_list}")
        except json.JSONDecodeError:
            await logger.error("[⚠] Неможливо розпарсити повідомлення:", message)

async def websocket_listener(parser_client):
    while True:  # Використовуємо цикл замість рекурсії
        try:
            await parser_client.connect()
            await logger.info(f"✅ Підключено до WebSocket сервера")

            # Надсилаємо підписку (залежно від API WebSocket)
            await parser_client.subscribe()

            async for message in parser_client.listen():  # Очікуємо повідомлення
                await logger.info(f"📩 Отримано повідомлення: {message}")

        except Exception as e:
            await logger.error(f"❌ Помилка WebSocket: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    ws_url = "ws://localhost:8000/ws"  # Замініть на реальну URL WebSocket сервера
    parser = ParserClient(ws_url)
    asyncio.run(parser.connect())
