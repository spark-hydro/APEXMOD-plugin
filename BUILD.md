# Building and testing the plugin

The plugin is Python only, so there is nothing to compile. A release is a ZIP with the
plugin folder (`src/apexmod`, installed as `APEXMOD/`) and the AMRS programs (`amrs` for
Linux and `amrs.exe` for Windows, both downloaded from the [AMRS](https://github.com/spark-hydro/AMRS)
release and not stored in git; the older Intel builds `amrs_rel24-002.exe` and `amrs_deb24-002.exe`
in `FOLDER_FOR_COPY` are).

## Build the ZIP

```bash
AMRS_PLATFORM=all scripts/fetch_amrs.sh   # amrs (Linux) and amrs.exe (Windows) from the
                                       # AMRS release in amrs-version.txt (default: Linux only)
python3 scripts/package.py --xml       # dist/APEXMOD.<version>.zip + plugins.xml  (both programs)
python3 scripts/package.py --linux --xml   # dist/APEXMOD.<version>-linux.zip + plugins-linux.xml (Linux program only)
python3 scripts/package.py --check dist/APEXMOD.1.5.3.zip   # layout check only
```

- The version comes from `src/apexmod/metadata.txt`. The ZIP has one top-level folder,
  `APEXMOD/`, with `metadata.txt` directly inside.
- **File name:** `APEXMOD.<version>[-linux].zip`. QGIS takes the plugin id from the file
  name up to the first dot, so `APEXMOD-1.5.3.zip` would be read as the plugin
  `APEXMOD-2` and updates would not be recognised.
- The ZIP is reproducible (fixed time stamps): the same files give the same checksum.
- QGIS "Install from ZIP" does not keep file permissions; the plugin sets the execute bit
  of `amrs` itself when it starts the model.
- `plugins.xml` points to `https://github.com/spark-hydro/APEXMOD-plugin/releases/download/v<version>/<zip>`;
  `--base-url` and `--tag` change that (for a mirror or a test).

## Install a local build

Windows: `.\install.ps1 -Zip dist\APEXMOD.1.5.3.zip` (`-PluginsDir DIR` for another folder, `-Uninstall`).
Linux:

```bash
./install.sh --zip dist/APEXMOD.1.5.3-linux.zip                 # default QGIS profile
./install.sh --zip dist/APEXMOD.1.5.3-linux.zip --plugins-dir /tmp/plugins
./install.sh --uninstall
```

`install.sh` refuses to replace a symbolic link (a development install, e.g.
`ln -s $PWD/src/apexmod ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/APEXMOD`)
unless you pass `--force`.

## Releases and CI

GitHub Actions workflows (tests on Linux and Windows, a QGIS 3.44 check, and the release build
from a tag) are added in the next step; this section will describe them then.

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
