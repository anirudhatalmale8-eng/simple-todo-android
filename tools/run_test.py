#!/usr/bin/env python3
"""Full on-device regression + edit-feature run for Simple To-Do.

Every check below reads the live accessibility tree off the device, so a pass means
the real app really is in that state - not that a screenshot merely looks right.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui import *  # noqa

log, failures = [], []


def check(desc, ok, detail=""):
    (log if ok else failures).append(f"{'PASS' if ok else 'FAIL'}: {desc} {detail}".strip())
    print(f"  {'PASS' if ok else '>>> FAIL'}: {desc} {detail}")
    if not ok:
        failures.append(desc)


def step(n, desc, checks):
    # The soft keyboard shrinks the list, which drops off-screen rows out of the
    # accessibility tree. Hide it first so every snapshot sees the whole list.
    dismiss_ime()
    s = state()
    screenshot(n)
    print(f"\n[{n}] {desc}\n    subtitle={s['subtitle']!r}\n    tasks={s['tasks']}\n    checked={s['checked']}")
    checks(s)
    log.append({"step": n, "desc": desc, **s})


def launch(clear=False):
    if clear:
        shell(f"pm clear {PKG}")
    shell(f"am start -n {PKG}/.MainActivity")
    time.sleep(2.5)


def add(text):
    tap_node("New task", "text", label="input")
    type_text(text)
    tap_node("Add", "text", label="Add")


def open_editor(title):
    dismiss_ime()  # so the whole list is reachable before we tap a row
    tap_node(f"Edit {title}", "desc", label=f"task text {title!r}")
    time.sleep(1.8)


shell(f"am force-stop {PKG}")
adb("logcat", "-c")

# ---------------------------------------------------------------- baseline: add
launch(clear=True)
step("01-empty", "Fresh launch, no tasks", lambda s: (
    check("empty state, no tasks", s["tasks"] == []),
    check("subtitle reads 'Nothing to do yet'", s["subtitle"] == "Nothing to do yet"),
))

for t in ["Buy milk", "Call the dentist", "Book flights"]:
    add(t)
step("02-three-tasks", "ADD still works", lambda s: (
    check("all three tasks present in order",
          s["tasks"] == ["Buy milk", "Call the dentist", "Book flights"], str(s["tasks"])),
    check("subtitle counts them", s["subtitle"] == "3 of 3 remaining", s["subtitle"]),
))

# ---------------------------------------------------------------- baseline: complete
tap_node("Toggle Buy milk", "desc", label="checkbox 'Buy milk'")
step("03-completed", "COMPLETE still works", lambda s: (
    check("'Buy milk' is ticked", s["checked"].get("Buy milk") is True),
    check("others untouched", s["checked"].get("Call the dentist") is False
                              and s["checked"].get("Book flights") is False),
    check("subtitle drops to 2 of 3", s["subtitle"] == "2 of 3 remaining", s["subtitle"]),
))

# ---------------------------------------------------------------- edit: save
open_editor("Call the dentist")
step("04-edit-open", "EDIT opens on tap, pre-filled", lambda s: (
    check("edited row left the read-only list while editing",
          "Call the dentist" not in s["tasks"], str(s["tasks"])),
    check("Save button on screen", find("Save edit", "desc") is not None),
    check("Cancel button on screen", find("Cancel edit", "desc") is not None),
    check("other rows still readable", "Buy milk" in s["tasks"] and "Book flights" in s["tasks"]),
))

clear_field()
type_text("Call the dentist at 4pm")
step("05-edit-typed", "EDIT accepts new text", lambda s: (
    check("field holds the new text",
          find("Call the dentist at 4pm", "text") is not None),
))

tap_node("Save edit", "desc", label="Save")
time.sleep(1.0)
step("06-edit-saved", "EDIT SAVES", lambda s: (
    check("row now reads the new text", "Call the dentist at 4pm" in s["tasks"], str(s["tasks"])),
    check("old text is gone", "Call the dentist" not in s["tasks"]),
    check("position in the list preserved", s["tasks"].index("Call the dentist at 4pm") == 1,
          str(s["tasks"])),
    check("editor closed", find("Save edit", "desc") is None),
    check("done-count unchanged by a rename", s["subtitle"] == "2 of 3 remaining", s["subtitle"]),
    check("renamed row keeps its unticked state",
          s["checked"].get("Call the dentist at 4pm") is False),
))

# ---------------------------------------------------------------- edit: cancel
open_editor("Book flights")
clear_field()
type_text("THROW THIS AWAY")
step("07-edit-cancel-typed", "EDIT: a change we are about to discard", lambda s: (
    check("field holds the throwaway text", find("THROW THIS AWAY", "text") is not None),
))

tap_node("Cancel edit", "desc", label="Cancel")
time.sleep(1.0)
step("08-edit-cancelled", "EDIT CANCELS cleanly", lambda s: (
    check("row still reads 'Book flights'", "Book flights" in s["tasks"], str(s["tasks"])),
    check("throwaway text was discarded", "THROW THIS AWAY" not in s["tasks"]),
    check("editor closed", find("Cancel edit", "desc") is None),
    check("list otherwise unchanged",
          s["tasks"] == ["Buy milk", "Call the dentist at 4pm", "Book flights"], str(s["tasks"])),
))

# ---------------------------------------------------------------- edit a completed task
open_editor("Buy milk")
type_text(" 2L")  # caret should already be at the end of the existing title
tap_node("Save edit", "desc", label="Save")
time.sleep(1.0)
step("09-edit-done-task", "EDIT on a completed task keeps the tick", lambda s: (
    check("text changed", "Buy milk 2L" in s["tasks"], str(s["tasks"])),
    check("still ticked", s["checked"].get("Buy milk 2L") is True),
    check("count still 2 of 3", s["subtitle"] == "2 of 3 remaining", s["subtitle"]),
))

# ---------------------------------------------------------------- blank guard
# Behavioural, not cosmetic: empty the field, actually press Save, and prove nothing moved.
open_editor("Book flights")
clear_field()
time.sleep(0.5)
tap_node("Save edit", "desc", label="Save (should do nothing)")
time.sleep(1.0)
step("10-blank-guard", "EDIT refuses to save a blank title", lambda s: (
    check("pressing Save on an empty field did not close the editor",
          find("Save edit", "desc") is not None),
    check("no blank/renamed row appeared",
          s["tasks"] == ["Buy milk 2L", "Call the dentist at 4pm"], str(s["tasks"])),
    check("subtitle unchanged", s["subtitle"] == "2 of 3 remaining", s["subtitle"]),
))
tap_node("Cancel edit", "desc", label="Cancel")
time.sleep(1.0)
step("10b-blank-cancelled", "and the original title comes back untouched", lambda s: (
    check("'Book flights' intact",
          s["tasks"] == ["Buy milk 2L", "Call the dentist at 4pm", "Book flights"], str(s["tasks"])),
))

# ---------------------------------------------------------------- delete
dismiss_ime()
tap_node("Delete Book flights", "desc", label="Delete 'Book flights'")
step("11-deleted", "DELETE still works", lambda s: (
    check("'Book flights' removed", "Book flights" not in s["tasks"], str(s["tasks"])),
    check("other rows untouched",
          s["tasks"] == ["Buy milk 2L", "Call the dentist at 4pm"], str(s["tasks"])),
    check("subtitle recounts", s["subtitle"] == "1 of 2 remaining", s["subtitle"]),
))

# ---------------------------------------------------------------- restart persistence
shell(f"am force-stop {PKG}")
time.sleep(2.0)
launch()
step("12-after-restart", "PERSISTENCE across a full process kill", lambda s: (
    check("edited titles survived",
          s["tasks"] == ["Buy milk 2L", "Call the dentist at 4pm"], str(s["tasks"])),
    check("completed state survived", s["checked"].get("Buy milk 2L") is True),
    check("deleted task stayed deleted", "Book flights" not in s["tasks"]),
    check("subtitle restored", s["subtitle"] == "1 of 2 remaining", s["subtitle"]),
))

# ---------------------------------------------------------------- un-complete + clear out
tap_node("Toggle Buy milk 2L", "desc", label="untick 'Buy milk 2L'")
step("13-unchecked", "COMPLETE toggles back off", lambda s: (
    check("unticked", s["checked"].get("Buy milk 2L") is False),
    check("subtitle back to 2 of 2", s["subtitle"] == "2 of 2 remaining", s["subtitle"]),
))

tap_node("Delete Buy milk 2L", "desc", label="Delete")
tap_node("Delete Call the dentist at 4pm", "desc", label="Delete")
step("14-empty-again", "DELETE back to empty", lambda s: (
    check("no tasks left", s["tasks"] == [], str(s["tasks"])),
    check("empty state returns", s["subtitle"] == "Nothing to do yet", s["subtitle"]),
))

# ---------------------------------------------------------------- keyboard Done saves
add("Water plants")
add("Pay rent")
open_editor("Water plants")
clear_field()
type_text("Water the plants")
shell("input keyevent 66")  # ENTER = the keyboard's Done action on a single-line field
time.sleep(1.2)
step("15-ime-done-saves", "EDIT saves from the keyboard's Done key too", lambda s: (
    check("renamed via Done", "Water the plants" in s["tasks"], str(s["tasks"])),
    check("editor closed", find("Save edit", "desc") is None),
))

# ---------------------------------------------------------------- switching rows mid-edit
open_editor("Water the plants")
clear_field()
type_text("UNSAVED EDIT")
dismiss_ime()
tap_node("Edit Pay rent", "desc", label="tap the other task while editing")
time.sleep(1.8)
step("16-switch-rows", "Tapping another task moves the editor and drops the unsaved change",
     lambda s: (
         check("only one editor open at a time",
               len([n for n in nodes() if n.get("content-desc") == "Save edit"]) == 1),
         check("first row reverted to its saved title",
               "Water the plants" in s["tasks"], str(s["tasks"])),
         check("unsaved text was not committed", "UNSAVED EDIT" not in s["tasks"]),
     ))
tap_node("Cancel edit", "desc", label="Cancel")
time.sleep(1.0)
step("17-final", "Back to a clean list", lambda s: (
    check("both tasks intact with saved titles",
          s["tasks"] == ["Water the plants", "Pay rent"], str(s["tasks"])),
))

# ---------------------------------------------------------------- crash check
crash = adb("logcat", "-d", "-b", "crash").stdout.decode("utf-8", "replace")
main = adb("logcat", "-d").stdout.decode("utf-8", "replace")
bad = [l for l in main.splitlines()
       if ("FATAL EXCEPTION" in l or "ANR in" in l) and PKG in main]
print("\n[crash check]")
check("no crash-buffer output", crash.strip() == "", crash.strip()[:200])
check("no FATAL EXCEPTION / ANR in logcat", not bad, str(bad[:3]))

json.dump(log, open(os.path.join(SHOTS, "run_log.json"), "w"), indent=2)
print(f"\n{'='*50}\n{'ALL CHECKS PASSED' if not failures else 'FAILURES: ' + str(failures)}\n{'='*50}")
sys.exit(1 if failures else 0)
