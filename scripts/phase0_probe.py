#!/usr/bin/env python3
"""Phase 0 probe for BrixGate: records how the real NeuroBrix CLI behaves.

Run it on the machine that has NeuroBrix installed (ideally with a GPU). It only runs
NeuroBrix commands and writes everything it observes into a report folder; it does not
send anything anywhere. Read the report before sharing it: it contains your hardware
description and local paths.

Usage examples:
    python phase0_probe.py
    python phase0_probe.py --llm TinyLlama-1.1B-Chat --tts Kokoro-82M --stt whisper-large \
        --audio-file sample.wav --image-model Sana_1600M_1024px_MultiLing
"""
from __future__ import annotations

import argparse
import os
import pathlib
import platform
import shlex
import subprocess
import sys
import threading
import time
from typing import Any

REPORT_NAME = "cli-contract-evidence.md"


def run_cmd(args: list[str], timeout: float) -> dict[str, Any]:
    """Run a command, capture stdout/stderr and the timestamps of every stdout line.

    Args:
        args: Full command line as a list.
        timeout: Seconds before the process is killed.

    Returns:
        Dict with exit code, duration, stdout, stderr and stdout line timestamps.
    """
    start = time.time()
    stamps: list[float] = []
    out_lines: list[str] = []
    err_lines: list[str] = []
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    except OSError as exc:
        return {"args": args, "rc": None, "error": f"{type(exc).__name__}: {exc}", "seconds": 0.0,
                "stdout": "", "stderr": "", "stamps": []}

    def pump(stream, sink: list[str], record: bool) -> None:
        """Read a stream line by line into a list, optionally recording arrival times."""
        for line in stream:
            sink.append(line)
            if record:
                stamps.append(time.time() - start)

    threads = [threading.Thread(target=pump, args=(proc.stdout, out_lines, True), daemon=True),
               threading.Thread(target=pump, args=(proc.stderr, err_lines, False), daemon=True)]
    for t in threads:
        t.start()
    timed_out = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        proc.wait()
    for t in threads:
        t.join(timeout=5)
    return {"args": args, "rc": proc.returncode, "timed_out": timed_out, "seconds": time.time() - start,
            "stdout": "".join(out_lines), "stderr": "".join(err_lines), "stamps": stamps}


def clip(text: str, limit: int = 2500) -> str:
    """Trim long output keeping head and tail."""
    if len(text) <= limit:
        return text
    return text[: limit // 2] + "\n[... recortado ...]\n" + text[-limit // 2:]


class Report:
    """Accumulates markdown sections for the evidence file."""

    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, title: str, res: dict[str, Any], note: str = "") -> None:
        """Append one probe result as a markdown section."""
        cmd = " ".join(shlex.quote(a) for a in res["args"])
        stamps = res.get("stamps", [])
        stream_hint = ""
        if len(stamps) >= 3:
            stream_hint = f"- Líneas de stdout: {len(stamps)}; primera a {stamps[0]:.1f}s, última a {stamps[-1]:.1f}s (si están muy separadas, la salida es incremental)\n"
        self.parts.append(
            f"\n### {title}\n\n- Comando: `{cmd}`\n- Código de salida: `{res.get('rc')}`"
            f"{' (TIMEOUT)' if res.get('timed_out') else ''}\n- Duración: {res.get('seconds', 0):.1f}s\n"
            f"{stream_hint}{('- Nota: ' + note + chr(10)) if note else ''}"
            f"{('- Error al lanzar: ' + res['error'] + chr(10)) if res.get('error') else ''}"
            f"\n**stdout**\n```\n{clip(res.get('stdout', '')) or '(vacío)'}\n```\n"
            f"**stderr**\n```\n{clip(res.get('stderr', '')) or '(vacío)'}\n```\n"
        )

    def write(self, path: pathlib.Path) -> None:
        """Write the report to disk."""
        path.write_text("".join(self.parts), encoding="utf-8")


def main() -> int:
    """Entry point: run all probes and write the report."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nb", default="neurobrix", help="Command to invoke NeuroBrix (default: neurobrix)")
    ap.add_argument("--out", default="phase0_results", help="Output folder")
    ap.add_argument("--timeout", type=float, default=900, help="Seconds per command (default 900)")
    ap.add_argument("--llm", help="Installed LLM model name")
    ap.add_argument("--vlm", help="Installed vision-language model name")
    ap.add_argument("--stt", help="Installed speech-to-text model name")
    ap.add_argument("--tts", help="Installed text-to-speech model name")
    ap.add_argument("--image-model", help="Installed image generation model name")
    ap.add_argument("--audio-file", help="Short WAV/MP3 file for STT")
    ap.add_argument("--image-file", help="Image file for VLM")
    ap.add_argument("--skip-serve", action="store_true", help="Skip the serve/daemon tests")
    a = ap.parse_args()

    nb = shlex.split(a.nb)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = Report()
    T = a.timeout

    def probe(title: str, extra: list[str], note: str = "", timeout: float | None = None) -> dict[str, Any]:
        """Run one NeuroBrix subcommand and add it to the report."""
        res = run_cmd(nb + extra, timeout or T)
        rep.add(title, res, note)
        print(f"[{res.get('rc')}] {title} ({res.get('seconds', 0):.1f}s)")
        return res

    rep.parts.append(
        "# Evidencia de la Fase 0: comportamiento real de la CLI de NeuroBrix\n\n"
        f"- Fecha: {time.strftime('%Y-%m-%d %H:%M')}\n- Sistema: {platform.platform()}\n- Python: {sys.version.split()[0]}\n"
    )

    # 1. Version, help and hardware
    probe("Versión", ["--version"])
    for sub in ["", "run", "serve", "chat", "stop", "upscale", "list", "info", "hub", "import"]:
        probe(f"Ayuda: {sub or '(general)'}", ([sub] if sub else []) + ["--help"])
    probe("doctor", ["doctor"])
    probe("info --system", ["info", "--system"])
    probe("info --hardware", ["info", "--hardware"])
    probe("info --models", ["info", "--models"])
    probe("list", ["list"])
    probe("list --store", ["list", "--store"])

    # 2. Is there a Python API?
    res = run_cmd([sys.executable, "-I", "-c",
                   "import neurobrix,sys;print(neurobrix.__file__);print(getattr(neurobrix,'__version__',None));"
                   "print([n for n in dir(neurobrix) if not n.startswith('_')])"], 60)
    rep.add("¿Se puede importar neurobrix como librería?", res,
            "Si funciona, mira qué expone; podría servir para llamar al motor sin subprocess.")
    print(f"[{res.get('rc')}] import neurobrix")

    # 3. Error contract
    probe("Error: modelo inexistente", ["run", "--model", "__no_existe__", "--prompt", "hola"])
    probe("Error: falta --prompt", ["run", "--model", a.llm or "__no_existe__"])

    # 4. One-shot runs per family
    work = out / "files"
    work.mkdir(exist_ok=True)
    if a.llm:
        probe("LLM: salida por defecto (¿stdout?)", ["run", "--model", a.llm, "--prompt", "What is the capital of France?",
              "--temperature", "0.0", "--max-tokens", "64"],
              "Mira si responde como asistente (plantilla de chat aplicada) o si solo continúa el texto.")
        probe("LLM: con --output", ["run", "--model", a.llm, "--prompt", "What is the capital of France?",
              "--temperature", "0.0", "--max-tokens", "64", "--output", str(work / "llm.txt")],
              "Comprueba si el archivo existe y qué sale por stdout.")
        probe("LLM: prompt con comillas y saltos de línea", ["run", "--model", a.llm, "--prompt",
              "Line one\nLine two with \"quotes\" and 'apostrophes'. Say OK.", "--max-tokens", "32"])
        probe("LLM: prompt con formato de conversación", ["run", "--model", a.llm, "--prompt",
              "System: You are terse.\nUser: Say hi.\nAssistant:", "--max-tokens", "32"])
    if a.vlm and a.image_file:
        probe("VLM: describir imagen", ["run", "--model", a.vlm, "--input-image", a.image_file,
              "--prompt", "Describe this image in one sentence.", "--max-tokens", "64"])
    if a.stt and a.audio_file:
        probe("STT: transcribir", ["run", "--model", a.stt, "--audio", a.audio_file])
    if a.tts:
        probe("TTS: sintetizar", ["run", "--model", a.tts, "--prompt", "Hello from BrixGate.",
              "--output", str(work / "tts.wav")])
    if a.image_model:
        probe("Imagen: generar", ["run", "--model", a.image_model, "--prompt", "a red fox", "--steps", "10",
              "--seed", "1", "--output", str(work / "img.png")])

    # 5. Serve / daemon
    if not a.skip_serve and a.llm:
        srv = subprocess.Popen(nb + ["serve", "--model", a.llm], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, errors="replace")
        t0 = time.time()
        ready = None
        while time.time() - t0 < T:
            time.sleep(5)
            r = run_cmd(nb + ["run", "--prompt", "Say OK.", "--max-tokens", "8"], 60)
            if r["rc"] == 0 and r["stdout"].strip():
                ready = time.time() - t0
                rep.add("serve: primer run exitoso tras arrancar", r, f"Tiempo hasta primera respuesta: {ready:.0f}s")
                break
        print(f"serve ready: {ready}")
        if ready is not None:
            probe("serve: run en caliente (sin --model)", ["run", "--prompt", "What is 2+2?", "--max-tokens", "16"])
            results: list[dict[str, Any]] = []
            threads = [threading.Thread(target=lambda: results.append(run_cmd(
                nb + ["run", "--prompt", "Count to five.", "--max-tokens", "32"], 300))) for _ in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            for i, r in enumerate(results, 1):
                rep.add(f"serve: petición concurrente {i}/2", r, "¿Se serializan, fallan o responden a la vez?")
            if a.image_model:
                probe("serve: pedir OTRO modelo con el demonio activo", ["run", "--model", a.image_model,
                      "--prompt", "a red fox", "--steps", "5", "--output", str(work / "img2.png")])
        probe("stop", ["stop"])
        try:
            srv.wait(timeout=30)
        except subprocess.TimeoutExpired:
            srv.kill()
        rep.parts.append(f"\n### serve (proceso en primer plano)\n- Código de salida: `{srv.returncode}`\n")
        home = pathlib.Path(os.path.expanduser("~/.neurobrix"))
        if home.exists():
            names = sorted(str(p.relative_to(home)) for p in home.rglob("*") if len(p.relative_to(home).parts) <= 2)
            rep.parts.append("\n### Contenido de ~/.neurobrix (solo nombres, 2 niveles)\n```\n" + "\n".join(names[:200]) + "\n```\n")

    rep.parts.append(
        "\n---\n## Preguntas que esta evidencia debe responder (rellena a mano)\n\n"
        "1. ¿La respuesta del LLM sale por stdout o solo con `--output`? ¿Hay texto extra (logs, barras de progreso) mezclado?\n"
        "2. ¿Los logs van a stderr y el resultado a stdout?\n"
        "3. ¿Qué códigos de salida usa en éxito y en error?\n"
        "4. ¿La salida del LLM es incremental (streaming real)? Mira las marcas de tiempo.\n"
        "5. ¿Aplica plantilla de chat? ¿Cómo se pasa un historial de mensajes?\n"
        "6. ¿Cómo se sabe que `serve` está listo? ¿Cuánto tarda?\n"
        "7. ¿Qué pasa con peticiones concurrentes y con pedir otro modelo con el demonio activo?\n"
        "8. ¿Existe API de Python importable?\n"
    )
    rep.write(out / REPORT_NAME)
    print(f"\nListo. Informe: {out / REPORT_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
