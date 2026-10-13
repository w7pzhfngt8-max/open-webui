@echo off
rem Double-click (or put a shortcut to this file in shell:startup) to start
rem sending MT5 screenshots to Claude. Set your key once with:
rem     setx ANTHROPIC_API_KEY sk-ant-...
title MT5 -> Claude
cd /d "%~dp0"
python -m pip install --quiet --upgrade anthropic
python claude_watcher.py %*
pause
