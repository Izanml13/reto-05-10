"""Inferencia contra la VM de Azure de Inetum (API REST compatible con OpenAI).

La mayoría de servidores de inferencia (vLLM, Ollama, TGI, LM Studio, LiteLLM)
exponen la API de OpenAI:
    GET  /v1/models            -> modelos desplegados
    POST /v1/chat/completions  -> generación

Uso:
    python inferencia_azure.py --listar
    python inferencia_azure.py --prompt "Explica qué es la cuantización Q4"
    python inferencia_azure.py --modelos gemma-4-E4B-it llama-3.1-8b --prompt "..."
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

PROMPT_POR_DEFECTO = (
    "Explica en español, en un máximo de 120 palabras, qué es la cuantización "
    "de un modelo de lenguaje y por qué reduce la VRAM necesaria. "
    "Termina con un ejemplo numérico."
)


def cargar_env(ruta=".env"):
    """Carga variables de un archivo .env sin depender de python-dotenv."""
    if not Path(ruta).exists():
        return
    for linea in Path(ruta).read_text().splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"'))


class ClienteVM:
    def __init__(self, base_url, api_key=None, timeout=120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.sesion = requests.Session()
        self.sesion.headers["Content-Type"] = "application/json"
        if api_key:
            self.sesion.headers["Authorization"] = f"Bearer {api_key}"

    def listar_modelos(self):
        r = self.sesion.get(f"{self.base_url}/v1/models", timeout=self.timeout)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])]

    def chat(self, modelo, prompt, max_tokens=400, temperature=0.7):
        cuerpo = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un asistente técnico preciso y conciso."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        inicio = time.perf_counter()
        r = self.sesion.post(f"{self.base_url}/v1/chat/completions", json=cuerpo, timeout=self.timeout)
        latencia = time.perf_counter() - inicio
        r.raise_for_status()
        datos = r.json()
        uso = datos.get("usage", {})
        tokens_salida = uso.get("completion_tokens", 0)
        return {
            "modelo": modelo,
            "respuesta": datos["choices"][0]["message"]["content"].strip(),
            "latencia_s": round(latencia, 2),
            "tokens_entrada": uso.get("prompt_tokens", 0),
            "tokens_salida": tokens_salida,
            "tokens_por_s": round(tokens_salida / latencia, 1) if latencia and tokens_salida else None,
        }


def analizar(resultado, prompt):
    """Métricas automáticas sencillas para comparar respuestas."""
    texto = resultado["respuesta"]
    palabras = len(texto.split())
    return {
        "palabras": palabras,
        "respeta_limite_120": palabras <= 120,
        "incluye_numeros": any(c.isdigit() for c in texto),
        "menciona_vram": "vram" in texto.lower() or "memoria" in texto.lower(),
    }


def guardar_informe(resultados, prompt, carpeta="resultados"):
    Path(carpeta).mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    Path(carpeta, f"resultados_{marca}.json").write_text(
        json.dumps({"prompt": prompt, "resultados": resultados}, ensure_ascii=False, indent=2)
    )
    md = [f"# Comparativa de respuestas · {marca}", "", f"**Prompt:** {prompt}", "",
          "| Modelo | Latencia (s) | Tokens salida | Tokens/s | Palabras | ≤120 palabras | Ejemplo numérico | Menciona VRAM |",
          "|---|---|---|---|---|:-:|:-:|:-:|"]
    ok = lambda b: "✅" if b else "❌"
    for r in resultados:
        if "error" in r:
            md.append(f"| {r['modelo']} | error: {r['error']} | | | | | | |")
            continue
        a = r["analisis"]
        md.append(f"| {r['modelo']} | {r['latencia_s']} | {r['tokens_salida']} | {r['tokens_por_s']} | "
                  f"{a['palabras']} | {ok(a['respeta_limite_120'])} | {ok(a['incluye_numeros'])} | {ok(a['menciona_vram'])} |")
    for r in resultados:
        if "respuesta" in r:
            md += ["", f"## {r['modelo']}", "", r["respuesta"]]
    md += ["", "## Valoración manual", "", "_Completar: precisión técnica, claridad, idioma y seguimiento de instrucciones._"]
    ruta = Path(carpeta, f"resultados_{marca}.md")
    ruta.write_text("\n".join(md))
    return ruta


def main():
    cargar_env()
    p = argparse.ArgumentParser(description="Inferencia contra la VM de Azure")
    p.add_argument("--url", default=os.getenv("AZURE_VM_URL"), help="URL base, p. ej. http://<ip>:8000")
    p.add_argument("--api-key", default=os.getenv("AZURE_VM_API_KEY"))
    p.add_argument("--listar", action="store_true", help="Solo listar modelos desplegados")
    p.add_argument("--modelos", nargs="*", help="Modelos a comparar (por defecto, los 2 primeros desplegados)")
    p.add_argument("--prompt", default=PROMPT_POR_DEFECTO)
    p.add_argument("--max-tokens", type=int, default=400)
    args = p.parse_args()

    if not args.url:
        sys.exit("Falta la URL de la VM: usa --url o define AZURE_VM_URL en .env")

    cliente = ClienteVM(args.url, args.api_key)

    try:
        desplegados = cliente.listar_modelos()
    except requests.RequestException as e:
        sys.exit(f"No se pudo conectar con {args.url}: {e}")

    print(f"Modelos desplegados en la VM ({len(desplegados)}):")
    for m in desplegados:
        print(f"  • {m}")
    if args.listar:
        return

    modelos = args.modelos or desplegados[:2]
    if len(modelos) < 2:
        print("Aviso: el reto pide comparar al menos 2 modelos.")

    resultados = []
    for modelo in modelos:
        print(f"\n→ {modelo} ...")
        try:
            r = cliente.chat(modelo, args.prompt, args.max_tokens)
            r["analisis"] = analizar(r, args.prompt)
            print(f"  {r['latencia_s']} s · {r['tokens_salida']} tokens\n  {r['respuesta'][:300]}")
        except requests.RequestException as e:
            r = {"modelo": modelo, "error": str(e)}
            print(f"  Error: {e}")
        resultados.append(r)

    print(f"\nInforme guardado en {guardar_informe(resultados, args.prompt)}")


if __name__ == "__main__":
    main()
