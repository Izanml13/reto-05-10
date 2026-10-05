"""Servidor falso compatible con OpenAI para probar inferencia_azure.py sin la VM.

    python tests/servidor_mock.py  # escucha en http://localhost:8000
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

MODELOS = ["gemma-4-E4B-it", "llama-3.1-8b-instruct"]


class Handler(BaseHTTPRequestHandler):
    def _json(self, datos):
        cuerpo = json.dumps(datos).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/v1/models":
            self._json({"data": [{"id": m} for m in MODELOS]})

    def do_POST(self):
        pet = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        texto = f"[{pet['model']}] La cuantización reduce los bits por peso: 8B × 4 bits ÷ 8 = 4 GB de VRAM."
        self._json({"choices": [{"message": {"content": texto}}],
                    "usage": {"prompt_tokens": 40, "completion_tokens": 25}})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("localhost", 8000), Handler).serve_forever()
