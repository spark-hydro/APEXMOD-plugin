"""Small helpers that behave the same on Windows, Linux and macOS."""
import os
import re
import subprocess
import sys


def open_file(path):
    """Open a file with the default application of the operating system.

    Replaces os.startfile, which exists on Windows only.
    """
    path = os.path.normpath(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: pylint
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _natural_key(name):
    # v0.1.10 sorts after v0.1.9
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def find_amrs_exe(folder, platform=None):
    """Return the AMRS (APEX-MODFLOW-RT3D-Salt) executable in `folder`, or None.

    Windows: `amrs.exe`, else the newest `amrs-*.exe` build (the AMRS release),
    else the old amrs_rel24-002.exe / apexmf1.1_64rel.exe of projects made with plugin 1.5.
    Linux/macOS: `amrs`, else the newest `amrs-*` build, e.g. the file name
    inside the AMRS release zip (amrs-v0.1.0-gnu-lin_x86_64-Rel).
    """
    platform = platform or sys.platform
    releases = lambda ok: sorted(
        (n for n in os.listdir(folder) if n.startswith("amrs-") and ok(n)),
        key=_natural_key, reverse=True)
    if platform.startswith("win"):
        names = ["amrs.exe"] + releases(lambda n: n.endswith(".exe"))
        names += ["amrs_rel24-002.exe", "apexmf1.1_64rel.exe"]
    else:
        names = ["amrs"] + releases(lambda n: not n.endswith((".zip", ".exe", ".txt", ".log")))
    for name in names:
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            return os.path.normpath(path)
    return None


def ensure_executable(path):
    """Set the execute bit (a zip or a copy can lose it). Does nothing on Windows."""
    if not sys.platform.startswith("win"):
        mode = os.stat(path).st_mode
        os.chmod(path, mode | 0o111)
