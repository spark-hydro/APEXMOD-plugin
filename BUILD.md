# Building and testing the plugin

The plugin is Python only, so there is nothing to compile. A release is a ZIP with the
plugin folder (`src/apexmod`, installed as `APEXMOD/`) and the AMRS programs (`amrs` for
Linux and `amrs.exe` for Windows, both downloaded from the [AMRS](https://github.com/spark-hydro/AMRS)
release and not stored in git; only the old Intel debug build `amrs_deb24-002.exe` in
`apexmf_exes` is). The plugin still finds the old Intel `amrs_rel24-002.exe` that projects made
with version 1.5 contain.

## Build the ZIP

```bash
AMRS_PLATFORM=all scripts/fetch_amrs.sh   # amrs (Linux) and amrs.exe (Windows) from the
                                       # AMRS release in amrs-version.txt (default: Linux only)
python3 scripts/package.py --xml       # dist/APEXMOD.<version>.zip + plugins.xml  (both programs)
python3 scripts/package.py --linux --xml   # dist/APEXMOD.<version>-linux.zip + plugins-linux.xml (Linux program only)
python3 scripts/package.py --check dist/APEXMOD.1.6.0.zip   # layout check only
```

- The version comes from `src/apexmod/metadata.txt`. The ZIP has one top-level folder,
  `APEXMOD/`, with `metadata.txt` directly inside.
- **File name:** `APEXMOD.<version>[-linux].zip`. QGIS takes the plugin id from the file
  name up to the first dot, so `APEXMOD-1.6.0.zip` would be read as the plugin
  `APEXMOD-2` and updates would not be recognised.
- The ZIP is reproducible (fixed time stamps): the same files give the same checksum.
- QGIS "Install from ZIP" does not keep file permissions; the plugin sets the execute bit
  of `amrs` itself when it starts the model.
- `plugins.xml` points to `https://github.com/spark-hydro/APEXMOD-plugin/releases/download/v<version>/<zip>`;
  `--base-url` and `--tag` change that (for a mirror or a test).

## Install a local build

Windows: `.\install.ps1 -Zip dist\APEXMOD.1.6.0.zip` (`-PluginsDir DIR` for another folder, `-Uninstall`).
Linux:

```bash
./install.sh --zip dist/APEXMOD.1.6.0-linux.zip                 # default QGIS profile
./install.sh --zip dist/APEXMOD.1.6.0-linux.zip --plugins-dir /tmp/plugins
./install.sh --uninstall
```

`install.sh` refuses to replace a symbolic link (a development install, e.g.
`ln -s $PWD/src/apexmod ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/APEXMOD`)
unless you pass `--force`.

## Releases and CI

- `.github/workflows/build.yml` (push to `main`, pull requests): unit tests on Linux and Windows;
  the ZIPs and `install.sh`; on Windows `install.ps1` (Windows PowerShell 5.1 and PowerShell 7) and the
  installed `amrs.exe --version`; and QGIS 3.44 (`qgis/qgis` image): installs the Linux ZIP with
  `install.sh`, loads the plugin, imports every module and, on the Animas example data
  (`Inputs/apexmod_data.zip`), creates a project, a 1000 m MODFLOW model, runs the linking step and
  the Run button code with the Linux AMRS program (`scripts/ci_qgis_check.py`, about a minute).
  **No model is run on Windows**, and the numbers of the example model are not compared with
  anything: the AMRS repository has the regression test for the program itself.
- `.github/workflows/release.yml`: push a tag equal to `v` + `version=` in `metadata.txt`
  (`git tag v1.6.0 && git push origin v1.6.0`) to build both ZIPs, `plugins.xml`,
  `plugins-linux.xml` and `SHA256SUMS` and attach them, with `install.sh` and `install.ps1`, to a
  GitHub Release. Manual runs and pull requests that touch the packaging build and upload workflow
  artifacts only.
- Both programs come from the AMRS release named in `amrs-version.txt`
  (`scripts/fetch_amrs.sh`); change the file to ship another version.
- Run the QGIS check locally in the same image:
  `docker run --rm -v $PWD:/work -v /path/to/unpacked/apexmod_data:/data:ro qgis/qgis:3.44 bash -c '...'`
  (install pandas, run `install.sh --zip dist/APEXMOD.<version>-linux.zip --plugins-dir /tmp/plugins`, then
  `QT_QPA_PLATFORM=offscreen python3 /work/scripts/ci_qgis_check.py --plugins-dir /tmp/plugins --data /data`).

## Tests

No QGIS needed (Python 3 only):

```bash
python3 src/apexmod/test/test_sysutil.py
python3 src/apexmod/test/test_package.py
```

Loading the plugin needs QGIS 3 (see the README for a conda environment):

```bash
conda activate qgis-ltr
ln -s $PWD/src/apexmod ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/APEXMOD
qgis
```
