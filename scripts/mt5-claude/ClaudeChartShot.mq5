//+------------------------------------------------------------------+
//| ClaudeChartShot.mq5                                              |
//| Saves a screenshot of the current chart into                     |
//| <Data Folder>\MQL5\Files\ClaudeShots\ where claude_watcher.py    |
//| picks it up and sends it to Claude for analysis.                 |
//|                                                                  |
//| Install: copy to <Data Folder>\MQL5\Scripts\, compile in         |
//| MetaEditor, then in Navigator right-click the script ->          |
//| "Set hotkey" (e.g. Ctrl+Shift+A).                                |
//+------------------------------------------------------------------+
#property copyright "MT5 -> Claude chart analysis"
#property version   "1.00"
#property script_show_inputs false

input int ShotWidth  = 1920;   // Screenshot width in pixels
input int ShotHeight = 1080;   // Screenshot height in pixels

void OnStart()
  {
   string symbol = _Symbol;
   string tf     = StringSubstr(EnumToString((ENUM_TIMEFRAMES)_Period), 7); // "PERIOD_H1" -> "H1"

   MqlDateTime t;
   TimeToStruct(TimeLocal(), t);
   string stamp = StringFormat("%04d%02d%02d_%02d%02d%02d",
                               t.year, t.mon, t.day, t.hour, t.min, t.sec);

   // Format parsed by claude_watcher.py: SYMBOL__TIMEFRAME__TIMESTAMP.png
   string file = "ClaudeShots\\" + symbol + "__" + tf + "__" + stamp + ".png";

   ChartRedraw();
   if(!ChartScreenShot(0, file, ShotWidth, ShotHeight, ALIGN_RIGHT))
     {
      Print("ClaudeChartShot: screenshot failed, error ", GetLastError());
      return;
     }
   Print("ClaudeChartShot: saved ", file, " - sent to Claude for analysis");
  }
//+------------------------------------------------------------------+
