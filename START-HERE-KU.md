# دروستکردنی بەرنامەی Windows

## داگرتنی بەرنامەی ئامادە

[پاکێجی Windows دابگرە](https://github.com/hamaatahir2005/shexai/actions/runs/39982153041/artifacts/12514112774) (نزیکەی ٢٦٦ MB). لە GitHub چوونەژوورەوە پێویستە.

ZIP ـەکە دەربهێنە، پاشان لە فۆڵدەری `installer` فایلەکەی `SheikhHamamomin-Setup.exe` بکەرەوە. بۆ دامەزراندنی ئەم پاکێجە Python پێویست نییە.

build و پشکنینی `.exe` سەرکەوتوو بوون و ٢٤ تاقیکردنەوە تێپەڕین. بۆ چاتی AI هێشتا پێویستە API یان Ollama ڕێک بخەیت. دەنگی کوردی هێشتا بە نموونەی ڕاستەقینە پشکنراو نییە.

بەشەکانی خوارەوە بۆ دروستکردنەوەی بەرنامەکەن لە کۆدی سەرچاوە.

## لەسەر کۆمپیوتەرەکەت

١. Python 3.12 ـی 64-bit دابمەزرێنە لە python.org. Python Launcher (`py`) ـیش هەڵبژێرە.
٢. پاکێجی ZIP دەربهێنە بۆ فۆڵدەرێک.
٣. دوو کلیک لە `BUILD-WINDOWS.cmd` بکە و `Y` هەڵبژێرە.
٤. چاوەڕێی داگرتنی پێداویستییەکان و تاقیکردنەوە و build بکە. ئینتەرنێت و بۆشایی دیسک پێویستە.
٥. ئەگەر سەرکەوتوو بوو، `dist/SheikhHamamomin-Windows-x64.zip` دروست دەبێت.
٦. هەموو ناوەڕۆکی ئەو ZIP ـە دەربهێنە، پاشان `SheikhHamamomin.exe` بکەرەوە. فایلەکانی دەوروبەری مەسڕەوە؛ تەنها `.exe` مەگوازەوە.

کۆمپیوتەری دووەم بۆ بەکارهێنانی بەرنامەی build کراو پێویستی بە Python نییە. بۆ AI پێویستت بە API یان Ollama هەیە. بۆ دەنگ پێویستت بە مۆدێل/خزمەتگوزاری و مایکرۆفۆن هەیە؛ کوالێتی دەنگی کوردی هێشتا پشکنراو نییە.

## Installer

Inno Setup 6 دابمەزرێنە، پاشان لە PowerShell لە فۆڵدەری پڕۆژەکە:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -Installer
```

ئەنجامی چاوەڕوانکراو: `dist/installer/SheikhHamamomin-Setup.exe`، لەگەڵ shortcut ـی Start Menu.

## بەبێ build لەسەر کۆمپیوتەرەکەت

کۆدەکە بخەرە repository ـی خۆت لە GitHub. لە Actions، workflow ـی **Build Windows application** بە Run workflow دەست پێ بکە. ئەگەر build سەرکەوتوو بوو، artifact ـی **SheikhHamamomin-Windows-x64** دابگرە؛ ZIP ـی بەرنامە و installer ـی تێدایە. پێویست ناکات کلیلەکانی API بخەیتە repository یان workflow.

workflow ـەکە لە ٢٠٢٦/١٠/٢٣ بە سەرکەوتوویی ڕاگیرا و فایلەکانی بەرنامەکە لە لینکی سەرەوە ئامادەن.
