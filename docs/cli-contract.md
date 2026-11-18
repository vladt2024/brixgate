# Contrato de la CLI de NeuroBrix (PLANTILLA: pendiente de verificar)

> **Estado: sin verificar.** Las columnas "Según el README" salen del README de NeuroBrix. Las columnas "Observado" están vacías: se rellenan con la evidencia que genera `phase0_probe.py` en una máquina con NeuroBrix instalado. Hasta entonces, nada de lo marcado como "?" debe darse por cierto.

## Cómo rellenarlo

1. Ejecuta `python phase0_probe.py` (ver opciones dentro del script).
2. Abre `phase0_results/cli-contract-evidence.md`.
3. Copia aquí lo observado, sustituyendo cada "?".

## Información de entorno

| Dato | Valor |
|---|---|
| Versión de NeuroBrix | ? |
| Sistema operativo | ? |
| GPU(s) | ? |
| Python / PyTorch | ? |
| Modelos instalados para la prueba | ? |

## Comandos

### `neurobrix run`

| Aspecto | Según el README | Observado |
|---|---|---|
| Argumentos LLM | `--model`, `--prompt`, `--temperature`, `--max-tokens`, `--repetition-penalty`, `--output` | ? |
| Dónde sale el texto del LLM | stdout por defecto ("`--output` default stdout") | ? |
| Dónde van los logs/progreso | no documentado | ? |
| Código de salida en éxito | no documentado | ? |
| Código de salida en error (modelo inexistente, falta prompt) | no documentado | ? |
| ¿Aplica plantilla de chat? | no documentado | ? |
| ¿Cómo se pasa un historial de mensajes? | no documentado | ? |
| ¿Salida incremental (streaming)? | no documentado | ? |
| Semilla / determinismo | `--seed` reproduce la salida en el mismo hardware | ? |

### `neurobrix serve` / `stop`

| Aspecto | Según el README | Observado |
|---|---|---|
| Qué hace | carga el modelo en VRAM y lo mantiene | ? |
| `run` posterior sin `--model` | funciona con el modelo cargado | ? |
| Cómo saber que está listo | no documentado | ? |
| Tiempo de arranque | no documentado | ? |
| Protocolo del demonio (socket, puerto, archivo) | no documentado | ? |
| Peticiones concurrentes | no documentado | ? |
| Pedir otro modelo con el demonio activo | no documentado | ? |
| Comportamiento de `stop` | libera VRAM | ? |

### `neurobrix list`

| Aspecto | Observado |
|---|---|
| Formato de salida (¿tabla, JSON, una línea por modelo?) | ? |
| ¿Se puede obtener JSON? | ? |
| Cómo distinguir la familia de cada modelo | ? |

### Otras familias

| Familia | Comando según el README | Salida observada | Formato del archivo de salida |
|---|---|---|---|
| STT | `run --model whisper-large --audio file.wav` | ? | stdout |
| TTS | `run --model Kokoro-82M --prompt "..." --output speech.wav` | ? | WAV |
| Imagen | `run --prompt … --steps --cfg --seed --height --width --output x.png` | ? | PNG |
| VLM | `run --input-image img.jpg --prompt "..."` | ? | stdout |
| Vídeo | `run … --num-frames --output video.mp4` | ? | MP4 |
| Upscale | `upscale --model … --input … --output …` | ? | PNG |

### Librería de Python

| Pregunta | Observado |
|---|---|
| ¿`import neurobrix` funciona? | ? |
| ¿Qué expone? | ? |
| ¿Hay una función para generar sin subprocess? | ? |

## Decisiones derivadas (rellenar al terminar)

| Decisión | Depende de | Resultado |
|---|---|---|
| Streaming real o simulado | salida incremental | ? |
| Cómo construir el prompt de chat | plantilla de chat | ? |
| Cómo detectar `serve` listo | protocolo del demonio | ? |
| subprocess o librería | API de Python | ? |
| Política de cambio de modelo | comportamiento con demonio activo | ? |
