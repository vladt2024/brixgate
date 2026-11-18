# BrixGate

> **Proyecto independiente y no oficial.** BrixGate no está afiliado, respaldado ni mantenido por el
> proyecto NeuroBrix. Cada modelo que ejecutes tiene su propia licencia (por ejemplo, OpenAudio S1 Mini es
> de uso no comercial). Comprueba la licencia de cada modelo antes de usarlo, sobre todo si es para uso
> comercial.

[Read in English](README.md)

BrixGate es un servidor HTTP que habla el protocolo de la API de OpenAI y, por debajo, ejecuta el motor de
línea de comandos [NeuroBrix](https://github.com/NeuroBrix/neurobrix) en tu propia máquina. El objetivo:
que cualquier app o SDK que ya hable con OpenAI funcione con modelos locales cambiando solo `base_url`,
manteniendo tus datos en local.

```
Cliente OpenAI ──HTTP──▶ BrixGate ──subprocess──▶ CLI de neurobrix ──▶ GPU
```

## Estado

**Pre-alfa. Todavía no funciona nada.** El repositorio contiene solo el esqueleto del proyecto. El
comportamiento de la CLI de NeuroBrix (formato de salida, códigos de error, streaming) aún se está
verificando; ver [`docs/cli-contract.md`](docs/cli-contract.md).

## Endpoints previstos

| Endpoint | Función |
|---|---|
| `GET /v1/models` | Listar modelos disponibles |
| `POST /v1/chat/completions` | Chat de texto y visión |
| `POST /v1/audio/transcriptions` | Voz a texto |
| `POST /v1/audio/speech` | Texto a voz |
| `POST /v1/images/generations` | Generación de imágenes |
| `POST /v1/videos` | Generación de vídeo (propio de BrixGate) |
| `POST /v1/upscale` | Escalado de imágenes (propio de BrixGate) |
| `GET /health` | Estado del servidor |

## Desarrollo

Requiere Python 3.10–3.12.

```
python -m venv .venv
.venv\Scripts\activate        # Windows (cmd)
source .venv/bin/activate     # macOS / Linux
python -m pip install -e ".[dev]"
ruff check . && ruff format --check . && mypy && pytest
```

Los tests que necesitan una instalación real de NeuroBrix y una GPU llevan la marca `gpu` y se omiten por
defecto.

## Licencia

Apache-2.0. Ver [LICENSE](LICENSE) y [NOTICE](NOTICE). Los modelos tienen sus propias licencias.
