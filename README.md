# Reto 05/10 · Modelos open-source y Hugging Face

Team MIRA · Inetum · 5 de octubre de 2026

## Entregables

| Entregable | Archivo | Estado |
|---|---|---|
| Tabla comparativa de modelos (Markdown) | [`comparativa_modelos.md`](comparativa_modelos.md) | ✅ |
| Script Python de inferencia contra la VM de Azure | [`inferencia_azure.py`](inferencia_azure.py) | ✅ Probado contra un servidor de prueba local · ⏳ pendiente de las credenciales de la VM |

## Tareas del reto

- [x] Explorar el Hub de modelos de Hugging Face
- [x] Comparar la familia Gemma 4 (E2B, E4B, 12B, 26B-A4B, 31B): parámetros efectivos, VRAM, modalidades y benchmarks
- [x] Tabla comparativa de 8 modelos open-source (Gemma 4, Llama 3.1, Phi-3, Mistral, Qwen2.5)
- [ ] Conectar a la VM de Azure y listar los modelos desplegados. **Bloqueado:** Inetum aún no ha proporcionado la URL ni la API key
- [ ] Ejecutar el mismo prompt en 2 modelos de la VM y analizar la calidad. El script ya está preparado

## Exploración del Hub de Hugging Face

1. Crear una cuenta en <https://huggingface.co/join>.
2. En **Models** (<https://huggingface.co/models>), filtrar por:
   - **Tasks:** *Text Generation*, *Image-Text-to-Text*, *Any-to-Any*
   - **Libraries:** *Transformers*, *GGUF*
   - **Licenses:** *apache-2.0*, *mit*
3. En la ficha (*model card*) de cada modelo, revisar:
   - **Arquitectura y parámetros:** sección «Model Overview».
   - **Benchmarks:** sección «Evaluation».
   - **Licencia:** etiqueta en la cabecera. Algunos modelos (Llama) piden aceptar condiciones antes de descargar.
   - **Model tree:** versiones cuantizadas (GGUF, GPTQ, AWQ), fine-tunes y adaptadores LoRA.
4. La colección oficial de Gemma 4 está en <https://huggingface.co/collections/google> y el modelo de referencia en <https://huggingface.co/google/gemma-4-E4B-it>.

## Script de inferencia

El script habla con cualquier servidor que exponga la **API compatible con OpenAI** (`/v1/models` y `/v1/chat/completions`), que es la que ofrecen vLLM, Ollama, TGI, LM Studio y LiteLLM.

```bash
pip install -r requirements.txt
cp .env.example .env           # rellenar AZURE_VM_URL y AZURE_VM_API_KEY

python inferencia_azure.py --listar                          # modelos desplegados
python inferencia_azure.py                                   # prompt por defecto en los 2 primeros modelos
python inferencia_azure.py --modelos modelo-a modelo-b --prompt "Tu prompt"
```

Para cada modelo, el script:

- mide la latencia, los tokens generados y los tokens por segundo;
- aplica comprobaciones automáticas: límite de palabras, ejemplo numérico y mención de VRAM;
- guarda los resultados en `resultados/` en JSON y en Markdown, con un apartado para la valoración manual de la calidad.

### Probarlo sin la VM

```bash
python tests/servidor_mock.py &                      # API falsa en localhost:8000
python inferencia_azure.py --url http://localhost:8000
```

> Si la VM de Inetum usa otra API (por ejemplo, Azure ML con `/score` o rutas propias), solo hay que adaptar `listar_modelos()` y `chat()` en la clase `ClienteVM`.
