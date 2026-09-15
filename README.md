# Simple To-Do (Android, Kotlin)

A single-screen to-do list. Add a task, edit it, tick it off, delete it. No login, no accounts, no network.

<p align="center">
  <img src="screenshots/02-three-tasks.png" width="240" alt="Task list">
  <img src="screenshots/04-edit-open.png" width="240" alt="Editing a task inline">
  <img src="screenshots/03-completed.png" width="240" alt="Completed task">
</p>

## What it does

- **Add** — type in the field, tap **Add** (or hit Done on the keyboard). Blank input is ignored and the Add button stays disabled until you type something.
- **Edit** — **tap a task's text** to rename it. The row turns into an inline text field, pre-filled and focused with the caret at the end, with **Save** and **Cancel** beside it (Done on the keyboard saves too). Blank titles are rejected, and renaming never changes whether a task is completed or where it sits in the list.
- **Complete** — tap the checkbox. The task greys out with a strikethrough; tap again to un-complete.
- **Delete** — tap **Delete** on the row. Gone immediately.
- The header shows a live count (`2 of 3 remaining`).
- Tasks survive closing and reopening the app — they're saved to `SharedPreferences` as JSON.

## Stack

| | |
|---|---|
| Language | Kotlin 2.3.20 |
| UI | Jetpack Compose + Material 3 |
| Architecture | `AndroidViewModel` + `StateFlow`, single `Activity` |
| minSdk / targetSdk / compileSdk | 24 / 35 / 36 |
| Build | Gradle 9.7.1, AGP 9.0.1, JDK 17 target |

No Room, no Hilt, no networking — the whole app is four small files.

## Project layout

```
app/src/main/java/com/talmale/todo/
├── MainActivity.kt      # the single screen: Compose UI, incl. the inline task editor
├── TodoViewModel.kt     # add / rename / toggle / delete, exposes StateFlow<List<Task>>
└── TodoRepository.kt    # Task model + SharedPreferences JSON persistence

tools/                   # adb-driven on-device test run (see screenshots/TEST-RUN.md)
├── ui.py                # find a node in the live UI dump, tap it, screenshot
├── run_test.py          # the 49 checks: add / edit / complete / delete / persistence
└── demo.py              # the same flow at human pace, for screen recording
```

## Install the APK

Grab `app-debug.apk` from the [Releases](../../releases) page (or build it yourself, below), copy it to your phone and open it. Android will ask you to allow installs from unknown sources — that's expected for any APK not coming from the Play Store.

Or over USB with adb:

```bash
adb install -r app-debug.apk
```

It's signed with the standard Android debug key, which is fine for sideloading. For Play Store distribution you'd sign a release build with your own keystore.

## Build from source

Requires a **JDK** (not just a JRE) and the Android SDK with platform 36.

```bash
git clone https://github.com/anirudhatalmale8-eng/simple-todo-android.git
cd simple-todo-android
echo "sdk.dir=/path/to/your/android-sdk" > local.properties
./gradlew assembleDebug
```

Output lands at `app/build/outputs/apk/debug/app-debug.apk`.

## Tested on

Android 15 (API 35), 720x1280 @ 320dpi. Every screenshot in `screenshots/` was captured from that running device via `adb exec-out screencap`.

The full run is **49 automated checks** against the real app on that device — add, edit (save, cancel, blank guard, keyboard Done, editing a completed task, switching rows mid-edit), complete, delete, and persistence across a `force-stop`. Each check reads the live accessibility tree, so a pass means the app really is in that state. See [`screenshots/TEST-RUN.md`](screenshots/TEST-RUN.md) for the step-by-step run, or [`screenshots/edit-task-demo.mp4`](screenshots/edit-task-demo.mp4) to watch it.

```bash
ANDROID_SERIAL=<your-device> python3 tools/run_test.py
```
