#!/usr/bin/env python3
"""Drives the app at human pace for the screen recording."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui import *  # noqa


def beat(n=1.6):
    time.sleep(n)


def add(text):
    tap_node("New task", "text")
    type_text(text)
    tap_node("Add", "text")
    beat()


def open_editor(title):
    dismiss_ime()
    tap_node(f"Edit {title}", "desc", label=f"tap '{title}'")
    time.sleep(2.0)


shell(f"am force-stop {PKG}")
shell(f"pm clear {PKG}")
shell(f"am start -n {PKG}/.MainActivity")
time.sleep(3.0)
beat(2.0)

# --- add ---
for t in ["Buy milk", "Call the dentist", "Book flights"]:
    add(t)
dismiss_ime()
beat(2.0)

# --- complete ---
tap_node("Toggle Buy milk", "desc", label="tick 'Buy milk'")
beat(2.5)

# --- edit + save ---
open_editor("Call the dentist")
beat(1.2)
clear_field()
type_text("Call the dentist at 4pm")
beat(2.0)
tap_node("Save edit", "desc", label="Save")
dismiss_ime()
beat(3.0)

# --- edit + cancel ---
open_editor("Book flights")
beat(1.2)
clear_field()
type_text("THROW THIS AWAY")
beat(2.0)
tap_node("Cancel edit", "desc", label="Cancel")
dismiss_ime()
beat(3.0)

# --- edit a completed task, appending at the caret ---
open_editor("Buy milk")
beat(1.2)
type_text(" 2L")
beat(1.5)
tap_node("Save edit", "desc", label="Save")
dismiss_ime()
beat(3.0)

# --- delete ---
tap_node("Delete Book flights", "desc", label="Delete 'Book flights'")
beat(3.0)

# --- restart: persistence ---
shell(f"am force-stop {PKG}")
beat(2.5)
shell(f"am start -n {PKG}/.MainActivity")
time.sleep(3.0)
beat(4.0)
print("demo done:", state())
