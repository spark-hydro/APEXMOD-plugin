"""Tests for pyfolder/sysutil.py (no QGIS needed): run with `python3 test/test_sysutil.py`."""
import importlib.util
import os
import stat
import tempfile
import unittest
from unittest import mock

_path = os.path.join(os.path.dirname(__file__), "..", "pyfolder", "sysutil.py")
_spec = importlib.util.spec_from_file_location("sysutil", _path)
sysutil = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sysutil)


class OpenFileTest(unittest.TestCase):
    def test_linux_uses_xdg_open(self):
        with mock.patch.object(sysutil.sys, "platform", "linux"), \
                mock.patch.object(sysutil.subprocess, "Popen") as popen:
            sysutil.open_file("/tmp/a/../out.gif")
        popen.assert_called_once_with(["xdg-open", os.path.normpath("/tmp/out.gif")])

    def test_macos_uses_open(self):
        with mock.patch.object(sysutil.sys, "platform", "darwin"), \
                mock.patch.object(sysutil.subprocess, "Popen") as popen:
            sysutil.open_file("/tmp/out.mp4")
        popen.assert_called_once_with(["open", os.path.normpath("/tmp/out.mp4")])

    def test_windows_uses_startfile(self):
        with mock.patch.object(sysutil.sys, "platform", "win32"), \
                mock.patch.object(sysutil.os, "startfile", create=True) as sf:
            sysutil.open_file("C:/x/out.gif")
        sf.assert_called_once_with(os.path.normpath("C:/x/out.gif"))


class EnsureExecutableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    @unittest.skipIf(os.name == "nt", "no execute bit on Windows")
    def test_ensure_executable(self):
        open(os.path.join(self.dir, "amrs"), "w").close()
        path = os.path.join(self.dir, "amrs")
        os.chmod(path, 0o644)
        sysutil.ensure_executable(path)
        self.assertTrue(os.stat(path).st_mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
