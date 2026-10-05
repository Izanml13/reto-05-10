# Comparativa de modelos open-source

> Reto del día 05/10/2026 · Team MIRA · Inetum
> Fuentes: fichas oficiales de cada modelo en Hugging Face. Las cifras de VRAM son **estimaciones propias** (ver [metodología](#metodología-de-cálculo-de-vram)).

---

## 1. Familia Gemma 4 (Google DeepMind)

Todos los modelos Gemma 4 se publican con licencia **Apache 2.0**, tienen variantes `-it` (afinadas para instrucciones), modo de razonamiento (*thinking*) configurable, llamadas a funciones y vocabulario de 262K tokens.

### 1.1 Arquitectura y modalidades

| Modelo | Tipo | Parámetros efectivos / activos | Parámetros totales | Capas | Contexto | Texto | Imagen | Vídeo* | Audio |
|---|---|---|---|---|---|:-:|:-:|:-:|:-:|
| [gemma-4-E2B-it](https://huggingface.co/google/gemma-4-E2B-it) | Denso + PLE | **2,3 B** efectivos | 5,1 B | 35 | 128K | ✅ | ✅ | ✅ | ✅ |
| [gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | Denso + PLE | **4,5 B** efectivos | 8 B | 42 | 128K | ✅ | ✅ | ✅ | ✅ |
| [gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) | Denso «Unified» (sin encoders) | 11,95 B | 11,95 B | 48 | 256K | ✅ | ✅ | ✅ | ✅ |
| [gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it) | MoE (8 de 128 expertos + 1 compartido) | **3,8 B** activos | 25,2 B | 30 | 256K | ✅ | ✅ | ✅ | ❌ |
| [gemma-4-31B-it](https://huggingface.co/google/gemma-4-31B-it) | Denso | 30,7 B | 30,7 B | 60 | 256K | ✅ | ✅ | ✅ | ❌ |

\* El vídeo se procesa como secuencia de fotogramas (máx. 60 s a 1 fps). El audio admite clips de hasta 30 s.

- **E = *effective*:** los modelos E2B y E4B usan *Per-Layer Embeddings* (PLE). Son tablas grandes que solo se consultan, por lo que el cómputo equivale al de los parámetros efectivos.
- **A = *active*:** el 26B-A4B es un *Mixture of Experts*. Activa solo 3,8 B por token (va casi tan rápido como un 4B), pero **hay que cargar los 25,2 B en memoria**.

### 1.2 VRAM estimada

| Modelo | BF16 (original) | Q8_0 | Q4_K_M | Hardware orientativo (Q4) |
|---|---|---|---|---|
| E2B | ~11 GB | ~6 GB | **~3,5 GB** | Móvil de gama alta, portátil sin GPU |
| E4B | ~17 GB | ~9,5 GB | **~6 GB** | Portátil o GPU de 8 GB |
| 12B | ~25 GB | ~14 GB | **~8,5 GB** | RTX 3060 12 GB / RTX 4070 |
| 26B-A4B | ~52 GB | ~28 GB | **~17 GB** | RTX 3090 / 4090 (24 GB) |
| 31B | ~63 GB | ~34 GB | **~20 GB** | RTX 3090 / 4090 (24 GB) |

### 1.3 Benchmarks (ficha oficial, modelos `-it`)

| Benchmark | E2B | E4B | 12B | 26B-A4B | 31B |
|---|---|---|---|---|---|
| MMLU Pro | 60,0 % | 69,4 % | 77,2 % | 82,6 % | **85,2 %** |
| GPQA Diamond | 43,4 % | 58,6 % | 78,8 % | 82,3 % | **84,3 %** |
| AIME 2026 (sin herramientas) | 37,5 % | 42,5 % | 77,5 % | 88,3 % | **89,2 %** |
| LiveCodeBench v6 | 44,0 % | 52,0 % | 72,0 % | 77,1 % | **80,0 %** |
| MMMLU (multilingüe) | 67,4 % | 76,6 % | 83,4 % | 86,3 % | **88,4 %** |
| MMMU Pro (visión) | 44,2 % | 52,6 % | 69,1 % | 73,8 % | **76,9 %** |
| CoVoST (traducción de voz) | 33,47 | 35,54 | **38,5** | — | — |

**Lectura rápida**

- **31B:** el mejor en todo, pero necesita una GPU de 24 GB incluso cuantizado.
- **26B-A4B:** casi la calidad del 31B con la velocidad de un 4B. Es la mejor relación calidad/latencia si hay memoria.
- **12B:** el punto dulce en GPUs de consumo y el más grande con audio.
- **E4B / E2B:** pensados para dispositivos. E4B supera a Gemma 3 27B en MMLU Pro (69,4 % frente a 67,6 %).

---

## 2. Comparativa general de modelos open-source

| Modelo | Desarrollador | Parámetros | VRAM BF16 | VRAM Q4_K_M | Contexto | Licencia | Idiomas | Modalidades | Casos de uso |
|---|---|---|---|---|---|---|---|---|---|
| **Gemma 4 E4B-it** | Google DeepMind | 4,5 B efectivos (8 B totales) | ~17 GB | ~6 GB | 128K | Apache 2.0 | 35+ (preentrenado en 140+) | Texto, imagen, vídeo, audio | Asistentes on-device, OCR, transcripción, agentes ligeros |
| **Gemma 4 31B-it** | Google DeepMind | 30,7 B | ~63 GB | ~20 GB | 256K | Apache 2.0 | 35+ (preentrenado en 140+) | Texto, imagen, vídeo | Razonamiento complejo, código, agentes, análisis de documentos |
| **Llama 3.1 8B Instruct** | Meta | 8 B | ~17 GB | ~6 GB | 128K | Llama 3.1 Community License | 8 (en, de, fr, it, pt, hi, es, th) | Texto | Chatbots, RAG, generación de texto, base para fine-tuning |
| **Llama 3.1 70B Instruct** | Meta | 70 B | ~141 GB | ~43 GB | 128K | Llama 3.1 Community License | 8 | Texto | Asistentes empresariales, razonamiento, generación de datos sintéticos |
| **Phi-3-mini-4k-instruct** | Microsoft | 3,8 B | ~8 GB | ~3 GB | 4K (variante de 128K) | MIT | Principalmente inglés | Texto | Edge y móvil, entornos con poca memoria, razonamiento matemático y lógico básico |
| **Phi-3-medium-128k-instruct** | Microsoft | 14 B | ~29 GB | ~9,5 GB | 128K | MIT | Principalmente inglés | Texto | Resumen de documentos largos, razonamiento con recursos limitados |
| **Mistral 7B Instruct v0.3** | Mistral AI | 7,3 B | ~15 GB | ~5 GB | 32K | Apache 2.0 | Principalmente inglés (bueno en fr, es, de, it) | Texto | Chat general, llamadas a funciones, despliegues ligeros |
| **Qwen2.5 7B Instruct** | Alibaba | 7,6 B | ~16 GB | ~5,5 GB | 128K | Apache 2.0 | 29+ | Texto | Multilingüe, código, matemáticas, salida JSON estructurada |

### Observaciones sobre las licencias

| Licencia | Uso comercial | Notas |
|---|---|---|
| **Apache 2.0** (Gemma 4, Mistral, Qwen2.5) | ✅ Sin restricciones | Hay que mantener el aviso de copyright y la licencia. Incluye concesión de patentes. |
| **MIT** (Phi-3) | ✅ Sin restricciones | La más permisiva: basta con conservar el aviso. |
| **Llama 3.1 Community License** | ⚠️ Con condiciones | Necesita licencia aparte si se superan 700 M de usuarios activos mensuales. Obliga a mostrar «Built with Llama» y a cumplir la política de uso aceptable de Meta. |

### ¿Cuál elegir?

| Necesidad | Recomendación |
|---|---|
| Procesar audio o imagen en local con poca memoria | **Gemma 4 E4B** |
| Máxima calidad en una sola GPU de 24 GB | **Gemma 4 31B** (Q4) o **26B-A4B** si importa la latencia |
| Multilingüe con buen español y licencia libre | **Gemma 4** o **Qwen2.5** |
| Dispositivo muy limitado, solo texto en inglés | **Phi-3-mini** |
| Ecosistema y fine-tunes de la comunidad | **Llama 3.1** |

---

## Metodología de cálculo de VRAM

```
VRAM ≈ parámetros_totales × bits_por_peso ÷ 8  +  ~1 GB (KV cache de ~8K tokens + overhead)
```

- Bits por peso: BF16 = 16 · Q8_0 ≈ 8,5 · Q4_K_M ≈ 4,9.
- En Gemma se usan los parámetros **totales**, porque PLE y los expertos MoE ocupan memoria aunque no calculen. Algunos motores pueden sacar las tablas PLE de la GPU y reducir la cifra de E2B y E4B.
- En los modelos Gemma con visión o audio se suma ~0,5 GB por los encoders.
- Para contextos largos (64K–256K), la KV cache puede añadir varios GB más.
