#!/usr/bin/env python3
"""Tiny adb driver: find a node by text/content-desc in the live UI dump and tap its centre."""
import os, re, subprocess, sys, time, xml.etree.ElementTree as ET

SERIAL = os.environ.get("ANDROID_SERIAL", "127.0.0.1:9085")
SHOTS = os.environ.get(
    "SHOTS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
)
PKG = "com.talmale.todo"


def adb(*args, **kw):
    return subprocess.run(["adb", "-s", SERIAL, *args], capture_output=True, **kw)


def shell(cmd):
    return adb("shell", cmd).stdout.decode("utf-8", "replace")


def dump():
    for _ in range(6):
        out = adb("exec-out", "uiautomator dump /dev/tty").stdout.decode("utf-8", "replace")
        start = out.find("<?xml")
        if start != -1 and "<hierarchy" in out:
            xml = out[start:]
            xml = xml[: xml.rfind("</hierarchy>") + len("</hierarchy>")]
            try:
                return ET.fromstring(xml)
            except ET.ParseError:
                pass
        time.sleep(0.7)
    raise RuntimeError("could not dump UI")


def nodes():
    return list(dump().iter("node"))


def find(match, attr="both"):
    """match: substring. attr: 'text' | 'desc' | 'both'."""
    for n in nodes():
        t, d = n.get("text", ""), n.get("content-desc", "")
        hay = {"text": [t], "desc": [d], "both": [t, d]}[attr]
        if any(match in (h or "") for h in hay):
            return n
    return None


def centre(node):
    x1, y1, x2, y2 = map(int, re.findall(r"-?\d+", node.get("bounds")))
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap_node(match, attr="both", label=None):
    n = find(match, attr)
    if n is None:
        raise RuntimeError(f"node not found: {match!r} ({attr})")
    x, y = centre(n)
    shell(f"input tap {x} {y}")
    print(f"tap {label or match} @ {x},{y}")
    time.sleep(1.0)


def type_text(s):
    shell("input text " + s.replace(" ", "%s"))
    time.sleep(0.8)


def ime_shown():
    out = shell("dumpsys input_method | grep -E 'mInputShown|mVisibleBound'")
    return "mInputShown=true" in out


def dismiss_ime():
    """Hide the soft keyboard so the whole list is on screen and in the a11y tree.

    Does not clear focus, so typing into the focused field still works afterwards.
    """
    if ime_shown():
        shell("input keyevent 4")
        time.sleep(1.0)


def clear_field():
    """Select-all then delete — avoids IME autocorrect weirdness from repeated backspaces."""
    shell("input keycombination 113 29")  # CTRL_LEFT + A
    time.sleep(0.4)
    shell("input keyevent 67")  # DEL
    time.sleep(0.5)


def screenshot(name):
    out = subprocess.run(["adb", "-s", SERIAL, "exec-out", "screencap", "-p"], capture_output=True)
    os.makedirs(SHOTS, exist_ok=True)
    path = os.path.join(SHOTS, f"{name}.png")
    open(path, "wb").write(out.stdout)
    print(f"  saved {name}.png")
    return path


def subtitle():
    for n in nodes():
        t = n.get("text", "")
        if "remaining" in t or "done" in t or "Nothing to do" in t:
            return t
    return "(no subtitle)"


def titles():
    """Task titles = nodes whose content-desc is 'Edit <title>'."""
    return [n.get("content-desc")[5:] for n in nodes() if n.get("content-desc", "").startswith("Edit ")]


def checked():
    return {n.get("content-desc")[7:]: n.get("checked") == "true"
            for n in nodes() if n.get("content-desc", "").startswith("Toggle ")}


def state():
    return {"subtitle": subtitle(), "tasks": titles(), "checked": checked()}
