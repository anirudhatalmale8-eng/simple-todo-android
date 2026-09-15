# Test run on device

Device: `redroid15_x86_64`, Android 15 (API 35), 720x1280 @ 320dpi, connected over adb at `127.0.0.1:9085`.

This run covers the new **edit a task** feature and re-runs everything that already worked
(add, complete, delete, restart persistence) to show none of it regressed.

Everything here was driven by [`tools/run_test.py`](../tools/run_test.py) against the real app on
that device — real touch events, real keyboard, real process kills. **49 checks, all passing.**

The important part: each check reads the live accessibility tree off the device and asserts on it.
A pass means the app really is in that state, not that a screenshot happens to look right. The
screenshots are there so you can see it too.

App data was cleared with `pm clear com.talmale.todo` before the run, so it starts from a
genuinely fresh install.

## Watch it

[`edit-task-demo.mp4`](edit-task-demo.mp4) — a ~2 minute screen recording of the same flow at
human pace: adding, completing, tapping a task to edit it and saving, editing and cancelling,
appending to a completed task, deleting, and a force-stop + relaunch at the end.

## The run

| # | Screenshot | Step | What it proves |
|---|---|---|---|
| 1 | `01-empty.png` | Fresh launch | Empty state renders, **Add** disabled while blank. |
| 2 | `02-three-tasks.png` | Added three tasks | **ADD STILL WORKS** — all three in order, header `3 of 3 remaining`. |
| 3 | `03-completed.png` | Ticked "Buy milk" | **COMPLETE STILL WORKS** — strikethrough, header `2 of 3 remaining`, other rows untouched. |
| 4 | `04-edit-open.png` | Tapped the text "Call the dentist" | **EDIT OPENS ON TAP** — inline editor, pre-filled, Save + Cancel on screen. Other rows stay readable. |
| 5 | `05-edit-typed.png` | Typed a new title | Field accepts the new text. |
| 6 | `06-edit-saved.png` | Tapped **Save** | **EDIT SAVES** — row reads "Call the dentist at 4pm", keeps its position, keeps its unticked state, editor closes, count unchanged. |
| 7 | `07-edit-cancel-typed.png` | Typed a throwaway change on "Book flights" | Editor holds the pending text. |
| 8 | `08-edit-cancelled.png` | Tapped **Cancel** | **EDIT CANCELS** — change discarded, row still reads "Book flights", rest of the list identical. |
| 9 | `09-edit-done-task.png` | Edited a *completed* task, appending " 2L" | Renaming a done task keeps its tick and strikethrough; the caret starts at the end of the title so appending just works. |
| 10 | `10-blank-guard.png` | Emptied the field and pressed **Save** | **BLANK GUARD** — Save is disabled, pressing it does nothing, editor stays open, no blank row is created. |
| 10b | `10b-blank-cancelled.png` | Cancelled out of that | Original title comes back untouched. |
| 11 | `11-deleted.png` | Deleted "Book flights" | **DELETE STILL WORKS** — row gone, others untouched, header `1 of 2 remaining`. |
| 12 | `12-after-restart.png` | `am force-stop` then relaunch | **PERSISTENCE STILL WORKS** — edited titles, the tick and the deletion all survived a full process kill. |
| 13 | `13-unchecked.png` | Un-ticked "Buy milk 2L" | Complete still toggles both ways; header back to `2 of 2 remaining`. |
| 14 | `14-empty-again.png` | Deleted the rest | Deleting the last task returns cleanly to the empty state. |
| 15 | `15-ime-done-saves.png` | Renamed, then hit **Done** on the keyboard | Edit also commits from the keyboard's Done key, not just the Save button. |
| 16 | `16-switch-rows.png` | Tapped a second task while already editing one | Only ever one editor open; the first row reverts to its saved title and the unsaved text is dropped. |
| 17 | `17-final.png` | Cancelled out | List left clean with both saved titles intact. |

## What the edit feature does

- **Tap the task text** to edit it. The checkbox and **Delete** are unaffected — tapping those
  still completes and deletes as before.
- The editor opens **inline in the same card**, pre-filled, focused, with the caret at the end of
  the existing title and the keyboard already up.
- **Save** commits the rename. **Cancel** discards it. The keyboard's **Done** key also saves.
- Blank titles are rejected — Save is disabled, mirroring how the **Add** button already behaves.
- Renaming never touches a task's completed state, its position in the list, or the header count.
- Only one row is editable at a time; tapping another task moves the editor there.

## Two things that got fixed during this work

Both found by running it on the device rather than by reading the code:

1. **Save / Cancel were landing behind the soft keyboard.** Stacking them under the text field
   made the editor card taller than what's left of a 360x640dp screen once the keyboard is up, so
   they got clipped. They now sit on one row beside the field (~72dp total), the list is
   `imePadding`-ed, and the open editor asks to be scrolled into view. Verified on the
   bottom-most row of a full list, the worst case.
2. **The caret opened at position 0**, so tapping a task to append to it typed at the front.
   It now opens at the end of the existing title.

## Crash check

`logcat` was cleared at the start of the run and both the main and crash buffers were inspected
at the end. No `FATAL EXCEPTION`, no `AndroidRuntime` errors, no ANRs.

## Reproduce it yourself

With a device on adb and the debug APK installed:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
ANDROID_SERIAL=<your-device> python3 tools/run_test.py     # the 49 checks + screenshots
ANDROID_SERIAL=<your-device> python3 tools/demo.py         # the flow at human pace, for recording
```

`tools/run_test.py` exits non-zero if any check fails and writes `screenshots/run_log.json`
with the observed state at every step.
