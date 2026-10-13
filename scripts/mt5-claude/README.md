# MT5 → Claude chart analysis

Press a hotkey in MetaTrader 5. A screenshot of the chart goes to Claude, and the
analysis opens on your screen a few seconds later.

## Files

| File | Purpose |
|---|---|
| `ClaudeChartShot.mq5` | MT5 script that saves the current chart to `MQL5\Files\ClaudeShots\` |
| `claude_watcher.py` | Watches that folder and sends each new screenshot to Claude |
| `start_claude_watcher.bat` | Double-click launcher for Windows |
| `prompt.txt` (optional) | Your own instructions, e.g. "Focus on London session liquidity" |

## Setup (Windows, one time)

1. **Python & API key.** Install Python 3.10+ from python.org (tick *Add to PATH*), then
   get a key at <https://console.anthropic.com> and run in a Command Prompt:
   ```
   setx ANTHROPIC_API_KEY sk-ant-your-key
   ```
2. **MT5 script.** In MT5: *File → Open Data Folder* → `MQL5\Scripts`, and copy
   `ClaudeChartShot.mq5` there. Open it in MetaEditor (F4) and press *Compile* (F7).
3. **Hotkey.** In MT5's Navigator (Ctrl+N) → *Scripts*, right-click
   `ClaudeChartShot` → *Set hotkey* → choose e.g. `Ctrl+Shift+A`.
4. **Start the watcher.** Double-click `start_claude_watcher.bat`. To have it start
   with Windows, press Win+R, type `shell:startup`, and put a shortcut to the `.bat` there.

## Use

Focus a chart and press your hotkey. The analysis appears in the watcher window
and opens as `<screenshot>.analysis.md` next to the image.

Already saving screenshots another way (e.g. right-click chart → *Save as Picture*)?
Point the watcher at that folder too:

```
start_claude_watcher.bat "C:\Users\me\Pictures\MT5"
```

## Options

- `CLAUDE_MODEL` env var — model to use (default `claude-opus-5-5`; e.g.
  `claude-sonnet-5-5` is cheaper).
- `prompt.txt` — replaces the default "Analyse this chart." instruction.

Claude's output is educational chart analysis, not financial advice.
