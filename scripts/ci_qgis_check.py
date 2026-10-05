#!/usr/bin/env python3
"""Check an installed APEXMOD plugin inside QGIS, without a display.

    QT_QPA_PLATFORM=offscreen python3 scripts/ci_qgis_check.py \\
        --plugins-dir DIR [--data DIR] [--no-run]

--plugins-dir  folder that holds APEXMOD/ (for example after install.sh --plugins-dir DIR)
--data         the unpacked Inputs/apexmod_data.zip (animas_apex_model/ and animas_shps/): runs the
               steps a user does, with the plugin's own methods and the file dialogs mocked:
               new project, APEX model, sub and river shapefiles, MODFLOW model (1000 m grid,
               river cells, input files), linking step, apexmf_link.txt, and the Run button code
               (run_apexmf_model) with the AMRS program from the plugin
--no-run       do everything except running the model

Exits with 1 if a step fails. Used by .github/workflows/build.yml in the qgis/qgis image.
"""
import argparse
import importlib
import os
import sys
import tempfile
import time
import traceback
from unittest import mock

# modules of the bundled FloPy that import names the bundled FloPy does not have;
# the plugin does not use them
KNOWN_BROKEN = {
    "APEXMOD.modules.flopy.utils.compare",
    "APEXMOD.modules.flopy.utils.gridgen",
    "APEXMOD.modules.flopy.utils.mfgrdfile",
    "APEXMOD.modules.flopy.utils.triangle",
}
SKIP_DIRS = {"__pycache__", "test", "FOLDER_FOR_COPY", "help", "templates", "pics", "i18n", ".git",
             ".qt_for_python", "scripts"}
# plugin_upload.py is a Plugin Builder template; temp.py and temp03.py are old scratch files
SKIP_FILES = {"plugin_upload.py", "temp.py", "temp03.py"}

failures = []
msgs = []   # texts of the message boxes the plugin opened


def step(name):
    def wrap(fn):
        def run(*args, **kwargs):
            t0 = time.time()
            try:
                result = fn(*args, **kwargs)
                print("ok    {} ({:.0f} s)".format(name, time.time() - t0), flush=True)
                return result
            except Exception:  # noqa: BLE001 - report every kind of failure
                failures.append(name)
                print("FAIL  ", name, flush=True)
                traceback.print_exc()
                return None
        return run
    return wrap


@step("load the plugin and run initGui()")
def load(plugins_dir):
    from qgis.testing.mocked import get_iface
    sys.path.insert(0, plugins_dir)
    import APEXMOD
    plugin = APEXMOD.classFactory(get_iface())
    plugin.initGui()
    return plugin


@step("import every module of the plugin")
def import_all(plugins_dir):
    base = os.path.join(plugins_dir, "APEXMOD")
    bad, count = [], 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if not name.endswith(".py") or name in SKIP_FILES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), plugins_dir)[:-3].replace(os.sep, ".")
            rel = rel[:-len(".__init__")] if rel.endswith(".__init__") else rel
            count += 1
            try:
                importlib.import_module(rel)
            except BaseException as err:  # noqa: BLE001
                if rel not in KNOWN_BROKEN:
                    bad.append("{}: {}: {}".format(rel, type(err).__name__, err))
    print("      {} modules, {} unexpected failures".format(count, len(bad)))
    assert not bad, "\n".join(bad)


@step("new project, APEX model, sub and river shapefiles")
def project(plugin, data):
    from qgis.core import QgsProject
    from qgis.PyQt.QtWidgets import QFileDialog
    from APEXMOD.pyfolder import db_functions
    proj_dir = tempfile.mkdtemp()
    QgsProject.instance().setFileName(os.path.join(proj_dir, "animas.qgz"))
    plugin.dlg.lineEdit_Project_Name.setText("animas")
    plugin.copyProjectfolder()
    db_functions.DB_CreateConnection(plugin)
    plugin.DB_Update_Project()
    root = QgsProject.instance().layerTreeRoot()
    for group in ("APEX", "MODFLOW", "APEX-MODFLOW"):
        root.insertGroup(0, group)
    paths = plugin.dirs_and_paths()
    for key, path in paths.items():
        assert os.path.isdir(path), "project folder missing: " + key
    with mock.patch.object(QFileDialog, "getExistingDirectory",
                           return_value=os.path.join(data, "animas_apex_model")):
        plugin.load_apex_model()
    assert os.path.isfile(os.path.join(paths["apexmf_model"], "APEXCONT.DAT"))
    with mock.patch.object(QFileDialog, "getOpenFileNames",
                           return_value=([os.path.join(data, "animas_shps", "sub_org.shp")], "")):
        plugin.load_sub()
    with mock.patch.object(QFileDialog, "getOpenFileNames",
                           return_value=([os.path.join(data, "animas_shps", "riv_org.shp")], "")):
        plugin.load_riv()
    names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
    assert "sub (APEX)" in names and "riv (APEX)" in names, names


@step("MODFLOW model: DEM, boundary, 1000 m grid, river cells, input files")
def modflow(plugin, data):
    from qgis.core import QgsProject
    from qgis.PyQt.QtWidgets import QFileDialog
    from APEXMOD.dialogs import createMFmodel_dialog
    dm = createMFmodel_dialog.createMFmodelDialog(plugin.iface)
    with mock.patch.object(QFileDialog, "getOpenFileName",
                           return_value=(os.path.join(data, "animas_shps", "DEM.tif"), "")):
        dm.loadDEM()
    dm.checkBox_use_sub.setChecked(True)     # boundary = dissolved sub shapefile
    dm.doubleSpinBox_delr.setValue(1000.0)
    dm.doubleSpinBox_delc.setValue(1000.0)
    dm.create_MF_shps()
    grid = QgsProject.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    act = QgsProject.instance().mapLayersByName("mf_act_grid (MODFLOW)")[0]
    assert grid.featureCount() == 9956, grid.featureCount()
    assert 3000 < act.featureCount() < 5000, act.featureCount()
    for radio, edit, value in (("radioButton_aq_thic_single", "lineEdit_aq_thic_single", "50"),
                               ("radioButton_hk_single", "lineEdit_hk_single", "5"),
                               ("radioButton_ss_single", "lineEdit_ss_single", "1e-5"),
                               ("radioButton_sy_single", "lineEdit_sy_single", "0.15"),
                               ("radioButton_initialH_single", "lineEdit_initialH_single", "5")):
        getattr(dm, radio).setChecked(True)
        getattr(dm, edit).setText(value)
    dm.groupBox_evt.setChecked(False)
    mf_dir = plugin.dirs_and_paths()["MODFLOW"]
    dm.lineEdit_createMFfolder.setText(mf_dir)
    dm.lineEdit_mname.setText("mf_1000")
    dm.create_mf_riv()
    dm.writeMF()
    for ext in ("bas", "dis", "nam", "nwt", "oc", "rch", "riv", "upw"):
        out = os.path.join(mf_dir, "mf_1000." + ext)
        assert os.path.getsize(out) > 0, out


@step("checkMF, linking step, apexmf_link.txt")
def link(plugin):
    mf_dir = plugin.dirs_and_paths()["MODFLOW"]
    plugin.checkMF()
    assert os.path.getsize(os.path.join(mf_dir, "modflow.mfn")) > 0
    plugin.geoprocessing_prepared()
    for name in ("link_grid_sa", "link_sa_grid", "link_river_grid"):
        out = os.path.join(mf_dir, name)
        assert os.path.getsize(out) > 0, out
    assert "Linking process has been completed successfully!" in msgs, msgs[-3:]
    plugin.create_apexmf_link()
    with open(os.path.join(mf_dir, "apexmf_link.txt")) as f:
        text = f.read()
    assert "Groundwater delay" in text and "flag for running RT3D" in text


@step("Run button code (run_apexmf_model) runs AMRS from the plugin")
def run_model(plugin, plugins_dir):
    import shutil
    paths = plugin.dirs_and_paths()
    exe = os.path.join(plugins_dir, "APEXMOD", "FOLDER_FOR_COPY", "APEX-MODFLOW", "amrs")
    assert os.path.isfile(exe), "the plugin has no Linux program: " + exe
    # the program as installed from the ZIP: no execute bit
    target = os.path.join(paths["apexmf_model"], "amrs")
    shutil.copyfile(exe, target)
    os.chmod(target, 0o644)
    plugin.run_apexmf_model()
    log = os.path.join(paths["apexmf_model"], "amrs_run.log")
    deadline = time.time() + 900
    text = ""
    while time.time() < deadline:
        time.sleep(1)
        if os.path.exists(log):
            with open(log) as f:
                text = f.read()
            if "Normal termination of simulation" in text:
                break
    assert "Normal termination of simulation" in text, "model did not finish:\n" + text[-1500:]
    for name in ("amf_MF_recharge.out", "amf_apex_channel.out", "amf_MF_gwsw.out"):
        out = os.path.join(paths["MODFLOW"], name)
        assert os.path.exists(out) and os.path.getsize(out) > 0, "no " + name


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plugins-dir", required=True)
    ap.add_argument("--data")
    ap.add_argument("--no-run", action="store_true")
    args = ap.parse_args()
    plugins_dir = os.path.abspath(args.plugins_dir)

    from qgis.testing import start_app
    start_app()
    from qgis.core import Qgis, QgsApplication
    # the QGIS GUI puts its own plugins (processing) on the path and registers the algorithm
    # providers; a script has to do it
    sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
    import processing  # noqa: F401 - the plugin imports it
    from processing.core.Processing import Processing
    Processing.initialize()
    from qgis.analysis import QgsNativeAlgorithms
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    from qgis.PyQt.QtWidgets import QMessageBox
    QMessageBox.exec_ = lambda self: msgs.append(self.text()) or 0   # no dialog can wait for a click
    print("QGIS", Qgis.QGIS_VERSION, "| Python", sys.version.split()[0], flush=True)

    plugin = load(plugins_dir)
    import_all(plugins_dir)
    if plugin is not None and args.data:
        data = os.path.abspath(args.data)
        project(plugin, data)
        if "new project, APEX model, sub and river shapefiles" not in failures:
            modflow(plugin, data)
        if "MODFLOW model: DEM, boundary, 1000 m grid, river cells, input files" not in failures:
            link(plugin)
        if not args.no_run and "checkMF, linking step, apexmf_link.txt" not in failures:
            run_model(plugin, plugins_dir)
    print("\n{} failed step(s){}".format(len(failures), ": " + ", ".join(failures) if failures else ""))
    sys.stdout.flush()
    os._exit(1 if failures else 0)  # QGIS can hang on exit in a container


if __name__ == "__main__":
    main()
