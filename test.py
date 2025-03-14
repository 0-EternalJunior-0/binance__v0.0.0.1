from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Порт для запуску сервера
PORT = 5555

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Отримуємо довжину тіла запиту
        post_data = self.rfile.read(content_length)  # Зчитуємо тіло запиту

        try:
            # Парсимо JSON-дані
            data = json.loads(post_data)
            print("Отримані дані:", data)

            # Відповідь клієнту
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "success", "received_data": data}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Сервер запущено на порту {PORT}")
    httpd.serve_forever()