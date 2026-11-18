# BrixGate

> **Unofficial, independent project.** BrixGate is not affiliated with, endorsed by, or maintained by the
> NeuroBrix project. Each model you run has its own license (for example, OpenAudio S1 Mini is
> non-commercial). Check the license of every model before using it, especially for commercial use.

[Leer en español](README.es.md)

BrixGate is an HTTP server that speaks the OpenAI API and, under the hood, runs the
[NeuroBrix](https://github.com/NeuroBrix/neurobrix) command-line engine on your own machine. The goal:
any app or SDK that already talks to OpenAI works with local models by changing only `base_url`, and your
data stays local.

```
OpenAI client ──HTTP──▶ BrixGate ──subprocess──▶ neurobrix CLI ──▶ GPU
```

## Status

**Pre-alpha. Nothing works yet.** The repository currently contains only the project skeleton. The behavior
of the NeuroBrix CLI (output format, exit codes, streaming) is still being verified; see
[`docs/cli-contract.md`](docs/cli-contract.md).

## Planned endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/models` | List available models |
| `POST /v1/chat/completions` | Text and vision chat |
| `POST /v1/audio/transcriptions` | Speech to text |
| `POST /v1/audio/speech` | Text to speech |
| `POST /v1/images/generations` | Image generation |
| `POST /v1/videos` | Video generation (BrixGate-specific) |
| `POST /v1/upscale` | Upscaling (BrixGate-specific) |
| `GET /health` | Server status |

## Development

Requires Python 3.10–3.12.

```
python -m venv .venv
.venv\Scripts\activate        # Windows (cmd)
source .venv/bin/activate     # macOS / Linux
python -m pip install -e ".[dev]"
ruff check . && ruff format --check . && mypy && pytest
```

Tests that need a real NeuroBrix install and a GPU are marked `gpu` and are skipped by default.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Models have their own licenses.
