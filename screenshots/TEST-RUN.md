# Test run on device

Device: `redroid15_x86_64`, Android 15 (API 35), 720x1280 @ 320dpi, connected over adb at `127.0.0.1:9085`.

Every screenshot below was pulled straight off that device with `adb exec-out screencap -p` while the app was running. Input was driven with `adb shell input tap` / `input text` — real touch events into the real app, not a preview or a mock.

App data was cleared with `pm clear com.talmale.todo` before the run, so this starts from a genuinely fresh install.

| # | Screenshot | Step | What it proves |
|---|---|---|---|
| 1 | `01-empty.png` | Fresh launch | Empty state renders. **Add** is disabled while the field is blank. |
| 2 | `02-typing.png` | Typed "Buy milk" | Input accepts text; **Add** becomes enabled. |
| 3 | `03-one-task.png` | Tapped **Add** | **ADD WORKS** — task appears, field clears, header reads `1 of 1 remaining`. |
| 4 | `04-three-tasks.png` | Added two more | Three rows, header reads `3 of 3 remaining`. |
| 5 | `05-completed.png` | Tapped checkbox on "Buy milk" | **COMPLETE WORKS** — box ticked, strikethrough applied, header drops to `2 of 3 remaining`. |
| 6 | `06-deleted.png` | Tapped **Delete** on "Call the dentist" | **DELETE WORKS** — row removed, header reads `1 of 2 remaining`, other rows untouched. |
| 7 | `07-after-restart.png` | `am force-stop` then relaunch | State survived a full process kill — "Buy milk" still ticked, "Call the dentist" still gone. |
| 8 | `08-unchecked.png` | Tapped the ticked checkbox again | Complete toggles both ways; header back to `2 of 2 remaining`. |
| 9 | `09-empty-again.png` | Deleted both remaining | Deleting the last task returns cleanly to the empty state. |

## Crash check

`logcat` was cleared before the restart step and inspected afterwards. No `FATAL EXCEPTION`, no `AndroidRuntime` errors, no ANRs — only normal ActivityManager lifecycle logging.

## Commands used

```bash
adb -s 127.0.0.1:9085 install -r app/build/outputs/apk/debug/app-debug.apk
adb -s 127.0.0.1:9085 shell pm clear com.talmale.todo
adb -s 127.0.0.1:9085 shell am start -n com.talmale.todo/.MainActivity
adb -s 127.0.0.1:9085 shell input tap 277 271          # focus field
adb -s 127.0.0.1:9085 shell input text "Buy%smilk"
adb -s 127.0.0.1:9085 shell input tap 613 263          # Add
adb -s 127.0.0.1:9085 shell input tap 88 403           # checkbox
adb -s 127.0.0.1:9085 shell input tap 605 523          # Delete
adb -s 127.0.0.1:9085 exec-out screencap -p > shot.png
```
