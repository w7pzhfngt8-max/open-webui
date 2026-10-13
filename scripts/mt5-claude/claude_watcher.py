"""Send MetaTrader 5 chart screenshots straight to Claude for analysis.

Watches the MT5 screenshot folder(s). Every new PNG/JPG is sent to Claude and
the analysis is saved next to the image as <name>.analysis.md and opened.

Usage:
    pip install anthropic
    set ANTHROPIC_API_KEY=sk-ant-...
    python claude_watcher.py                 # auto-finds MQL5\\Files\\ClaudeShots
    python claude_watcher.py D:\\Shots ...   # also/instead watch other folders
"""

import base64
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
POLL_SECONDS = 1.0
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

SYSTEM_PROMPT = """You are an experienced technical analyst reviewing a MetaTrader 5 chart screenshot.
Describe only what is visible on the chart; if something cannot be read, say so rather than guessing.
Structure your answer as:
1. Market structure & trend (on the shown timeframe)
2. Key support / resistance levels (with approximate prices read from the axis)
3. Indicators visible on the chart and what they show
4. Notable patterns or signals
5. Possible scenarios (bullish and bearish), with invalidation levels
6. Risk notes
Keep it concise. This is educational analysis, not financial advice."""

# Optional: put your own instructions in prompt.txt next to this script.
PROMPT_FILE = Path(__file__).with_name("prompt.txt")


def default_watch_dirs() -> list[Path]:
    """Find <Data Folder>\\MQL5\\Files\\ClaudeShots for every MT5 terminal."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return []
    pattern = os.path.join(appdata, "MetaQuotes", "Terminal", "*", "MQL5", "Files")
    dirs = []
    for files_dir in glob.glob(pattern):
        shots = Path(files_dir) / "ClaudeShots"
        shots.mkdir(exist_ok=True)
        dirs.append(shots)
    return dirs


def chart_context(image: Path) -> str:
    """Filenames from ClaudeChartShot.mq5 look like EURUSD__H1__20261013_101500.png."""
    parts = image.stem.split("__")
    if len(parts) >= 3:
        return f"Symbol: {parts[0]}\nTimeframe: {parts[1]}\n"
    return ""


def wait_until_written(path: Path, timeout: float = 10.0) -> None:
    """MT5 may still be writing the file; wait until its size stops changing."""
    last = -1
    deadline = time.time() + timeout
    while time.time() < deadline:
        size = path.stat().st_size
        if size == last and size > 0:
            return
        last = size
        time.sleep(0.3)


def analyze(client: anthropic.Anthropic, image: Path) -> str:
    data = base64.standard_b64encode(image.read_bytes()).decode("utf-8")
    instructions = (
        PROMPT_FILE.read_text(encoding="utf-8")
        if PROMPT_FILE.exists()
        else "Analyse this chart."
    )

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        output_config={"effort": "high"},
        # If a safety classifier declines, retry on a fallback model automatically.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": IMAGE_TYPES[image.suffix.lower()],
                            "data": data,
                        },
                    },
                    {"type": "text", "text": chart_context(image) + instructions},
                ],
            }
        ],
    )

    if response.stop_reason == "refusal":
        return "Claude declined to analyse this image."
    return "\n".join(b.text for b in response.content if b.type == "text")


def open_file(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # opens in the default .md / text viewer
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def scan(dirs: list[Path]) -> set[Path]:
    return {
        p for d in dirs for p in d.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_TYPES
    }


def main() -> None:
    dirs = [Path(a) for a in sys.argv[1:]] or default_watch_dirs()
    if not dirs:
        sys.exit("No MT5 folder found. Pass the screenshot folder as an argument.")
    for d in dirs:
        if not d.is_dir():
            sys.exit(f"Folder does not exist: {d}")
        print(f"Watching {d}")

    client = anthropic.Anthropic()
    seen = scan(dirs)  # ignore screenshots that were already there
    print(f"Ready - new screenshots go to {MODEL}. Ctrl+C to stop.")

    while True:
        time.sleep(POLL_SECONDS)
        for image in sorted(scan(dirs) - seen):
            seen.add(image)
            print(f"\n>> Analysing {image.name} ...")
            try:
                wait_until_written(image)
                text = analyze(client, image)
            except anthropic.AuthenticationError:
                sys.exit("Invalid API key - set ANTHROPIC_API_KEY.")
            except (anthropic.APIError, OSError) as e:
                print(f"   failed: {e}")
                continue
            out = image.with_suffix(".analysis.md")
            out.write_text(f"# {image.name}\n\n{text}\n", encoding="utf-8")
            print(text)
            print(f"   saved {out}")
            open_file(out)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
